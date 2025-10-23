#!/usr/bin/env python3
"""
Search with answer generation example using Vertex AI Search API.

This example demonstrates how to perform search queries and generate
AI-powered answers based on the search results.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import vertex_search
sys.path.insert(0, str(Path(__file__).parent.parent))

from vertex_search import VertexSearchClient


def main():
    """Run search with answer example."""
    print("🤖 Vertex AI Search - Search with Answer Example")
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
    
    # Example queries that benefit from answer generation
    queries = [
        "What are the benefits of using Google Cloud Platform?",
        "How can I optimize my machine learning models?",
        "What are the best practices for data security in the cloud?",
        "Explain the difference between supervised and unsupervised learning"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"🤖 Query {i}: {query}")
        print("-" * 50)
        
        try:
            # Perform search with answer generation
            answer_response = client.search_with_answer(
                query=query,
                page_size=5,
                enable_related_questions=True
            )
            
            # Display the generated answer
            print("📝 Generated Answer:")
            print(f"   {answer_response.answer}")
            print()
            
            # Display related questions if available
            if answer_response.related_questions:
                print("❓ Related Questions:")
                for j, question in enumerate(answer_response.related_questions, 1):
                    print(f"   {j}. {question}")
                print()
            
            # Display search results used for answer generation
            if answer_response.search_results:
                print(f"📊 Search Results ({len(answer_response.search_results)}):")
                for j, result in enumerate(answer_response.search_results[:3], 1):  # Show top 3
                    print(f"   {j}. {result.title}")
                    print(f"      Score: {result.score}")
                    print(f"      Content: {result.content[:80]}...")
                    print()
            
            # Display session information if available
            if answer_response.session_id:
                print(f"🔗 Session ID: {answer_response.session_id}")
            
        except Exception as e:
            print(f"❌ Search with answer failed: {e}")
        
        print("=" * 60)
        print()
    
    print("✅ Search with answer example completed!")


if __name__ == "__main__":
    main()
