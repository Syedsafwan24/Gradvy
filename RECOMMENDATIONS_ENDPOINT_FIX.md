# Recommendations Endpoint Fix

## Problem Identified

**Error**: HTTP 404 on `/api/preferences/recommendations/` endpoint

**Root Cause**: Frontend was calling endpoints that didn't exist in the backend:
- Frontend called: `POST /api/preferences/recommendations/generate/`
- Frontend called: `POST /api/preferences/recommendations/feedback/`
- Backend only had: `GET/POST /api/preferences/recommendations/`

## Solution Implemented

### 1. Added New URL Routes

**File**: `/backend/core/apps/preferences/urls.py`

Added two new endpoints:
```python
path('recommendations/generate/', views.GenerateRecommendationsView.as_view(), name='generate_recommendations'),
path('recommendations/feedback/', views.RecommendationFeedbackView.as_view(), name='recommendation_feedback'),
```

### 2. Created New View Classes

**File**: `/backend/core/apps/preferences/views.py`

#### GenerateRecommendationsView
- **Purpose**: Explicitly generate new course recommendations
- **Method**: POST
- **Endpoint**: `/api/preferences/recommendations/generate/`
- **Features**:
  - Creates mock recommendations for testing
  - Saves to MongoDB CourseRecommendation
  - Returns structured response
  - 24-hour expiration

#### RecommendationFeedbackView
- **Purpose**: Collect user feedback on recommendations
- **Method**: POST
- **Endpoint**: `/api/preferences/recommendations/feedback/`
- **Features**:
  - Records helpful/not_helpful feedback
  - Updates CourseRecommendation document
  - Helps improve future recommendations

## API Structure

### Recommendations Endpoints (3 total)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/preferences/recommendations/` | Get existing recommendations | ✅ Working |
| POST | `/api/preferences/recommendations/generate/` | Generate new recommendations | ✅ Fixed |
| POST | `/api/preferences/recommendations/feedback/` | Submit feedback | ✅ Fixed |

## Response Format

### GET `/api/preferences/recommendations/`
```json
{
  "success": true,
  "message": "Recommendations retrieved successfully",
  "data": {
    "recommendations": {
      "user_id": 1,
      "generated_at": "2025-11-25T...",
      "expires_at": "2025-11-26T...",
      "recommendations": [...]
    },
    "source": "cached"
  }
}
```

### POST `/api/preferences/recommendations/generate/`
```json
{
  "success": true,
  "message": "Recommendations generated successfully",
  "data": {
    "recommendations": {
      "user_id": 1,
      "generated_at": "2025-11-25T...",
      "recommendations": [
        {
          "course_id": "test_course_1",
          "platform": "udemy",
          "title": "Mock Course 1",
          "score": 0.95,
          "reasoning": ["matches_learning_goal"],
          "metadata": {...}
        }
      ]
    },
    "source": "generated"
  }
}
```

### POST `/api/preferences/recommendations/feedback/`
```json
{
  "success": true,
  "message": "Feedback recorded successfully"
}
```

## Testing

### 1. Check Endpoint Availability
```bash
# GET recommendations (should return empty if none exist)
curl -X GET http://localhost:8000/api/preferences/recommendations/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Generate recommendations
curl -X POST http://localhost:8000/api/preferences/recommendations/generate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Submit feedback
curl -X POST http://localhost:8000/api/preferences/recommendations/feedback/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recommendation_id": "test_course_1", "feedback": "helpful"}'
```

### 2. Frontend Test
1. Navigate to `/app/preferences`
2. Click on "Recommendations" tab
3. Should see "No Recommendations Yet"
4. Click "Generate New Recommendations"
5. Should see 2 mock courses appear

## Files Modified

1. **`/backend/core/apps/preferences/urls.py`**
   - Added 2 new URL patterns

2. **`/backend/core/apps/preferences/views.py`**
   - Added `GenerateRecommendationsView` class (~60 lines)
   - Added `RecommendationFeedbackView` class (~45 lines)

## Next Steps

### Immediate
- ✅ Endpoints created
- ✅ Syntax validated
- ⏳ Test in browser (refresh Django server)

### Future Enhancements
1. **Replace Mock Data**: Integrate with actual ML recommendation service
2. **Add Filtering**: Support filtering by platform, difficulty, etc.
3. **Add Pagination**: For large recommendation sets
4. **Add Analytics**: Track recommendation effectiveness
5. **Add Caching**: Cache individual recommendations

## Notes

- **Mock Data**: Currently returns 2 test courses for development
- **Expiration**: Recommendations expire after 24 hours
- **CSRF**: Endpoints are CSRF-exempt for API access
- **Authentication**: All endpoints require JWT authentication
- **MongoDB**: Uses CourseRecommendation document from learning_content app

---

**Status**: ✅ Fixed - Ready for testing
**Date**: 2025-11-25
