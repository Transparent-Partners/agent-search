#!/usr/bin/env python3
"""
Search example using Vertex AI Search API.

This example demonstrates how to perform search queries
with SOW analysis and document discovery.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import vertex_search
sys.path.insert(0, str(Path(__file__).parent.parent))

from vertex_search import VertexSearchClient


def main():
    """Run search example."""
    print("🔍 Vertex AI Search - Search Example")
    print("=" * 60)
    
    # Initialize the client
    try:
        client = VertexSearchClient()
        print(f"✅ Connected to project: {client.project_id}")
        print(f"✅ Using engine: {client.engine_id}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        print("Make sure you have authenticated with: gcloud auth application-default login")
        return
    
    # Simulate a conversation
    conversation = [
        {
            "query": "How many SOWs are there?",
            "description": "Initial question about SOW count"
        },
        {
            "query": "Can you summarize CHR_SOW#1_Martech Assessment Enablement_11.15.24?",
            "description": "Follow-up requesting specific SOW summary"
        },
        {
            "query": "Can you summarize another SOW?",
            "description": "Follow-up requesting another SOW summary"
        }
    ]
    
    session_id = None
    user_pseudo_id = "demo_user"
    
    print("🎯 Starting search session...")
    print(f"👤 User: {user_pseudo_id}")
    print()
    
    for i, turn in enumerate(conversation, 1):
        print(f"💬 Turn {i}: {turn['description']}")
        print(f"❓ Query: {turn['query']}")
        print("-" * 50)
        
        try:
            # Perform search based on the query type
            if i == 1 and "how many" in turn['query'].lower():
                # First question: "How many SOWs are there?"
                print("📊 Analyzing SOW documents...")
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
                    print()
                
            elif "summarize" in turn['query'].lower() and "CHR_SOW" in turn['query']:
                # Second question: Summarize specific SOW
                print("🔍 Searching for specific SOW...")
                # Extract SOW reference from query
                import re
                sow_match = re.search(r'CHR_SOW#?(\d+)', turn['query'])
                if sow_match:
                    sow_num = sow_match.group(1)
                    search_query = f"CHR_SOW#{sow_num}"
                else:
                    search_query = turn['query']
                
                results = client.search(query=search_query, page_size=10)
                
                if results:
                    print(f"\n📄 Found {len(results)} document(s) related to this SOW:")
                    print()
                    
                    for j, result in enumerate(results[:5], 1):
                        print(f"  {j}. {result.title}")
                        if result.uri:
                            print(f"     Link: {result.uri}")
                        if result.content:
                            print(f"     Preview: {result.content[:150]}...")
                        print()
                else:
                    print("❌ No documents found for this SOW")
                    
            elif "summarize another" in turn['query'].lower():
                # Third question: Summarize another SOW
                print("📊 Listing available SOWs...")
                sow_analysis = client.search_and_analyze_sows(query="SOW", page_size=50)
                
                analysis = sow_analysis['analysis']
                print(f"\n📋 Available SOWs ({analysis['total_sows']} total):")
                print()
                
                for sow_key, sow_info in analysis['sows'].items():
                    print(f"  • {sow_key}: {sow_info['primary_title']}")
                    if sow_info['documents']:
                        first_doc = sow_info['documents'][0]
                        if first_doc['link']:
                            print(f"    🔗 {first_doc['link']}")
                    print()
                
                print("💡 Tip: Ask 'Can you summarize CHR_SOW#X?' with a specific number")
                print()
            else:
                # Generic search
                results = client.search(query=turn['query'], page_size=10)
                
                if results:
                    print(f"\n📊 Search Results ({len(results)}):")
                    for j, result in enumerate(results[:5], 1):
                        print(f"  {j}. {result.title}")
                        if result.uri:
                            print(f"     🔗 {result.uri}")
                        if result.content:
                            print(f"     {result.content[:100]}...")
                        print()
                else:
                    print("❌ No results found")
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
        
        print("=" * 60)
        print()
    
    # Display final summary
    print("📋 Final Summary:")
    print("-" * 30)
    print(f"✅ Processed {len(conversation)} queries successfully")
    print(f"👤 User: {user_pseudo_id}")
    print("📝 Note: Using single-turn search with answer generation")
    print("💡 For multi-turn conversations, contact Google Support for allowlisting")
    
    print()
    print("✅ Search example completed!")


if __name__ == "__main__":
    main()
