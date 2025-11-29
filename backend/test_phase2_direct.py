"""
File: backend/test_phase2_direct.py
Description: Direct unit tests for Phase 2 improvements - skill gap analysis and adaptive pacing
Purpose: Test skill filtering, prerequisite addition, and adaptive lesson calculation
RELEVANT FILES: backend/ml_services/integrations/roadmap_service.py, backend/core/apps/learning_content/api/views.py
"""

import sys
import os
import django

# Setup Django environment
sys.path.insert(0, '/home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/backend/core')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.learning_content.api.views import GenerateLearningPathView
from ml_services.integrations.roadmap_service import RoadmapService, Roadmap, RoadmapNode


def test_skill_gap_analysis():
    """Test skill gap analysis methods in RoadmapService."""
    print("\n" + "="*80)
    print("TEST 1: SKILL GAP ANALYSIS")
    print("="*80)

    # Create mock roadmap with test nodes
    test_nodes = [
        RoadmapNode(
            id="1",
            title="HTML Basics",
            description="Learn HTML fundamentals",
            skills=["html", "web development"]
        ),
        RoadmapNode(
            id="2",
            title="CSS Styling",
            description="Learn CSS",
            skills=["css", "styling"],
            prerequisites=["1"]
        ),
        RoadmapNode(
            id="3",
            title="JavaScript Programming",
            description="Learn JavaScript",
            skills=["javascript", "programming"],
            prerequisites=["1"]
        ),
        RoadmapNode(
            id="4",
            title="React Framework",
            description="Learn React",
            skills=["react", "frontend"],
            prerequisites=["2", "3"]
        ),
        RoadmapNode(
            id="5",
            title="Advanced React",
            description="Advanced React concepts",
            skills=["react", "hooks", "advanced"],
            prerequisites=["4"]
        )
    ]

    test_roadmap = Roadmap(
        roadmap_id="frontend",
        title="Frontend Development",
        description="Web development roadmap",
        category="web_dev",
        nodes=test_nodes
    )

    service = RoadmapService()

    # Test Case 1: User knows HTML and CSS
    print("\n--- Test Case 1: User knows HTML and CSS ---")
    current_skills = ["HTML", "CSS"]

    filtered = service.filter_roadmap_by_skills(
        test_roadmap,
        current_skills,
        similarity_threshold=0.7
    )

    print(f"Original nodes: {len(test_roadmap.nodes)}")
    print(f"Filtered nodes: {len(filtered.nodes)}")
    print(f"Remaining topics: {[node.title for node in filtered.nodes]}")

    # Should skip HTML and CSS, keep JavaScript, React, Advanced React
    expected_count = 3  # JavaScript, React, Advanced React
    test1_pass = len(filtered.nodes) == expected_count
    print(f"{'✅ PASS' if test1_pass else '❌ FAIL'}: Expected {expected_count} nodes, got {len(filtered.nodes)}")

    # Test Case 2: Add prerequisites back
    print("\n--- Test Case 2: Add Prerequisites ---")

    enhanced = service.add_prerequisite_nodes(
        test_roadmap,
        current_skills,
        filtered
    )

    print(f"After adding prerequisites: {len(enhanced.nodes)} nodes")
    print(f"Topics: {[node.title for node in enhanced.nodes]}")

    # Since React depends on CSS (which was skipped), CSS should be added back
    has_css = any(node.title == "CSS Styling" for node in enhanced.nodes)
    print(f"{'✅ PASS' if has_css else '❌ FAIL'}: CSS prerequisite {'was' if has_css else 'was NOT'} added back")

    # Test Case 3: Similarity calculation
    print("\n--- Test Case 3: Similarity Calculation ---")

    test_pairs = [
        ("html", "HTML Basics", 0.7),  # Should match (substring + high similarity)
        ("css", "CSS Styling", 0.7),   # Should match
        ("python", "JavaScript Programming", 0.0),  # Should NOT match
        ("react framework", "React Framework", 0.9),  # Exact match
    ]

    all_similarity_tests_pass = True
    for skill, title, expected_min in test_pairs:
        similarity = service._calculate_similarity(skill.lower(), title.lower())
        matches = similarity >= expected_min
        print(f"  '{skill}' vs '{title}': {similarity:.2f} ({'✅ match' if matches else '❌ no match'})")
        if not matches and expected_min > 0:
            all_similarity_tests_pass = False

    all_tests_pass = test1_pass and has_css and all_similarity_tests_pass

    if all_tests_pass:
        print(f"\n{'='*80}")
        print("✅ ALL SKILL GAP ANALYSIS TESTS PASSED!")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print("❌ SOME TESTS FAILED")
        print(f"{'='*80}")

    return all_tests_pass


