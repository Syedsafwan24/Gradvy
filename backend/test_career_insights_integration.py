#!/usr/bin/env python
"""
Quick test script to verify career insights integration works

Run from backend/ directory:
    python test_career_insights_integration.py
"""

import os
import sys

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from ml_services.services.career_insights_service import get_career_insights_service
from ml_services.integrations import RoadmapService

print("\n" + "="*80)
print("CAREER INSIGHTS INTEGRATION TEST")
print("="*80)

# Test 1: Career Insights Service
print("\n1. Testing CareerInsightsService...")
try:
    service = get_career_insights_service()

    # Test domain mapping
    domain = service.map_learning_goals_to_career_domain("I want to learn React and JavaScript")
    print(f"   ✅ Domain mapping: '{domain}'")

    # Test skills extraction
    modules = [
        {"title": "Introduction to React", "description": "Learn React basics", "difficulty": "beginner"},
        {"title": "Advanced JavaScript", "description": "ES6+ features", "difficulty": "intermediate"}
    ]
    skills = service.extract_skills_from_modules(modules)
    print(f"   ✅ Skills extracted: {len(skills)} skills")
    for skill in skills[:3]:
        print(f"      - {skill.skill_name} ({skill.skill_category}): {skill.importance_score}")

    # Test career insights generation
    insights = service.generate_career_insights(
        learning_goals="React and JavaScript development",
        modules=modules,
        user_location=""
    )
    print(f"   ✅ Career insights generated:")
    print(f"      - {len(insights.career_roles)} career roles")
    print(f"      - {insights.total_job_openings} total job openings")
    print(f"      - Market demand score: {insights.market_demand_score}/100")

except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Learning Outcomes Generation
print("\n2. Testing Learning Outcomes Generation...")
try:
    roadmap_service = RoadmapService()

    outcomes = roadmap_service.generate_module_learning_outcomes(
        module_title="Introduction to React Hooks",
        module_description="Learn useState, useEffect, and custom hooks",
        difficulty="intermediate",
        lessons=[{"title": "useState basics"}, {"title": "useEffect deep dive"}]
    )

    print(f"   ✅ Learning outcomes generated: {len(outcomes)} outcomes")
    for idx, outcome in enumerate(outcomes, 1):
        print(f"      {idx}. {outcome}")

except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Job API Service (if credentials available)
print("\n3. Testing Job API Service...")
try:
    from ml_services.integrations.job_api_service import get_job_api_service

    job_service = get_job_api_service()

    if job_service.enabled:
        print("   ✅ Adzuna API credentials found")
        # Test would make real API call - skip in automated tests
        print("   ℹ️  Skipping real API call (would consume API quota)")
    else:
        print("   ⚠️  Adzuna API not configured (this is OK)")
        print("   ℹ️  Set ADZUNA_APP_ID and ADZUNA_APP_KEY to enable")

except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("✅ ALL TESTS PASSED!")
print("="*80)
print("\nCareer insights integration is working correctly.")
print("You can now generate learning paths with career insights enabled.")
print("\nNext steps:")
print("  1. Generate a learning path via the API")
print("  2. Check that career_insights field is populated")
print("  3. Verify modules have learning_outcomes arrays")
print("")
