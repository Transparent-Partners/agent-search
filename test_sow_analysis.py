#!/usr/bin/env python3
"""
Quick test script for SOW analysis functionality.
Run this directly in your terminal to test the enhanced search.
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from vertex_search import VertexSearchClient


def main():
    """Test SOW analysis functionality."""
    print("🔍 SOW Analysis Test")
    print("=" * 60)
    
    # Initialize client
    try:
        client = VertexSearchClient()
        print(f"✅ Connected to project: {client.project_id}")
        print(f"✅ Using engine: {client.engine_id}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return
    
    # Test 1: How many SOWs are there?
    print("📊 Test 1: Analyzing SOW documents...")
    print("-" * 60)
    try:
        sow_analysis = client.search_and_analyze_sows(query="SOW", page_size=50)
        analysis = sow_analysis['analysis']
        
        print(f"\n✅ Found {analysis['total_sows']} unique SOWs:")
        print()
        
        for sow_key, sow_info in analysis['sows'].items():
            print(f"  📄 {sow_key}: {len(sow_info['documents'])} document(s)")
            print(f"      Primary: {sow_info['primary_title']}")
            if sow_info['documents']:
                first_doc = sow_info['documents'][0]
                if first_doc['link']:
                    print(f"      Link: {first_doc['link']}")
            print()
        
        if analysis['other_documents']:
            print(f"  📋 Other related documents: {len(analysis['other_documents'])}")
            for doc in analysis['other_documents'][:3]:
                print(f"      • {doc['title']}")
            print()
        
        print(f"  📈 Total documents found: {analysis['total_documents']}")
        print()
        
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        print()
    
    # Test 2: Search for specific SOW
    print("📊 Test 2: Searching for CHR_SOW#1...")
    print("-" * 60)
    try:
        results = client.search(query="CHR_SOW#1", page_size=10)
        
        if results:
            print(f"\n✅ Found {len(results)} document(s) for CHR_SOW#1:")
            print()
            
            for i, result in enumerate(results[:5], 1):
                print(f"  {i}. {result.title}")
                if result.uri:
                    print(f"     🔗 {result.uri}")
                if result.content:
                    preview = result.content[:150].replace('\n', ' ')
                    print(f"     📝 {preview}...")
                print()
        else:
            print("❌ No documents found for CHR_SOW#1")
            
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        print()
    
    # Test 3: General search
    print("📊 Test 3: General search for 'Statement of Work'...")
    print("-" * 60)
    try:
        results = client.search(query="Statement of Work", page_size=10)
        
        if results:
            print(f"\n✅ Found {len(results)} document(s):")
            print()
            
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result.title}")
                if result.score:
                    print(f"     Score: {result.score}")
                print()
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        print()
    
    print("=" * 60)
    print("✅ SOW Analysis Test Complete!")


if __name__ == "__main__":
    main()

