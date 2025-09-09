// MongoDB initialization script for Gradvy preferences database
// This script runs when MongoDB container starts for the first time

print('Starting Gradvy MongoDB initialization...');

// Switch to the gradvy_preferences database
db = db.getSiblingDB('gradvy_preferences');

// Create application user for Django
db.createUser({
  user: 'gradvy_app',
  pwd: 'gradvy_app_secure_2024',
  roles: [
    {
      role: 'readWrite',
      db: 'gradvy_preferences'
    }
  ]
});

print('Created application user: gradvy_app');

// Create collections with validation schemas

// User Preferences Collection
db.createCollection('user_preferences', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'created_at', 'updated_at'],
      properties: {
        user_id: {
          bsonType: 'int',
          description: 'PostgreSQL user ID reference - required'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp - required'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Last update timestamp - required'
        },
        basic_info: {
          bsonType: 'object',
          properties: {
            learning_goals: {
              bsonType: 'array',
              items: { bsonType: 'string' }
            },
            experience_level: {
              enum: ['complete_beginner', 'some_basics', 'intermediate', 'advanced']
            },
            preferred_pace: {
              enum: ['slow', 'medium', 'fast']
            },
            time_availability: {
              enum: ['1-2hrs', '3-5hrs', '5+hrs']
            },
            learning_style: {
              bsonType: 'array',
              items: { 
                enum: ['visual', 'hands_on', 'reading', 'videos', 'interactive']
              }
            },
            career_stage: {
              enum: ['student', 'career_change', 'skill_upgrade', 'professional']
            },
            target_timeline: {
              enum: ['3months', '6months', '1year', 'flexible']
            }
          }
        },
        interactions: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['type', 'timestamp'],
            properties: {
              type: {
                enum: ['course_click', 'quiz_attempt', 'video_watch', 'search', 'page_view', 'course_enroll', 'course_complete']
              },
              data: { bsonType: 'object' },
              timestamp: { bsonType: 'date' },
              context: { bsonType: 'object' }
            }
          }
        },
        ai_insights: {
          bsonType: 'object',
          properties: {
            learning_patterns: { bsonType: 'object' },
            strength_areas: {
              bsonType: 'array',
              items: { bsonType: 'string' }
            },
            improvement_areas: {
              bsonType: 'array',
              items: { bsonType: 'string' }
            },
            recommended_paths: {
              bsonType: 'array',
              items: { bsonType: 'object' }
            },
            updated_at: { bsonType: 'date' }
          }
        },
        content_preferences: {
          bsonType: 'object',
          properties: {
            preferred_platforms: {
              bsonType: 'array',
              items: { 
                enum: ['udemy', 'coursera', 'youtube', 'edx', 'khan_academy', 'pluralsight', 'linkedin_learning']
              }
            },
            content_types: {
              bsonType: 'array',
              items: { 
                enum: ['video', 'article', 'interactive', 'quiz', 'project', 'book']
              }
            },
            difficulty_preference: {
              enum: ['mixed', 'beginner', 'intermediate', 'advanced']
            },
            duration_preference: {
              enum: ['short', 'medium', 'long', 'mixed']
            },
            language_preference: {
              bsonType: 'array',
              items: { bsonType: 'string' }
            },
            instructor_ratings_min: {
              bsonType: 'double',
              minimum: 0,
              maximum: 5
            }
          }
        }
      }
    }
  }
});

print('Created user_preferences collection with validation schema');

// Create indexes for better performance
db.user_preferences.createIndex({ user_id: 1 }, { unique: true });
db.user_preferences.createIndex({ 'updated_at': -1 });
db.user_preferences.createIndex({ 'basic_info.learning_goals': 1 });
db.user_preferences.createIndex({ 'interactions.timestamp': -1 });

print('Created indexes on user_preferences collection');

// User Learning Sessions Collection (for detailed tracking)
db.createCollection('learning_sessions', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'session_id', 'start_time'],
      properties: {
        user_id: {
          bsonType: 'int',
          description: 'PostgreSQL user ID reference - required'
        },
        session_id: {
          bsonType: 'string',
          description: 'Unique session identifier - required'
        },
        start_time: {
          bsonType: 'date',
          description: 'Session start timestamp - required'
        },
        end_time: {
          bsonType: 'date',
          description: 'Session end timestamp'
        },
        duration: {
          bsonType: 'int',
          description: 'Session duration in seconds'
        },
        activities: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              activity_type: {
                enum: ['course_view', 'video_watch', 'quiz_attempt', 'coding_practice', 'reading']
              },
              content_id: { bsonType: 'string' },
              duration: { bsonType: 'int' },
              completion_rate: { bsonType: 'double' },
              timestamp: { bsonType: 'date' }
            }
          }
        },
        device_info: {
          bsonType: 'object',
          properties: {
            type: { enum: ['desktop', 'mobile', 'tablet'] },
            os: { bsonType: 'string' },
            browser: { bsonType: 'string' }
          }
        }
      }
    }
  }
});

// Create indexes for learning sessions
db.learning_sessions.createIndex({ user_id: 1, start_time: -1 });
db.learning_sessions.createIndex({ session_id: 1 }, { unique: true });

print('Created learning_sessions collection with indexes');

// Course Recommendations Collection (cache for personalized recommendations)
db.createCollection('course_recommendations', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'generated_at'],
      properties: {
        user_id: {
          bsonType: 'int',
          description: 'PostgreSQL user ID reference - required'
        },
        generated_at: {
          bsonType: 'date',
          description: 'Recommendation generation timestamp - required'
        },
        expires_at: {
          bsonType: 'date',
          description: 'Recommendation expiry timestamp'
        },
        recommendations: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              course_id: { bsonType: 'string' },
              platform: { bsonType: 'string' },
              title: { bsonType: 'string' },
              score: { bsonType: 'double' },
              reasoning: { bsonType: 'array' },
              metadata: { bsonType: 'object' }
            }
          }
        },
        algorithm_version: {
          bsonType: 'string',
          description: 'Version of recommendation algorithm used'
        }
      }
    }
  }
});

// Create indexes for course recommendations
db.course_recommendations.createIndex({ user_id: 1 });
db.course_recommendations.createIndex({ expires_at: 1 });

print('Created course_recommendations collection with indexes');

// AI Training Data Collection (for improving personalization)
db.createCollection('ai_training_data', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'event_type', 'timestamp'],
      properties: {
        user_id: {
          bsonType: 'int',
          description: 'PostgreSQL user ID reference - required'
        },
        event_type: {
          enum: ['positive_feedback', 'negative_feedback', 'course_completion', 'course_abandonment', 'rating_given'],
          description: 'Type of training event - required'
        },
        timestamp: {
          bsonType: 'date',
          description: 'Event timestamp - required'
        },
        event_data: {
          bsonType: 'object',
          description: 'Event-specific data'
        },
        user_context: {
          bsonType: 'object',
          description: 'User context at time of event'
        }
      }
    }
  }
});

// Create indexes for AI training data
db.ai_training_data.createIndex({ user_id: 1, timestamp: -1 });
db.ai_training_data.createIndex({ event_type: 1, timestamp: -1 });

print('Created ai_training_data collection with indexes');

print('Gradvy MongoDB initialization completed successfully!');
print('Collections created:');
print('- user_preferences (with validation and indexes)');
print('- learning_sessions (for detailed session tracking)');
print('- course_recommendations (for caching personalized recommendations)');
print('- ai_training_data (for ML model improvement)');
print('Application user "gradvy_app" created with readWrite permissions');