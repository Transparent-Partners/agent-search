#!/usr/bin/env python3
"""
Debug script to investigate the search response structure.
This will help us understand why we're getting 0 results.
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
        
        # Check if results exist
        if hasattr(response, 'results'):
            print(f"✅ Has 'results' attribute: {type(response.results)}")
            print(f"Results length: {len(list(response.results))}")
            
            # Try to iterate through results
            results_list = list(response.results)
            print(f"Results list length: {len(results_list)}")
        
        # Try accessing pages directly
        if hasattr(response, 'pages'):
            print(f"✅ Has 'pages' attribute: {type(response.pages)}")
            pages_list = list(response.pages)
            print(f"Pages length: {len(pages_list)}")
            
            if pages_list:
                first_page = pages_list[0]
                print(f"First page type: {type(first_page)}")
                print(f"First page dir: {[attr for attr in dir(first_page) if not attr.startswith('_')]}")
                
                if hasattr(first_page, 'results'):
                    page_results = list(first_page.results)
                    print(f"First page results length: {len(page_results)}")
                    
                    if page_results:
                        print("\n📄 First result from page:")
                        first_result = page_results[0]
                        print(f"  Result type: {type(first_result)}")
                        print(f"  Result dir: {[attr for attr in dir(first_result) if not attr.startswith('_')]}")
                        
                        if hasattr(first_result, 'document'):
                            doc = first_result.document
                            print(f"  Document type: {type(doc)}")
                            print(f"  Document dir: {[attr for attr in dir(doc) if not attr.startswith('_')]}")
                            
                            # Check for derived_struct_data
                            if hasattr(doc, 'derived_struct_data'):
                                print(f"  ✅ Has derived_struct_data: {type(doc.derived_struct_data)}")
                                derived = doc.derived_struct_data
                                print(f"  Derived data keys: {list(derived.keys()) if hasattr(derived, 'keys') else 'No keys method'}")
                                
                                if 'title' in derived:
                                    print(f"  Title: {derived['title']}")
                                if 'link' in derived:
                                    print(f"  Link: {derived['link']}")
                            else:
                                print(f"  ❌ No derived_struct_data")
        else:
            print("❌ No 'pages' attribute in response")
            
            if results_list:
                print("\n📄 First result analysis:")
                first_result = results_list[0]
                print(f"  Result type: {type(first_result)}")
                print(f"  Result dir: {[attr for attr in dir(first_result) if not attr.startswith('_')]}")
                
                if hasattr(first_result, 'document'):
                    doc = first_result.document
                    print(f"  Document type: {type(doc)}")
                    print(f"  Document dir: {[attr for attr in dir(doc) if not attr.startswith('_')]}")
                    
                    # Check for derived_struct_data
                    if hasattr(doc, 'derived_struct_data'):
                        print(f"  ✅ Has derived_struct_data: {type(doc.derived_struct_data)}")
                        derived = doc.derived_struct_data
                        print(f"  Derived data keys: {list(derived.keys()) if hasattr(derived, 'keys') else 'No keys method'}")
                        
                        if 'title' in derived:
                            print(f"  Title: {derived['title']}")
                        if 'link' in derived:
                            print(f"  Link: {derived['link']}")
                    else:
                        print(f"  ❌ No derived_struct_data")
                        
                    # Check for regular attributes
                    if hasattr(doc, 'title'):
                        print(f"  Document title: {doc.title}")
                    if hasattr(doc, 'uri'):
                        print(f"  Document URI: {doc.uri}")
            else:
                print("❌ No results in the response")
        else:
            print("❌ No 'results' attribute in response")
        
        # Check other response attributes
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


def debug_our_search_method():
    """Debug our custom search method."""
    print("\n🔍 Debug: Our Search Method")
    print("=" * 60)
    
    try:
        client = VertexSearchClient()
        
        print("📡 Calling our search method...")
        results = client.search(query="SOW", page_size=10)
        
        print(f"📊 Our method returned: {len(results)} results")
        
        if results:
            print("\n📄 First result from our method:")
            first_result = results[0]
            print(f"  Title: {first_result.title}")
            print(f"  URI: {first_result.uri}")
            print(f"  Content: {first_result.content[:100]}...")
            print(f"  Score: {first_result.score}")
            print(f"  Metadata keys: {list(first_result.metadata.keys()) if first_result.metadata else 'None'}")
        else:
            print("❌ Our method returned no results")
            
    except Exception as e:
        print(f"❌ Our search method failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_search_response()
    debug_our_search_method()
