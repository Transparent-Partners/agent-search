#!/usr/bin/env python3
"""
Test using REST API directly (like curl) to see if we get results.
"""

import requests
import subprocess
import json
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from vertex_search import VertexSearchClient


def get_access_token():
    """Get access token using gcloud."""
    try:
        result = subprocess.run(['gcloud', 'auth', 'print-access-token'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Failed to get access token: {e}")
        return None


def test_rest_api():
    """Test the REST API directly like curl."""
    print("🔍 Testing REST API (like curl)")
    print("=" * 60)
    
    # Get access token
    token = get_access_token()
    if not token:
        return
    
    print("✅ Got access token")
    
    # Prepare the request
    url = "https://discoveryengine.googleapis.com/v1alpha/projects/622273141210/locations/global/collections/default_collection/engines/checkers_1761176786564/servingConfigs/default_search:search"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "query": "SOW",
        "pageSize": 10,
        "queryExpansionSpec": {"condition": "AUTO"},
        "spellCorrectionSpec": {"mode": "AUTO"},
        "languageCode": "en-US",
        "userInfo": {"timeZone": "America/Denver"}
    }
    
    print(f"📡 Making REST API request to: {url}")
    print(f"📋 Request data: {json.dumps(data, indent=2)}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ REST API Success!")
            print(f"📊 Total size: {result.get('totalSize', 'N/A')}")
            print(f"📊 Results count: {len(result.get('results', []))}")
            print(f"📊 Attribution token: {result.get('attributionToken', 'N/A')[:50]}...")
            
            if result.get('results'):
                print("\n📄 First few results:")
                for i, res in enumerate(result['results'][:3], 1):
                    doc = res.get('document', {})
                    derived = doc.get('derivedStructData', {})
                    title = derived.get('title', 'No title')
                    link = derived.get('link', 'No link')
                    print(f"  {i}. {title}")
                    print(f"     Link: {link}")
                    print()
        else:
            print(f"❌ REST API failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ REST API request failed: {e}")
        import traceback
        traceback.print_exc()


def compare_with_grpc():
    """Compare with gRPC results."""
    print("\n🔍 Comparing with gRPC API")
    print("=" * 60)
    
    try:
        client = VertexSearchClient()
        results = client.search(query="SOW", page_size=10)
        print(f"📊 gRPC results count: {len(results)}")
        
        if results:
            print("📄 gRPC results:")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result.title}")
                print(f"     Link: {result.uri}")
                print()
        else:
            print("❌ No gRPC results")
            
    except Exception as e:
        print(f"❌ gRPC failed: {e}")


if __name__ == "__main__":
    test_rest_api()
    compare_with_grpc()
