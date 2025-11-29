# Duplicate Module Titles Investigation Report

## Problem Summary
User's learning path shows multiple modules with identical titles:
- "Learn the basics" appears at least 3 times
- "Learn the Basics" (different capitalization)

## Root Cause Analysis

### THE BUG: No Module-Level De-duplication

**Location:** `backend/core/apps/learning_content/api/views.py`, lines 788-862

**What Happens:**
1. Phase 3's `select_optimal_modules()` correctly selects N unique roadmap nodes
2. BUT: Each node is then independently converted to a module using `node.title` (line 852)
3. **No validation** checks if module titles are unique before adding to `modules_data`
4. Result: If roadmap.sh data has duplicate node titles, they ALL appear in the final path

### The Flow (With Line Numbers)

```python
# Step 1: Select optimal modules from roadmap (lines 778-783)
selected_modules = roadmap_service.select_optimal_modules(
    filtered_roadmap,
    user_preferences_dict,
    user_profile,
    dynamic_module_count  # e.g., 10 modules requested
)

# Step 2: Convert each node to a module (lines 788-862)
for idx, node in enumerate(selected_modules, 1):
    # ...search for courses...
    
    # Create module with roadmap node data (lines 849-862)
    module = {
        'module_id': f"module-{idx}",
        'title': node.title,  # ← DIRECTLY uses node.title without validation
        'description': node.description,
        'order': idx,
        # ...
    }
    modules_data.append(module)  # ← No duplicate check!
```

**The Problem:**
- `node.title` is taken directly from roadmap.sh JSON without validation
- No check for duplicate titles before adding to `modules_data`
- Different nodes can have identical titles (e.g., "Learn the Basics")

### Why This Happens

#### Issue #1: Roadmap.sh Data Quality
**File:** `backend/ml_services/integrations/roadmap_service.py`, lines 187-259

Roadmap.sh JSON structure has nodes like:
```json
{
  "nodes": [
    {"id": "1", "data": {"label": "Learn the Basics"}},
    {"id": "2", "data": {"label": "Learn the basics"}},  // Different ID, same title
    {"id": "3", "data": {"label": "Learn the Basics"}}   // Different ID, same title again
  ]
}
```

The parser (lines 204-209) extracts titles AS-IS:
```python
title = (
    node_data.get('title') or
    data_obj.get('label') or  # ← Takes raw label from roadmap.sh
    node_data.get('label') or
    ''
)
```

**No normalization** of titles happens here.

#### Issue #2: Phase 3 Merging Only De-duplicates Across Goals
**File:** `backend/ml_services/integrations/roadmap_service.py`, lines 418-514

The `_merge_roadmaps()` function DOES de-duplicate (lines 453-476):
```python
# Check for duplicates using similarity matching
for seen_title, existing_node in seen_titles.items():
    similarity = SequenceMatcher(None, title_lower, seen_title).ratio()
    
    if similarity >= 0.7:  # 70% similarity threshold
        # Merge duplicate nodes
        existing_node.skills = list(set(existing_node.skills + node.skills))
        is_duplicate = True
        break
```

**BUT:**
- This only runs when merging MULTIPLE goals (e.g., ["web_dev", "ai_ml"])
- For SINGLE goal paths, `get_merged_roadmap_for_goals()` returns the roadmap AS-IS (lines 391-393):
  ```python
  if len(learning_goals) == 1:
      return self.get_roadmap_for_preferences(user_preferences)  # ← No de-duplication!
  ```

#### Issue #3: No Title Validation During Module Creation
**File:** `backend/core/apps/learning_content/api/views.py`, lines 849-862

When creating modules, there's NO check like:
```python
# MISSING CODE - should be here:
if any(m['title'].lower() == node.title.lower() for m in modules_data):
    logger.warning(f"Skipping duplicate module title: {node.title}")
    continue
```

## Specific Problem Areas

### 1. Single-Goal Paths Get No De-duplication
**Line:** `roadmap_service.py:391-393`