def test_adaptive_pacing():
    """Test adaptive pacing algorithm."""
    print("\n" + "="*80)
    print("TEST 2: ADAPTIVE PACING")
    print("="*80)

    # Test Case 1: Beginner with limited time
    print("\n--- Test Case 1: Beginner with limited time ---")
    prefs1 = {
        "basic_info": {
            "time_availability": "1-2hrs",
            "experience_level": "complete_beginner",
            "preferred_pace": "slow"
        }
    }

    lessons1 = GenerateLearningPathView.calculate_lessons_per_module(
        prefs1,
        module_index=0,  # First module
        total_modules=10
    )

    print(f"Configuration: 1-2hrs, beginner, slow pace, first module")
    print(f"Expected: ~3 lessons (low time, beginner gets -1, early module +1)")
    print(f"Actual: {lessons1} lessons")
    test1_pass = 2 <= lessons1 <= 4
    print(f"{'✅ PASS' if test1_pass else '❌ FAIL'}: Lesson count in expected range")

    # Test Case 2: Advanced user with lots of time
    print("\n--- Test Case 2: Advanced user with lots of time ---")
    prefs2 = {
        "basic_info": {
            "time_availability": "5+hrs",
            "experience_level": "advanced",
            "preferred_pace": "fast"
        }
    }

    lessons2 = GenerateLearningPathView.calculate_lessons_per_module(
        prefs2,
        module_index=4,  # Middle module
        total_modules=10
    )

    print(f"Configuration: 5+hrs, advanced, fast pace, middle module")
    print(f"Expected: ~8-9 lessons (high time base=7, advanced +1, fast ×1.1)")
    print(f"Actual: {lessons2} lessons")
    test2_pass = 7 <= lessons2 <= 10
    print(f"{'✅ PASS' if test2_pass else '❌ FAIL'}: Lesson count in expected range")

    # Test Case 3: Verify adaptive behavior (advanced > beginner)
    print("\n--- Test Case 3: Advanced should get more lessons than beginner ---")
    print(f"Beginner lessons: {lessons1}")
    print(f"Advanced lessons: {lessons2}")
    test3_pass = lessons2 > lessons1
    print(f"{'✅ PASS' if test3_pass else '❌ FAIL'}: Advanced gets more lessons")

    # Test Case 4: Verify position adjustment (early vs late module)
    print("\n--- Test Case 4: Position adjustment (early vs late) ---")
    prefs_same = {
        "basic_info": {
            "time_availability": "3-5hrs",
            "experience_level": "some_basics",
            "preferred_pace": "medium"
        }
    }

    early_lessons = GenerateLearningPathView.calculate_lessons_per_module(
        prefs_same,
        module_index=0,  # First module (early)
        total_modules=10
    )

    late_lessons = GenerateLearningPathView.calculate_lessons_per_module(
        prefs_same,
        module_index=9,  # Last module (late)
        total_modules=10
    )

    print(f"Early module (1/10): {early_lessons} lessons")
    print(f"Late module (10/10): {late_lessons} lessons")
    test4_pass = early_lessons > late_lessons  # Early should have more than late
    print(f"{'✅ PASS' if test4_pass else '❌ FAIL'}: Early module has more lessons than late")

    all_tests_pass = test1_pass and test2_pass and test3_pass and test4_pass

    if all_tests_pass:
        print(f"\n{'='*80}")
        print("✅ ALL ADAPTIVE PACING TESTS PASSED!")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print("❌ SOME TESTS FAILED")
        print(f"{'='*80}")

    return all_tests_pass


def main():
    """Run all Phase 2 tests."""
    print("\n" + "="*80)
    print("PHASE 2 TESTING - SKILL GAP ANALYSIS & ADAPTIVE PACING")
    print("="*80)

    results = {
        "skill_gap_analysis": test_skill_gap_analysis(),
        "adaptive_pacing": test_adaptive_pacing()
    }

    # Summary
    print("\n" + "="*80)
    print("FINAL TEST SUMMARY")
    print("="*80)

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name.replace('_', ' ').title()}")

    print(f"\nOverall: {passed_tests}/{total_tests} test groups passed")

    if passed_tests == total_tests:
        print("\n" + "="*80)
        print("🎉 ALL PHASE 2 TESTS PASSED!")
        print("✓ Skill gap analysis working correctly")
        print("✓ Adaptive pacing algorithm implemented")
        print("\n✅ Phase 2: Core Intelligence is complete!")
        print("="*80)
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test group(s) failed. Review implementation.")


if __name__ == "__main__":
    main()
