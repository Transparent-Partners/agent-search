#!/usr/bin/env python3
"""
Get Answers example using Vertex AI Search API.

This example demonstrates how to generate AI-powered answers
using the REST API answer endpoint.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import vertex_search
sys.path.insert(0, str(Path(__file__).parent.parent))

from vertex_search import VertexSearchClient


def main():
    """Run get answers example."""
    print("🤖 Vertex AI Search - Get Answers Example")
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
    
    # Example queries for answer generation
    queries = [
        "How many SOWs are there?",
        "What is the purpose of CHR_SOW#1?",
        "Can you summarize the Martech Assessment Enablement project?",
        "What are the key deliverables in our SOWs?"
    ]
    
    print("🎯 Testing Answer Generation with REST API")
    print("=" * 60)
    
    for i, query in enumerate(queries, 1):
        print(f"🤖 Query {i}: {query}")
        print("-" * 50)
        
        try:
            # First, perform a search to get query_id
            print("📡 Step 1: Performing search to get query ID...")
            search_results = client.search(query=query, page_size=5)
            
            if search_results:
                print(f"✅ Found {len(search_results)} search results")
                
                # Extract query_id from search results (we'll need to implement this)
                query_id = None  # This would need to be extracted from search response
                
                print("📡 Step 2: Generating answer using REST API...")
                
                # Try to get answer using REST API
                try:
                    answer_response = client.get_answer_rest_api(
                        query=query,
                        query_id=query_id,
                        enable_related_questions=True
                    )
                    
                    print("✅ Answer generated successfully!")
                    print(f"📝 Answer: {answer_response.answer}")
                    
                    if answer_response.related_questions:
                        print("❓ Related Questions:")
                        for j, question in enumerate(answer_response.related_questions, 1):
                            print(f"   {j}. {question}")
                    
                    if answer_response.search_results:
                        print(f"📊 Search Results ({len(answer_response.search_results)}):")
                        for j, result in enumerate(answer_response.search_results[:3], 1):
                            print(f"   {j}. {result.title}")
                            if result.uri:
                                print(f"      Link: {result.uri}")
                    
                except Exception as answer_error:
                    print(f"❌ Answer generation failed: {answer_error}")
                    print("📋 Showing search results instead:")
                    
                    for j, result in enumerate(search_results[:3], 1):
                        print(f"   {j}. {result.title}")
                        if result.uri:
                            print(f"      Link: {result.uri}")
                        if result.content:
                            print(f"      Preview: {result.content[:100]}...")
            else:
                print("❌ No search results found")
                
        except Exception as e:
            print(f"❌ Query failed: {e}")
        
        print("=" * 60)
        print()
    
    print("📋 Final Summary:")
    print("-" * 30)
    print("✅ Tested answer generation with REST API")
    print("📝 Note: This uses the new REST API answer endpoint")
    print("💡 If answers are empty, we may need to investigate the answer endpoint configuration")
    
    print()
    print("✅ Get answers example completed!")


if __name__ == "__main__":
    main()