```python
if len(learning_goals) == 1:
    return self.get_roadmap_for_preferences(user_preferences)
```

**Impact:** Users with one goal (most common case) get raw roadmap.sh data with all duplicates.

### 2. Module Priority Scoring Doesn't Check Titles
**Line:** `roadmap_service.py:562-722` (select_optimal_modules)

The scoring system ranks nodes by:
- Skill gap relevance
- Goal alignment
- Career fit
- Difficulty progression
- Prerequisites

**BUT:** Never checks if `node.title` is unique. Could select 3 nodes all called "Learn the Basics" if they score high.

### 3. No Fallback Title Normalization
**Line:** `roadmap_service.py:204-209`

```python
title = (
    node_data.get('title') or
    data_obj.get('label') or
    node_data.get('label') or
    ''
)
```

**Missing:** Title normalization like:
- Strip whitespace
- Normalize capitalization
- Add context from category/description if title is generic

## Evidence in Code

### Proof #1: De-duplication Only in Multi-Goal Merging
`roadmap_service.py:453-476`
```python
# This ONLY runs during _merge_roadmaps() (multi-goal)
for seen_title, existing_node in seen_titles.items():
    similarity = SequenceMatcher(None, title_lower, seen_title).ratio()
    if similarity >= 0.7:
        # Duplicate found - merge
```

### Proof #2: Single Goal Bypasses Merging
`roadmap_service.py:367-416`
```python
def get_merged_roadmap_for_goals(...):
    if len(learning_goals) == 1:
        return self.get_roadmap_for_preferences(user_preferences)  # ← Direct return
```

### Proof #3: No Module Title Validation
`views.py:849-862`
```python
module = {
    'module_id': f"module-{idx}",
    'title': node.title,  # ← No validation
    # ...
}
modules_data.append(module)  # ← No duplicate check
```

## Why Users See This Bug

**Scenario:**
1. User selects ONE learning goal: "web_dev"
2. Fetches roadmap from roadmap.sh: "frontend.json"
3. Roadmap has 50 nodes, including:
   - Node #1: id="html-basics", title="Learn the Basics"
   - Node #15: id="css-basics", title="Learn the basics"  (lowercase)
   - Node #23: id="js-basics", title="Learn the Basics"
4. Priority scoring selects all 3 (they cover different skills)
5. Module creation adds all 3 with identical displayed titles
6. Frontend shows: "Learn the Basics" (3 times)

## Is This a Data Issue or Code Bug?

**Both:**

### Data Issue (roadmap.sh)
- roadmap.sh JSON has generic, repetitive node titles
- No enforcement of unique titles per roadmap
- Example: "Learn the basics", "Getting Started", "Introduction" appear multiple times

### Code Bug (Gradvy)
- **Missing de-duplication for single-goal paths**
- **No title validation during module creation**
- **No title normalization/enrichment**

## Where De-duplication Should Happen

### Option 1: During Roadmap Parsing (BEST)
**File:** `roadmap_service.py:144-277` (_parse_roadmap)

Add title normalization:
```python
# After extracting title (line 209)
title = title.strip()
title_lower = title.lower()

# Check for duplicate titles
if title_lower in seen_titles_in_roadmap:
    # Enrich with category/description
    title = f"{title} ({category})"
```

### Option 2: During Module Selection
**File:** `roadmap_service.py:562-722` (select_optimal_modules)

Add de-duplication:
```python
# After scoring (line 705)
seen_titles = set()
unique_selected = []
for score, idx, node, breakdown in scored_modules[:target_count]:
    title_lower = node.title.lower()
    if title_lower not in seen_titles:
        unique_selected.append(node)
        seen_titles.add(title_lower)
```

### Option 3: During Module Creation (SAFEGUARD)
**File:** `views.py:788-862`

