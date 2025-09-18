# MongoDB Platform Schema Fix - Immediate Action Required

## 🚨 **Critical Issue**

**Problem**: MongoDB collection schema validation only allows 7 platforms, but the MongoEngine model defines 25+ platforms. This causes validation errors when users select platforms like `freecodecamp`, `codecademy`, `skillshare`, etc.

**Impact**: Users cannot save preferences containing unsupported platforms, leading to 500 errors and poor user experience.

**Affected Field**: `content_preferences.preferred_platforms`

## 📊 **Current vs Required Schema**

### **Current MongoDB Schema (Restrictive)**
```json
{
  "content_preferences": {
    "properties": {
      "preferred_platforms": {
        "items": {
          "enum": [
            "udemy", "coursera", "youtube", "edx", "khan_academy",
            "pluralsight", "linkedin_learning"
          ]
        }
      }
    }
  }
}
```

### **Required MongoDB Schema (Complete)**
```json
{
  "content_preferences": {
    "properties": {
      "preferred_platforms": {
        "items": {
          "enum": [
            "udemy", "coursera", "youtube", "edx", "khan_academy",
            "pluralsight", "linkedin_learning", "codecademy", "freecodecamp",
            "skillshare", "masterclass", "brilliant", "datacamp", "codewars",
            "hackerrank", "leetcode", "udacity", "treehouse", "laracasts",
            "egghead", "frontend_masters", "css_tricks", "mdn_web_docs",
            "w3schools", "stackoverflow", "github", "medium", "dev_to"
          ]
        }
      }
    }
  }
}
```

## 🔧 **Implementation Steps**

### **Step 1: Backup Database**
```bash
# Create backup before making schema changes
mongodump --db gradvy_preferences --collection user_preferences --out ./backup_$(date +%Y%m%d_%H%M%S)/
```

### **Step 2: Connect to MongoDB**
```bash
# Local development
mongosh "mongodb://localhost:27017/gradvy_preferences"

# Or for production/cloud instances
mongosh "mongodb+srv://cluster.mongodb.net/gradvy_preferences" --username admin
```

### **Step 3: Update Collection Schema Validation**
```javascript
// Update the validation schema to include all platform choices
db.runCommand({
  "collMod": "user_preferences",
  "validator": {
    "$jsonSchema": {
      "bsonType": "object",
      "properties": {
        "content_preferences": {
          "bsonType": ["object", "null"],
          "properties": {
            "preferred_platforms": {
              "bsonType": ["array"],
              "items": {
                "bsonType": "string",
                "enum": [
                  "udemy", "coursera", "youtube", "edx", "khan_academy",
                  "pluralsight", "linkedin_learning", "codecademy", "freecodecamp",
                  "skillshare", "masterclass", "brilliant", "datacamp", "codewars",
                  "hackerrank", "leetcode", "udacity", "treehouse", "laracasts",
                  "egghead", "frontend_masters", "css_tricks", "mdn_web_docs",
                  "w3schools", "stackoverflow", "github", "medium", "dev_to"
                ]
              }
            },
            "content_types": {
              "bsonType": ["array"],
              "items": {
                "bsonType": "string",
                "enum": ["video", "article", "interactive", "quiz", "project", "book", "podcast"]
              }
            },
            "difficulty_preference": {
              "bsonType": ["string", "null"],
              "enum": ["mixed", "beginner", "intermediate", "advanced"]
            },
            "duration_preference": {
              "bsonType": ["string", "null"],
              "enum": ["short", "medium", "long", "mixed"]
            },
            "language_preference": {
              "bsonType": ["array"],
              "items": {
                "bsonType": "string"
              }
            },
            "instructor_ratings_min": {
              "bsonType": ["double", "int", "null"],
              "minimum": 0.0,
              "maximum": 5.0
            }
          }
        }
      }
    }
  },
  "validationLevel": "strict",
  "validationAction": "error"
})
```

### **Step 4: Verify Schema Update**
```javascript
// Test that freecodecamp is now accepted
db.user_preferences.findOne({user_id: 11}).content_preferences.preferred_platforms;

// Try updating a document with freecodecamp
db.user_preferences.updateOne(
  {user_id: 999999},
  {
    $set: {
      "content_preferences.preferred_platforms": ["youtube", "udemy", "freecodecamp"]
    }
  },
  {upsert: true}
);

// Verify it worked (should not throw validation error)
db.user_preferences.findOne({user_id: 999999});

// Clean up test document
db.user_preferences.deleteOne({user_id: 999999});
```

### **Step 5: Remove Temporary Code**

After schema update is successful, remove the temporary defensive code:

1. **Remove from `serializers.py`**:
   ```python
   # Remove the validate_preferred_platforms method in ContentPreferencesSerializer
   # Lines 94-122 in serializers.py
   ```

2. **Update error messages in `views.py`**:
   ```python
   # Update platform error messages to remove "temporarily unavailable" language
   # Lines 318-335 in views.py
   ```

## 🧪 **Testing Checklist**

After schema update:

- [ ] User can select `freecodecamp` and save preferences
- [ ] User can select `codecademy` and save preferences
- [ ] User can select multiple platforms including previously unsupported ones
- [ ] No MongoDB validation errors in application logs
- [ ] Existing users with filtered platforms can now select full range
- [ ] Frontend platform selection works correctly

## 📋 **Verification Commands**

```javascript
// Check current schema validation
db.runCommand({collStats: "user_preferences"});

// Count documents with each platform (after update)
db.user_preferences.aggregate([
  {$unwind: "$content_preferences.preferred_platforms"},
  {$group: {_id: "$content_preferences.preferred_platforms", count: {$sum: 1}}},
  {$sort: {count: -1}}
]);

// Check for any remaining validation errors
db.user_preferences.find({"content_preferences.preferred_platforms": "freecodecamp"});
```

## ⚠️ **Important Notes**

1. **Staging First**: Test this schema update in staging environment before production
2. **Backup Essential**: Always backup before schema modifications
3. **Coordination Required**: Coordinate with application deployment to remove temporary code
4. **Monitor After**: Watch application logs for any validation errors after update

## 🎯 **Success Criteria**

✅ All 25 platforms from MongoEngine model are accepted by MongoDB schema
✅ Users can save preferences with any supported platform combination
✅ No more MongoDB validation errors for platform choices
✅ Defensive filtering code successfully removed
✅ User experience restored to full functionality

## 📞 **Support**

If you encounter issues during schema update:

1. Check MongoDB logs for detailed error messages
2. Verify connection has proper admin privileges
3. Ensure database name and collection name are correct
4. Contact database administrator if permission issues occur

---

**Estimated Time**: 15-30 minutes (including backup and testing)
**Risk Level**: Low (schema updates are non-destructive with proper backup)
**Rollback**: Restore from backup if issues occur