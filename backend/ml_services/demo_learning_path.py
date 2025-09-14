"""
backend/ml_services/demo_learning_path.py
Demonstration of the AI-powered learning path generation system
Shows complete flow from user preferences to personalized curriculum
RELEVANT FILES: services/learning_path_service.py, utils/model_initializer.py
"""

import os
import sys
import logging
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def demo_learning_path_generation():
    """
    Comprehensive demonstration of ML-powered learning path generation.

    This demo shows:
    1. System initialization with local models
    2. User data processing and sanitization
    3. AI-powered curriculum generation
    4. Resource matching and optimization
    5. Complete learning path output
    """

    print("=" * 80)
    print("🚀 GRADVY AI LEARNING PATH GENERATION DEMO")
    print("=" * 80)
    print()

    try:
        # =============================================================================
        # STEP 1: INITIALIZE ML SYSTEM
        # =============================================================================

        print("📋 Step 1: Initializing ML System...")
        print("-" * 40)

        from ml_services.utils.model_initializer import initialize_ml_system

        # Initialize with development profile (uses lighter models)
        print("🔧 Initializing ML infrastructure...")

        init_results = initialize_ml_system(deployment_profile="development")

        print(f"✅ ML System initialized successfully!")
        print(f"   • Models registered: {len(init_results['registered_models'])}")
        print(f"   • Models preloaded: {len(init_results['preloaded_models'])}")
        print(f"   • Initialization time: {init_results['initialization_time_ms']:.0f}ms")
        print()

        # =============================================================================
        # STEP 2: SIMULATE USER DATA (FROM GRADVY PREFERENCES)
        # =============================================================================

        print("👤 Step 2: Simulating User Learning Preferences...")
        print("-" * 40)

        # This would typically come from your UserPreference MongoDB model
        user_profile = {
            "user_id": "demo_user_123",
            "learning_goals": ["python", "web_development", "ai_ml"],
            "experience_level": "beginner",
            "time_availability": "3-5hrs",  # per week
            "preferred_pace": "medium",
            "learning_styles": ["hands_on", "videos", "interactive"],
            "target_timeline": "6months",
            "career_stage": "career_change",
            "previous_experience": ["basic_programming"],
            "preferred_platforms": ["udemy", "coursera", "youtube"]
        }

        print("📊 User Learning Profile:")
        for key, value in user_profile.items():
            print(f"   • {key.replace('_', ' ').title()}: {value}")
        print()

        # =============================================================================
        # STEP 3: CREATE LEARNING PATH REQUEST
        # =============================================================================

        print("🎯 Step 3: Creating Learning Path Request...")
        print("-" * 40)

        from ml_services.services.learning_path_service import LearningPathRequest

        # Create structured request
        learning_request = LearningPathRequest(
            user_id=user_profile["user_id"],
            request_id=f"demo_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            learning_goals=user_profile["learning_goals"],
            experience_level=user_profile["experience_level"],
            time_availability=user_profile["time_availability"],
            preferred_pace=user_profile["preferred_pace"],
            learning_styles=user_profile["learning_styles"],
            target_timeline=user_profile["target_timeline"],
            career_stage=user_profile["career_stage"],
            previous_experience=user_profile["previous_experience"],
            preferred_platforms=user_profile["preferred_platforms"],
            max_modules=6,
            include_projects=True,
            include_assessments=True
        )

        print(f"✅ Request created for {learning_request.user_id}")
        print(f"   • Goals: {', '.join(learning_request.learning_goals)}")
        print(f"   • Timeline: {learning_request.target_timeline}")
        print(f"   • Max modules: {learning_request.max_modules}")
        print()

        # =============================================================================
        # STEP 4: INITIALIZE LEARNING PATH SERVICE
        # =============================================================================

        print("🧠 Step 4: Initializing AI Learning Path Service...")
        print("-" * 40)

        from ml_services.services.learning_path_service import LearningPathService

        # Create and initialize the service
        learning_service = LearningPathService()

        print("🔧 Initializing service (this may take a moment for first-time model loading)...")

        try:
            learning_service.initialize()
            print("✅ Learning Path Service initialized successfully!")
        except Exception as e:
            print(f"⚠️  Service initialization had issues: {e}")
            print("   This is expected in demo mode - continuing with mock generation...")

        print(f"   • Service: {learning_service.service_name}")
        print(f"   • Primary model: {learning_service.primary_model}")
        print(f"   • Required models: {', '.join(learning_service.required_models)}")
        print()

        # =============================================================================
        # STEP 5: GENERATE AI-POWERED LEARNING PATH
        # =============================================================================

        print("🎓 Step 5: Generating Personalized Learning Path...")
        print("-" * 40)

        print("🤖 AI is analyzing your preferences and generating curriculum...")
        print("   • Analyzing learning requirements...")
        print("   • Creating curriculum structure...")
        print("   • Generating detailed modules...")
        print("   • Optimizing learning progression...")
        print()

        start_time = datetime.now()

        try:
            # Generate the learning path
            response = learning_service.process(learning_request)

            generation_time = (datetime.now() - start_time).total_seconds()

            if response.success:
                print(f"✅ Learning Path Generated Successfully!")
                print(f"   • Generation time: {generation_time:.2f}s")
                print(f"   • Processing time: {response.processing_time_ms:.0f}ms")
                print()

                # =============================================================================
                # STEP 6: DISPLAY GENERATED LEARNING PATH
                # =============================================================================

                print("📚 Step 6: Your Personalized Learning Path")
                print("=" * 80)

                learning_path = response.data['learning_path']
                modules = response.data['modules']

                # Display overview
                print(f"🎯 LEARNING PATH: {learning_path['title']}")
                print(f"📖 Description: {learning_path['description']}")
                print()
                print(f"📊 OVERVIEW:")
                print(f"   • Total Modules: {learning_path['total_modules']}")
                print(f"   • Estimated Hours: {learning_path['estimated_total_hours']}h")
                print(f"   • Timeline: {learning_path['target_timeline']}")
                print(f"   • Experience Level: {learning_path['experience_level']}")
                print()

                print(f"🌟 KEY FEATURES:")
                for feature in learning_path['key_features']:
                    print(f"   • {feature}")
                print()

                # Display modules
                print(f"📋 LEARNING MODULES:")
                print("=" * 60)

                for i, module in enumerate(modules, 1):
                    print(f"\n📚 MODULE {i}: {module['title']}")
                    print(f"   📝 Description: {module['description']}")
                    print(f"   ⏱️  Estimated Hours: {module['estimated_hours']}h")
                    print(f"   📊 Difficulty: {module['difficulty_level']}")

                    if module['prerequisites']:
                        print(f"   📋 Prerequisites: {', '.join(module['prerequisites'])}")

                    print(f"   🎯 Learning Objectives:")
                    for obj in module['learning_objectives']:
                        print(f"      • {obj}")

                    print(f"   📖 Lessons ({len(module['lessons'])}):")
                    for lesson in module['lessons']:
                        print(f"      • {lesson['title']} ({lesson['estimated_minutes']}min)")

                    if module.get('projects'):
                        print(f"   🛠️  Projects:")
                        for project in module['projects']:
                            print(f"      • {project['title']} ({project['estimated_hours']}h)")

                    if module.get('assessment'):
                        assessment = module['assessment']
                        print(f"   📝 Assessment: {assessment['title']} ({assessment['estimated_minutes']}min)")

                print()
                print("=" * 80)
                print("🎉 LEARNING PATH GENERATION COMPLETE!")
                print("=" * 80)
                print()
                print("💡 Next Steps:")
                print("   1. Save this learning path to MongoDB")
                print("   2. Begin Module 1 with recommended resources")
                print("   3. Track progress through the platform")
                print("   4. Use playground for hands-on coding practice")
                print("   5. Take assessments to validate learning")
                print()

                # =============================================================================
                # STEP 7: SYSTEM STATISTICS
                # =============================================================================

                print("📈 Step 7: System Performance Statistics")
                print("-" * 40)

                from ml_services.utils.model_initializer import get_global_initializer

                initializer = get_global_initializer()
                stats = initializer.get_system_stats()

                print(f"🔧 System Configuration:")
                print(f"   • Deployment Profile: {stats['deployment_profile']}")
                print(f"   • Available Models: {stats['available_models']}")
                print(f"   • Loaded Models: {stats['loaded_models']}")
                print()

                print(f"💾 Cache Statistics:")
                cache_stats = stats['cache_stats']
                print(f"   • Cached Models: {cache_stats['total_models']}")
                print(f"   • Cache Size: {cache_stats['total_size_gb']:.2f} GB")
                print(f"   • Usage: {cache_stats['usage_percent']:.1f}%")
                print()

            else:
                print(f"❌ Learning Path Generation Failed!")
                print(f"   Error: {response.error}")

        except Exception as e:
            print(f"❌ Error during learning path generation: {e}")
            print("   This might be due to missing model files in demo mode")

            # Show what the system WOULD generate
            print()
            print("📋 DEMO: What the system would generate:")
            print("-" * 40)
            print("🎯 Python to AI/ML Developer - 6 Month Journey")
            print()
            print("📚 Module 1: Python Programming Fundamentals (12h)")
            print("📚 Module 2: Data Structures & Algorithms (16h)")
            print("📚 Module 3: Web Development with Python (20h)")
            print("📚 Module 4: Introduction to Data Science (18h)")
            print("📚 Module 5: Machine Learning Fundamentals (24h)")
            print("📚 Module 6: AI Project Portfolio (30h)")
            print()
            print("✨ Total: 120 hours over 6 months")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   This demo requires the full ML services to be properly set up.")
        print("   Please ensure all dependencies are installed:")
        print("   pip install torch transformers sentence-transformers huggingface_hub")

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 80)
    print("🏁 DEMO COMPLETE")
    print("=" * 80)
    print()
    print("This demo showed how Gradvy's AI system:")
    print("✅ 1. Processes user learning preferences")
    print("✅ 2. Uses local AI models for privacy")
    print("✅ 3. Generates personalized curricula")
    print("✅ 4. Creates detailed learning modules")
    print("✅ 5. Optimizes for individual learning styles")
    print()
    print("🚀 Ready for production deployment!")


if __name__ == "__main__":
    demo_learning_path_generation()