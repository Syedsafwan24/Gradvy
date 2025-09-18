# MongoDB Schema Update Plan

## Background

The current issue is that the MongoDB collection schema validation only allows 7 interaction types:
- `course_click`
- `quiz_attempt`
- `video_watch`
- `search`
- `page_view`
- `course_enroll`
- `course_complete`

However, the Python application code defines 13 interaction types, including:
- `onboarding_started`
- `onboarding_flow_completed`
- `social_profile_update`
- `privacy_settings_change`
- `preference_manual_save`
- `preference_auto_save`

This mismatch causes MongoDB validation errors when the application tries to log interactions.

## Current Temporary Fix

We've implemented temporary filtering in the Python code to skip unsupported interaction types:

```python
# TEMPORARY FIX in core/apps/preferences/models.py
mongodb_allowed_types = [
    'course_click', 'quiz_attempt', 'video_watch', 'search', 'page_view',
    'course_enroll', 'course_complete'
]
if interaction_type not in mongodb_allowed_types:
    logger.warning(f"Skipping interaction type '{interaction_type}' due to MongoDB schema validation.")
    return
```

## Required Schema Update

### 1. Current MongoDB Schema

Location: Collection validation in MongoDB
Current enum constraint for `behavioral_patterns.interaction_history.type`:

```json
{
  "type": {
    "enum": [
      "course_click",
      "quiz_attempt",
      "video_watch",
      "search",
      "page_view",
      "course_enroll",
      "course_complete"
    ]
  }
}
```

### 2. Required Schema Update

The enum should be updated to include all interaction types defined in the Python code:

```json
{
  "type": {
    "enum": [
      "course_click",
      "quiz_attempt",
      "video_watch",
      "search",
      "page_view",
      "course_enroll",
      "course_complete",
      "onboarding_started",
      "onboarding_flow_completed",
      "social_profile_update",
      "privacy_settings_change",
      "preference_manual_save",
      "preference_auto_save"
    ]
  }
}
```

## Implementation Steps

### Step 1: Database Administration Access

**Requirements:**
- MongoDB admin credentials or admin access to the Gradvy database
- Permission to modify collection schema validation rules
- Access to production/staging MongoDB instance

**Commands needed:**
```bash
# Connect to MongoDB with admin privileges
mongosh "mongodb://localhost:27017/gradvy_preferences" --username admin --password <admin_password>

# Or for MongoDB Atlas/Cloud
mongosh "mongodb+srv://cluster.mongodb.net/gradvy_preferences" --username admin --password <admin_password>
```

### Step 2: Backup Current Collection

**Before making any schema changes:**

```javascript
// Create backup collection
db.userpreference.aggregate([{ $out: "userpreference_backup_" + new Date().toISOString() }])

// Verify backup
db.userpreference_backup_<timestamp>.countDocuments()
```

### Step 3: Update Collection Validation Schema

```javascript
// Get current validation rules
db.runCommand({ "collMod": "userpreference", "validator": {} })

// Update validation schema to include new interaction types
db.runCommand({
  "collMod": "userpreference",
  "validator": {
    "$jsonSchema": {
      "bsonType": "object",
      "properties": {
        "behavioral_patterns": {
          "bsonType": "object",
          "properties": {
            "interaction_history": {
              "bsonType": "array",
              "items": {
                "bsonType": "object",
                "properties": {
                  "type": {
                    "enum": [
                      "course_click",
                      "quiz_attempt",
                      "video_watch",
                      "search",
                      "page_view",
                      "course_enroll",
                      "course_complete",
                      "onboarding_started",
                      "onboarding_flow_completed",
                      "social_profile_update",
                      "privacy_settings_change",
                      "preference_manual_save",
                      "preference_auto_save"
                    ]
                  }
                }
              }
            }
          }
        }
      }
    }
  }
})
```

### Step 4: Validate Schema Update

```javascript
// Test validation with new interaction type
db.userpreference.insertOne({
  "user_id": 999999,
  "behavioral_patterns": {
    "interaction_history": [{
      "type": "onboarding_started",
      "data": {"page": "test"},
      "metadata": {"source": "test"}
    }]
  }
})

// Should succeed if schema update worked
// Clean up test document
db.userpreference.deleteOne({"user_id": 999999})
```

### Step 5: Remove Temporary Filtering Code

Once schema is updated, remove the temporary filtering in Python:

```python
# Remove this block from core/apps/preferences/models.py
# TEMPORARY FIX: Filter interaction types to match MongoDB schema validation
mongodb_allowed_types = [
    'course_click', 'quiz_attempt', 'video_watch', 'search', 'page_view',
    'course_enroll', 'course_complete'
]
if interaction_type not in mongodb_allowed_types:
    logger.warning(f"Skipping interaction type '{interaction_type}' due to MongoDB schema validation.")
    return
```

### Step 6: Test Full Workflow

1. Test all interaction types can be logged successfully
2. Test onboarding flow with interaction logging
3. Test manual save workflow without filtering
4. Verify no MongoDB validation errors occur

## Risk Assessment

### Low Risk
- Schema validation updates are non-destructive
- Existing data remains unchanged
- Can be reverted if issues occur

### Medium Risk
- Requires admin database access
- Should be tested in staging environment first
- Need coordination with production deployment

### Mitigation Strategies
1. **Staging Testing**: Test schema update in staging environment first
2. **Backup**: Complete backup before schema modification
3. **Rollback Plan**: Document exact steps to revert schema changes
4. **Monitoring**: Monitor application logs after deployment for any issues

## Alternative Approaches

### Option 1: Update Python Code (Current Temporary Fix)
- **Pros**: No database admin access needed, immediate fix
- **Cons**: Data loss (interactions not logged), not a proper solution

### Option 2: Use Generic Interaction Type
- **Pros**: No schema change needed
- **Cons**: Loss of interaction type granularity, harder analytics

### Option 3: Remove Schema Validation
- **Pros**: Maximum flexibility
- **Cons**: Loss of data integrity checks

## Recommended Approach

**Primary Recommendation**: Proceed with MongoDB schema update (Step 1-6 above)

**Reasoning**:
1. Maintains data integrity while supporting all interaction types
2. Proper long-term solution
3. Enables full analytics and user behavior tracking
4. Minimal risk with proper backup and testing

## Timeline

1. **Week 1**: Obtain admin access and test in staging
2. **Week 2**: Schedule production deployment window
3. **Week 3**: Execute schema update and remove temporary code
4. **Week 4**: Monitor and validate full workflow

## Files to Update After Schema Fix

1. `backend/core/apps/preferences/models.py` - Remove temporary filtering
2. `frontend/src/app/app/onboarding/page.jsx` - Can use original interaction types
3. `backend/core/apps/preferences/serializers.py` - Can use original interaction types

## Success Criteria

✅ All 13 interaction types can be logged without errors
✅ MongoDB validation passes for all interaction types
✅ Manual save workflow works without filtering
✅ Onboarding flow logs interactions properly
✅ No data loss in interaction tracking
✅ Application logs show no MongoDB validation errors

---

**Note**: This plan requires MongoDB admin access. If admin access is not available, the temporary filtering solution should remain in place until proper database administration can be arranged.