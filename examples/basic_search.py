#!/usr/bin/env python3
"""
Basic search example using Vertex AI Search API.

This example demonstrates how to perform simple search queries
without answer generation.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import vertex_search
sys.path.insert(0, str(Path(__file__).parent.parent))

from vertex_search import VertexSearchClient


def main():
    """Run basic search example."""
    print("🔍 Vertex AI Search - Basic Search Example")
    print("=" * 50)
    
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
    
    # Example queries
    queries = [
        "What is machine learning?",
        "How does Google Cloud work?",
        "Best practices for data analysis"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"🔍 Query {i}: {query}")
        print("-" * 40)
        
        try:
            # Perform search
            results = client.search(
                query=query,
                page_size=5,
                query_expansion=True,
                spell_correction=True
            )
            
            if results:
                print(f"📊 Found {len(results)} results:")
                for j, result in enumerate(results, 1):
                    print(f"  {j}. {result.title}")
                    print(f"     Score: {result.score}")
                    print(f"     Content: {result.content[:100]}...")
                    if result.uri:
                        print(f"     URI: {result.uri}")
                    print()
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
        
        print()
    
    print("✅ Basic search example completed!")


if __name__ == "__main__":
    main()