Add validation:
```python
# Before appending (line 862)
title_lower = node.title.lower()
if any(m['title'].lower() == title_lower for m in modules_data):
    # Skip or enrich title
    continue
modules_data.append(module)
```

## Recommended Fix

**Multi-Layered Approach:**

1. **Apply de-duplication to single-goal paths** (roadmap_service.py)
   - Modify `get_merged_roadmap_for_goals()` to ALWAYS de-duplicate
   - Even for single goals, run title similarity check

2. **Add title validation in `select_optimal_modules()`** (roadmap_service.py)
   - After scoring, filter out duplicate titles
   - Keep highest-scored instance of each title

3. **Add safeguard in module creation** (views.py)
   - Before appending module, check if title exists
   - Enrich duplicate titles with context (e.g., "Learn the Basics (HTML)")

4. **Optional: Enrich generic titles during parsing** (roadmap_service.py)
   - If title is too generic ("Learn the Basics"), append category
   - Example: "Learn the Basics" → "Learn the Basics: HTML Fundamentals"

## Specific Line Numbers for Fixes

### Fix #1: De-duplicate Single-Goal Paths
**File:** `backend/ml_services/integrations/roadmap_service.py`
**Lines:** 391-393

```python
# CURRENT CODE:
if len(learning_goals) == 1:
    return self.get_roadmap_for_preferences(user_preferences)

# SHOULD BE:
if len(learning_goals) == 1:
    roadmap = self.get_roadmap_for_preferences(user_preferences)
    # Apply de-duplication even for single goal
    roadmap = self._deduplicate_roadmap_nodes(roadmap)
    return roadmap
```

### Fix #2: Add Title De-duplication to Module Selection
**File:** `backend/ml_services/integrations/roadmap_service.py`
**Lines:** 707-710 (after scoring, before returning)

```python
# CURRENT CODE:
selected_nodes = [node for score, idx, node, breakdown in selected_scored]

# SHOULD BE:
seen_titles = {}
selected_nodes = []
for score, idx, node, breakdown in selected_scored:
    title_lower = node.title.lower().strip()
    if title_lower not in seen_titles:
        selected_nodes.append(node)
        seen_titles[title_lower] = node
    else:
        logger.debug(f"Skipping duplicate title: '{node.title}' (already selected)")
```

### Fix #3: Add Module Title Validation
**File:** `backend/core/apps/learning_content/api/views.py`
**Lines:** 849-862 (before appending module)

```python
# CURRENT CODE:
module = {
    'module_id': f"module-{idx}",
    'title': node.title,
    # ...
}
modules_data.append(module)

# SHOULD BE:
module_title = node.title.strip()
# Check for duplicate titles
if any(m['title'].lower() == module_title.lower() for m in modules_data):
    logger.warning(f"⚠️ Duplicate module title detected: '{module_title}', enriching with context")
    module_title = f"{module_title} ({node.category})"

module = {
    'module_id': f"module-{idx}",
    'title': module_title,  # Use validated title
    # ...
}
modules_data.append(module)
```

## Summary

**Root Cause:**
- Phase 3's de-duplication ONLY runs for multi-goal paths
- Single-goal paths (most common) bypass de-duplication entirely
- No validation during module creation
- Roadmap.sh has generic, repetitive node titles

**Impact:**
- Users see "Learn the Basics" multiple times
- Poor UX - looks like a bug
- Wastes space in learning path

**Fix Priority:**
1. **HIGH:** Add de-duplication to `select_optimal_modules()` (line 707)
2. **MEDIUM:** Apply de-duplication to single-goal paths (line 391)
3. **LOW:** Add title enrichment during module creation (line 849)

**Estimated Fix Time:** 30-60 minutes

## Next Steps

1. Verify this analysis by checking user's actual learning path data
2. Implement Fix #2 (title de-duplication in module selection) - simplest, most effective
3. Test with single-goal and multi-goal paths
4. Consider adding title enrichment for very generic titles ("Learn the Basics" → "Learn the Basics: HTML")
