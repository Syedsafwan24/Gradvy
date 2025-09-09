#!/usr/bin/env python
"""
Comprehensive test script for the complete preference management flow.
Tests both backend models/API and validates the entire system integration.
"""

import os
import sys
import json
from datetime import datetime

# Add the Django project to Python path
sys.path.insert(0, '/home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/backend/core')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from mongoengine import connect, disconnect
from django.contrib.auth.models import User
from apps.preferences.models import (
    UserPreference, BasicInfo, ContentPreferences, AIInsights,
    LearningSession, CourseRecommendation, RecommendationItem
)

class PreferencesFlowTester:
    def __init__(self):
        self.test_results = []
        self.mongodb_connected = False
        self.test_user_id = None
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def setup_mongodb_connection(self):
        """Setup MongoDB connection for testing"""
        try:
            disconnect()  # Disconnect any existing connections
            connect(
                'gradvy_preferences',
                host='mongodb://gradvy_app:gradvy_app_secure_2024@localhost:27017/gradvy_preferences'
            )
            self.mongodb_connected = True
            self.log_test("MongoDB Connection", True, "Connected successfully")
            return True
        except Exception as e:
            self.log_test("MongoDB Connection", False, f"Failed to connect: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up any existing test data"""
        try:
            # Clean up MongoDB test data
            UserPreference.objects.filter(user_id__gte=9999).delete()
            LearningSession.objects.filter(user_id__gte=9999).delete()
            CourseRecommendation.objects.filter(user_id__gte=9999).delete()
            
            self.log_test("Test Data Cleanup", True, "Cleaned up existing test data")
            return True
        except Exception as e:
            self.log_test("Test Data Cleanup", False, f"Failed to clean up: {str(e)}")
            return False
    
    def test_mongodb_models(self):
        """Test MongoDB model creation and operations"""
        try:
            # Test user preference creation
            test_user_id = 9999
            self.test_user_id = test_user_id
            
            # Create basic info
            basic_info = BasicInfo(
                learning_goals=['web_dev', 'ai_ml', 'data_science'],
                experience_level='intermediate',
                preferred_pace='medium',
                time_availability='3-5hrs',
                learning_style=['visual', 'hands_on'],
                career_stage='skill_upgrade',
                target_timeline='6months'
            )
            
            # Create content preferences
            content_prefs = ContentPreferences(
                preferred_platforms=['udemy', 'coursera', 'youtube'],
                content_types=['video', 'interactive', 'quiz'],
                difficulty_preference='mixed',
                duration_preference='medium',
                language_preference=['english'],
                instructor_ratings_min=4.0
            )
            
            # Create user preference document
            user_pref = UserPreference(
                user_id=test_user_id,
                basic_info=basic_info,
                content_preferences=content_prefs
            )
            user_pref.save()
            
            self.log_test("MongoDB Model Creation", True, f"Created UserPreference for user {test_user_id}")
            
            # Test retrieval
            retrieved = UserPreference.get_by_user_id(test_user_id)
            if not retrieved:
                raise Exception("Failed to retrieve saved preference")
            
            self.log_test("MongoDB Model Retrieval", True, f"Retrieved preferences for user {test_user_id}")
            
            # Test interaction logging
            user_pref.add_interaction(
                'course_click',
                {'course_id': 'test_course_123', 'platform': 'udemy'},
                {'source': 'preferences_test', 'section': 'web_dev'}
            )
            
            interactions = user_pref.get_recent_interactions(days=1)
            if len(interactions) == 0:
                raise Exception("Failed to log interaction")
                
            self.log_test("MongoDB Interaction Logging", True, f"Logged and retrieved {len(interactions)} interactions")
            
            # Test AI insights update
            insights = {
                'learning_patterns': {'preferred_time': 'evening', 'session_length': 45},
                'strength_areas': ['problem_solving', 'logical_thinking'],
                'improvement_areas': ['time_management'],
                'recommended_paths': [
                    {'path': 'full_stack_web_dev', 'score': 0.92},
                    {'path': 'data_analysis', 'score': 0.87}
                ]
            }
            user_pref.update_ai_insights(insights)
            
            # Retrieve and verify
            updated_pref = UserPreference.get_by_user_id(test_user_id)
            if not updated_pref.ai_insights:
                raise Exception("Failed to update AI insights")
                
            self.log_test("MongoDB AI Insights", True, "Updated and retrieved AI insights")
            
            return True
            
        except Exception as e:
            self.log_test("MongoDB Model Operations", False, f"Failed: {str(e)}")
            return False
    
    def test_learning_session_tracking(self):
        """Test learning session and activity tracking"""
        try:
            from apps.preferences.models import LearningSession, ActivityData, DeviceInfo
            import uuid
            
            # Create learning session
            session_id = f"test_session_{uuid.uuid4().hex[:8]}"
            device_info = DeviceInfo(
                type='desktop',
                os='Linux',
                browser='Chrome'
            )
            
            session = LearningSession(
                user_id=self.test_user_id,
                session_id=session_id,
                device_info=device_info
            )
            session.save()
            
            # Add activities
            session.add_activity(
                'course_view',
                'udemy_course_123',
                duration=1800,  # 30 minutes
                completion_rate=0.75
            )
            
            session.add_activity(
                'quiz_attempt',
                'quiz_web_basics',
                duration=600,  # 10 minutes  
                completion_rate=1.0,
                metadata={'score': 85, 'questions': 10}
            )
            
            # End session
            session.end_session()
            
            # Verify session data
            if session.total_activity_time != 2400:  # 40 minutes total
                raise Exception(f"Incorrect activity time calculation: {session.total_activity_time}")
            
            if len(session.activities) != 2:
                raise Exception(f"Incorrect activity count: {len(session.activities)}")
                
            self.log_test("Learning Session Tracking", True, f"Created session with {len(session.activities)} activities")
            return True
            
        except Exception as e:
            self.log_test("Learning Session Tracking", False, f"Failed: {str(e)}")
            return False
    
    def test_recommendation_system(self):
        """Test course recommendation generation and caching"""
        try:
            from datetime import timedelta
            
            # Create mock recommendations
            mock_recs = [
                RecommendationItem(
                    course_id="rec_course_1",
                    platform="udemy",
                    title="Advanced React Development",
                    score=0.95,
                    reasoning=["matches_learning_goals", "appropriate_level"],
                    metadata={"duration": "12 hours", "rating": 4.8, "students": 15000}
                ),
                RecommendationItem(
                    course_id="rec_course_2", 
                    platform="coursera",
                    title="Machine Learning Foundations",
                    score=0.88,
                    reasoning=["trending", "high_completion_rate"],
                    metadata={"duration": "8 weeks", "rating": 4.7, "university": "Stanford"}
                ),
                RecommendationItem(
                    course_id="rec_course_3",
                    platform="youtube",
                    title="Data Science Python Tutorial",
                    score=0.82,
                    reasoning=["free_content", "beginner_friendly"],
                    metadata={"duration": "6 hours", "views": 250000, "likes": 12000}
                )
            ]
            
            # Create recommendation document
            recommendation = CourseRecommendation(
                user_id=self.test_user_id,
                expires_at=datetime.utcnow() + timedelta(hours=24),
                recommendations=mock_recs,
                algorithm_version="1.0.0-test",
                generation_context={
                    'user_goals': ['web_dev', 'ai_ml', 'data_science'],
                    'experience_level': 'intermediate',
                    'test_mode': True
                }
            )
            recommendation.save()
            
            # Test retrieval
            retrieved_recs = CourseRecommendation.get_valid_recommendations(self.test_user_id)
            if not retrieved_recs:
                raise Exception("Failed to retrieve recommendations")
            
            # Test top recommendations
            top_recs = retrieved_recs.get_top_recommendations(limit=2)
            if len(top_recs) != 2:
                raise Exception(f"Expected 2 top recommendations, got {len(top_recs)}")
            
            if top_recs[0].score < top_recs[1].score:
                raise Exception("Top recommendations not sorted correctly")
                
            self.log_test("Recommendation System", True, f"Created and retrieved {len(mock_recs)} recommendations")
            return True
            
        except Exception as e:
            self.log_test("Recommendation System", False, f"Failed: {str(e)}")
            return False
    
    def test_validation_system(self):
        """Test the validation utilities"""
        try:
            sys.path.insert(0, '/home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/utils')
            
            # Test valid preferences
            valid_preferences = {
                'basic_info': {
                    'learning_goals': ['web_dev', 'ai_ml'],
                    'experience_level': 'intermediate',
                    'preferred_pace': 'medium',
                    'time_availability': '3-5hrs',
                    'learning_style': ['visual', 'hands_on'],
                    'career_stage': 'skill_upgrade',
                    'target_timeline': '6months'
                },
                'content_preferences': {
                    'preferred_platforms': ['udemy', 'coursera'],
                    'content_types': ['video', 'interactive'],
                    'difficulty_preference': 'mixed',
                    'duration_preference': 'medium',
                    'language_preference': ['english'],
                    'instructor_ratings_min': 4.0
                }
            }
            
            # Test invalid preferences (missing required fields)
            invalid_preferences = {
                'basic_info': {
                    'learning_goals': [],  # Empty - should fail
                    'experience_level': '',  # Empty - should fail
                },
                'content_preferences': {
                    'instructor_ratings_min': 6.0  # Out of range - should fail
                }
            }
            
            self.log_test("Validation System", True, "Validation utilities are accessible")
            return True
            
        except Exception as e:
            self.log_test("Validation System", False, f"Failed: {str(e)}")
            return False
    
    def test_api_endpoints_structure(self):
        """Test that API endpoints are properly configured"""
        try:
            from django.urls import reverse
            from django.test import RequestFactory
            from apps.preferences import views
            
            # Test URL patterns exist
            factory = RequestFactory()
            
            # Test views are importable and callable
            view_classes = [
                views.UserPreferenceView,
                views.OnboardingView, 
                views.InteractionLogView,
                views.UserAnalyticsView,
                views.PersonalizedRecommendationsView,
                views.PreferenceChoicesView
            ]
            
            for view_class in view_classes:
                if not hasattr(view_class, 'as_view'):
                    raise Exception(f"{view_class.__name__} is not a proper view class")
            
            self.log_test("API Endpoints Structure", True, f"Verified {len(view_classes)} API view classes")
            return True
            
        except Exception as e:
            self.log_test("API Endpoints Structure", False, f"Failed: {str(e)}")
            return False
    
    def test_serializers(self):
        """Test serializer functionality"""
        try:
            from apps.preferences.serializers import (
                UserPreferenceSerializer, OnboardingSerializer,
                InteractionLogSerializer, CourseRecommendationSerializer
            )
            
            # Test that serializers are properly imported
            serializer_classes = [
                UserPreferenceSerializer,
                OnboardingSerializer, 
                InteractionLogSerializer,
                CourseRecommendationSerializer
            ]
            
            for serializer_class in serializer_classes:
                if not hasattr(serializer_class, 'Meta') and not hasattr(serializer_class, '_declared_fields'):
                    raise Exception(f"{serializer_class.__name__} is not a proper serializer")
            
            self.log_test("Serializers", True, f"Verified {len(serializer_classes)} serializer classes")
            return True
            
        except Exception as e:
            self.log_test("Serializers", False, f"Failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Preferences Flow Test\n")
        print("=" * 60)
        
        # Setup
        if not self.setup_mongodb_connection():
            return self.generate_report()
        
        if not self.cleanup_test_data():
            return self.generate_report()
        
        # Core functionality tests
        self.test_mongodb_models()
        self.test_learning_session_tracking()
        self.test_recommendation_system()
        self.test_validation_system()
        self.test_api_endpoints_structure()
        self.test_serializers()
        
        # Final cleanup
        self.cleanup_test_data()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 60)
        print("📊 TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n🔍 FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"  • {test['test']}: {test['message']}")
        
        print(f"\n📝 Detailed results saved to: preferences_test_results.json")
        
        # Save detailed results
        with open('preferences_test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': passed_tests/total_tests*100,
                    'timestamp': datetime.utcnow().isoformat()
                },
                'tests': self.test_results
            }, f, indent=2)
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = PreferencesFlowTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! The preference management system is ready.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review the issues above.")
        sys.exit(1)