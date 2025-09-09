// MongoDB sample data script for development and testing
// This script creates sample data for development/testing purposes

print('Adding sample data for development...');

// Switch to the gradvy_preferences database
db = db.getSiblingDB('gradvy_preferences');

// Sample user preferences for different user types
const samplePreferences = [
  {
    user_id: 1,
    created_at: new Date(),
    updated_at: new Date(),
    basic_info: {
      learning_goals: ['web_dev', 'javascript'],
      experience_level: 'some_basics',
      preferred_pace: 'medium',
      time_availability: '3-5hrs',
      learning_style: ['visual', 'hands_on'],
      career_stage: 'career_change',
      target_timeline: '6months'
    },
    content_preferences: {
      preferred_platforms: ['udemy', 'youtube'],
      content_types: ['video', 'interactive'],
      difficulty_preference: 'beginner',
      duration_preference: 'medium',
      language_preference: ['english'],
      instructor_ratings_min: 4.0
    },
    interactions: [
      {
        type: 'search',
        data: { query: 'javascript beginner' },
        timestamp: new Date(Date.now() - 86400000), // 1 day ago
        context: { page: 'dashboard' }
      },
      {
        type: 'course_click',
        data: { course_id: 'udemy_js_101', title: 'JavaScript for Beginners' },
        timestamp: new Date(Date.now() - 3600000), // 1 hour ago
        context: { source: 'search_results', position: 1 }
      }
    ]
  },
  {
    user_id: 2,
    created_at: new Date(),
    updated_at: new Date(),
    basic_info: {
      learning_goals: ['ai_ml', 'python'],
      experience_level: 'intermediate',
      preferred_pace: 'fast',
      time_availability: '5+hrs',
      learning_style: ['reading', 'hands_on'],
      career_stage: 'skill_upgrade',
      target_timeline: '3months'
    },
    content_preferences: {
      preferred_platforms: ['coursera', 'edx'],
      content_types: ['video', 'quiz', 'project'],
      difficulty_preference: 'intermediate',
      duration_preference: 'long',
      language_preference: ['english'],
      instructor_ratings_min: 4.5
    },
    interactions: [
      {
        type: 'course_enroll',
        data: { course_id: 'coursera_ml_101', title: 'Machine Learning Course' },
        timestamp: new Date(Date.now() - 604800000), // 1 week ago
        context: { source: 'recommendations' }
      },
      {
        type: 'quiz_attempt',
        data: { quiz_id: 'python_basics', score: 85 },
        timestamp: new Date(Date.now() - 7200000), // 2 hours ago
        context: { course_context: 'coursera_ml_101' }
      }
    ]
  }
];

// Insert sample user preferences
try {
  db.user_preferences.insertMany(samplePreferences);
  print(`Inserted ${samplePreferences.length} sample user preference records`);
} catch (error) {
  print('Note: Sample data may already exist or there was an insertion error');
  print('Error: ' + error);
}

// Sample learning sessions
const sampleSessions = [
  {
    user_id: 1,
    session_id: 'session_001_user1',
    start_time: new Date(Date.now() - 7200000), // 2 hours ago
    end_time: new Date(Date.now() - 3600000), // 1 hour ago
    duration: 3600,
    activities: [
      {
        activity_type: 'course_view',
        content_id: 'udemy_js_101',
        duration: 1800,
        completion_rate: 0.3,
        timestamp: new Date(Date.now() - 7200000)
      },
      {
        activity_type: 'video_watch',
        content_id: 'udemy_js_101_video_1',
        duration: 900,
        completion_rate: 1.0,
        timestamp: new Date(Date.now() - 5400000)
      },
      {
        activity_type: 'quiz_attempt',
        content_id: 'udemy_js_101_quiz_1',
        duration: 300,
        completion_rate: 1.0,
        timestamp: new Date(Date.now() - 3900000)
      }
    ],
    device_info: {
      type: 'desktop',
      os: 'Windows 10',
      browser: 'Chrome'
    }
  }
];

try {
  db.learning_sessions.insertMany(sampleSessions);
  print(`Inserted ${sampleSessions.length} sample learning session records`);
} catch (error) {
  print('Note: Sample session data may already exist or there was an insertion error');
  print('Error: ' + error);
}

// Sample course recommendations
const sampleRecommendations = [
  {
    user_id: 1,
    generated_at: new Date(),
    expires_at: new Date(Date.now() + 86400000), // Expires in 1 day
    recommendations: [
      {
        course_id: 'udemy_react_101',
        platform: 'udemy',
        title: 'React.js for Beginners',
        score: 0.95,
        reasoning: ['matches_learning_goal', 'appropriate_difficulty', 'high_rating'],
        metadata: {
          duration: '12 hours',
          rating: 4.6,
          students: 15000,
          price: 89.99
        }
      },
      {
        course_id: 'youtube_js_advanced',
        platform: 'youtube',
        title: 'Advanced JavaScript Concepts',
        score: 0.87,
        reasoning: ['skill_progression', 'free_content', 'matches_style'],
        metadata: {
          duration: '8 hours',
          views: 250000,
          likes: 12000,
          price: 0
        }
      }
    ],
    algorithm_version: 'v1.0.0'
  }
];

try {
  db.course_recommendations.insertMany(sampleRecommendations);
  print(`Inserted ${sampleRecommendations.length} sample recommendation records`);
} catch (error) {
  print('Note: Sample recommendation data may already exist or there was an insertion error');
  print('Error: ' + error);
}

// Create some AI training data samples
const sampleTrainingData = [
  {
    user_id: 1,
    event_type: 'positive_feedback',
    timestamp: new Date(Date.now() - 86400000),
    event_data: {
      course_id: 'udemy_js_101',
      feedback_type: 'thumbs_up',
      rating: 5
    },
    user_context: {
      learning_goal: 'web_dev',
      experience_level: 'some_basics',
      session_number: 3
    }
  },
  {
    user_id: 2,
    event_type: 'course_completion',
    timestamp: new Date(Date.now() - 604800000),
    event_data: {
      course_id: 'coursera_ml_101',
      completion_rate: 1.0,
      final_score: 88,
      time_taken: 86400 // 24 hours total
    },
    user_context: {
      learning_goal: 'ai_ml',
      experience_level: 'intermediate',
      target_timeline: '3months'
    }
  }
];

try {
  db.ai_training_data.insertMany(sampleTrainingData);
  print(`Inserted ${sampleTrainingData.length} sample AI training records`);
} catch (error) {
  print('Note: Sample AI training data may already exist or there was an insertion error');
  print('Error: ' + error);
}

print('Sample data insertion completed!');
print('Note: This sample data is for development/testing purposes only');