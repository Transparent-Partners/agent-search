#!/usr/bin/env python3
"""
Clean debug script to investigate the search response structure.
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from vertex_search import VertexSearchClient
from google.cloud import discoveryengine_v1 as discoveryengine


def debug_search_response():
    """Debug the raw search response structure."""
    print("🔍 Debug: Search Response Structure")
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
    
    # Make a direct search request
    try:
        print("📡 Making search request...")
        
        # Create the search request manually
        request = discoveryengine.SearchRequest(
            serving_config=f"{client.engine_path}/servingConfigs/default_search",
            query="SOW",
            page_size=10,
            query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
                condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO
            ),
            spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
                mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
            ),
            language_code="en-US",
            user_info=discoveryengine.UserInfo(
                time_zone="America/Denver"
            )
        )
        
        print(f"📋 Request serving config: {request.serving_config}")
        print(f"📋 Request query: {request.query}")
        print(f"📋 Request page size: {request.page_size}")
        print()
        
        # Make the API call
        response = client.client.search(request)
        
        print("📊 Response Analysis:")
        print("-" * 40)
        print(f"Response type: {type(response)}")
        print(f"Response dir: {[attr for attr in dir(response) if not attr.startswith('_')]}")
        print()
        
        # Try different ways to access results
        print("🔍 Trying different access methods:")
        
        # Method 1: Direct iteration
        print("1. Direct iteration over response:")
        try:
            results_direct = list(response)
            print(f"   Results count: {len(results_direct)}")
            if results_direct:
                print(f"   First result type: {type(results_direct[0])}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 2: Access pages
        print("2. Accessing pages:")
        try:
            if hasattr(response, 'pages'):
                pages = list(response.pages)
                print(f"   Pages count: {len(pages)}")
                if pages:
                    first_page = pages[0]
                    print(f"   First page type: {type(first_page)}")
                    if hasattr(first_page, 'results'):
                        page_results = list(first_page.results)
                        print(f"   First page results: {len(page_results)}")
                        if page_results:
                            print(f"   First result from page: {type(page_results[0])}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 3: Access results attribute
        print("3. Accessing results attribute:")
        try:
            if hasattr(response, 'results'):
                results_attr = list(response.results)
                print(f"   Results attribute count: {len(results_attr)}")
                if results_attr:
                    print(f"   First result from attr: {type(results_attr[0])}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Check other attributes
        print("\n📊 Other response attributes:")
        for attr in ['total_size', 'attribution_token', 'guided_search_result', 'summary']:
            if hasattr(response, attr):
                value = getattr(response, attr)
                print(f"  {attr}: {value}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Search request failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_search_response()
