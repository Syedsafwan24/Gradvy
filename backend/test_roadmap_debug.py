#!/usr/bin/env python
"""
backend/test_roadmap_debug.py
Quick test script to debug roadmap.sh data structure
Why: Investigate why module names are gibberish instead of meaningful titles
RELEVANT FILES: ml_services/integrations/roadmap_service.py, learning_path_service.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ml_services.integrations.roadmap_service import RoadmapService

def test_roadmap_fetch():
    """Test fetching and parsing roadmap.sh data"""
    print("=" * 80)
    print("TESTING ROADMAP.SH DATA FETCH")
    print("=" * 80)

    service = RoadmapService()

    # Test with web_dev (frontend roadmap)
    print("\n🔍 Fetching 'web_dev' roadmap from roadmap.sh...")
    roadmap = service.fetch_roadmap('web_dev')

    if roadmap:
        print(f"\n✅ Roadmap fetched successfully!")
        print(f"   Title: {roadmap.title}")
        print(f"   Total nodes: {len(roadmap.nodes)}")
        print(f"   First 5 node titles:")
        for i, node in enumerate(roadmap.nodes[:5]):
            print(f"     {i+1}. {node.title}")
            print(f"        ID: {node.id}")
            print(f"        Description: {node.description[:100] if node.description else 'N/A'}...")
    else:
        print("\n❌ Failed to fetch roadmap")

if __name__ == '__main__':
    test_roadmap_fetch()
