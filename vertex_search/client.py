"""
Main client for Vertex AI Search API integration.
"""

import os
import json
import requests
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core import exceptions as gcp_exceptions

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from the project root
    project_root = Path(__file__).parent.parent
    dotenv_path = project_root / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
except ImportError:
    pass  # dotenv not installed, skip

from .models import SearchResult, AnswerResponse, SearchRequest, AnswerRequest
from .session import SessionManager


class VertexSearchClient:
    """Client for interacting with Vertex AI Search API."""
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        engine_id: Optional[str] = None,
        location: str = "global",
        api_version: str = "v1alpha"
    ):
        """
        Initialize the Vertex AI Search client.
        
        Args:
            project_id: Google Cloud project ID (defaults to environment variable)
            engine_id: Vertex AI Search engine ID (defaults to environment variable)
            location: Location of the search engine (default: "global")
            api_version: API version to use (default: "v1alpha")
        """
        self.project_id = project_id or os.getenv("PROJECT_ID", "transparent-agent-dev")
        self.engine_id = engine_id or os.getenv("ENGINE_ID", "chr_project_agent_app_v2")
        self.location = location
        self.api_version = api_version
        
        # Initialize the Discovery Engine client
        self.client = discoveryengine.SearchServiceClient()
        self.conversational_client = discoveryengine.ConversationalSearchServiceClient()
        
        # Session manager for conversational search
        self.session_manager = SessionManager()
        
        # Base URL for API calls
        self.base_url = f"https://discoveryengine.googleapis.com/{api_version}"
        self.engine_path = (
            f"projects/{self.project_id}/locations/{self.location}/"
            f"collections/default_collection/engines/{self.engine_id}"
        )
    
    def _get_access_token(self) -> str:
        """Get access token using gcloud."""
        try:
            result = subprocess.run(['gcloud', 'auth', 'print-access-token'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            raise Exception(f"Failed to get access token: {e}")
    
    def search(
        self,
        query: str,
        page_size: int = 10,
        query_expansion: bool = True,
        spell_correction: bool = True,
        language_code: str = "en-US",
        time_zone: str = "America/Denver",
        user_pseudo_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Perform a basic search query using REST API.
        
        Args:
            query: The search query
            page_size: Number of results to return
            query_expansion: Enable query expansion
            spell_correction: Enable spell correction
            language_code: Language code for the query
            time_zone: User timezone
            user_pseudo_id: Optional user identifier
            session_id: Optional session ID for conversational search
            
        Returns:
            List of SearchResult objects
            
        Raises:
            Exception: If the API call fails
        """
        try:
            # Get access token
            token = self._get_access_token()
            
            # Prepare the REST API request
            url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/collections/default_collection/engines/{self.engine_id}/servingConfigs/default_search:search"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "query": query,
                "pageSize": page_size,
                "queryExpansionSpec": {"condition": "AUTO"} if query_expansion else None,
                "spellCorrectionSpec": {"mode": "AUTO"} if spell_correction else None,
                "languageCode": language_code,
                "userInfo": {
                    "timeZone": time_zone,
                    "userPseudoId": user_pseudo_id
                } if user_pseudo_id else {"timeZone": time_zone}
            }
            
            # Add session if provided
            if session_id:
                data["session"] = session_id
            
            # Make the REST API call
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                raise Exception(f"REST API failed: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # Parse results
            results = []
            for item in result.get('results', []):
                document = item.get('document', {})
                derived_data = document.get('derivedStructData', {})
                
                # Get title
                title = derived_data.get('title', '')
                
                # Get link/URI
                uri = derived_data.get('link', None)
                
                # Extract snippets
                content_parts = []
                for snippet_obj in derived_data.get('snippets', []):
                    if isinstance(snippet_obj, dict) and 'snippet' in snippet_obj:
                        content_parts.append(snippet_obj['snippet'])
                
                content = ' '.join(content_parts) if content_parts else ''
                
                # Get metadata
                metadata = dict(derived_data)
                
                # Get score
                score = None
                rank_signals = item.get('rankSignals', {})
                if 'defaultRank' in rank_signals:
                    score = float(rank_signals['defaultRank'])
                
                search_result = SearchResult(
                    title=title,
                    content=content,
                    uri=uri,
                    metadata=metadata,
                    score=score
                )
                results.append(search_result)
            
            return results
            
        except Exception as e:
            raise Exception(f"Search failed: {e}")
    
    def get_answer_rest_api(
        self,
        query: str,
        query_id: Optional[str] = None,
        session_id: Optional[str] = None,
        enable_related_questions: bool = True
    ) -> AnswerResponse:
        """
        Generate an answer for a query using REST API.
        
        Args:
            query: The query text
            query_id: Optional query ID from previous search
            session_id: Optional session ID for conversational context
            enable_related_questions: Whether to generate related questions
            
        Returns:
            AnswerResponse object
            
        Raises:
            Exception: If the API call fails
        """
        try:
            # Get access token
            token = self._get_access_token()
            
            # Prepare the REST API request for answer generation
            url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/collections/default_collection/engines/{self.engine_id}/servingConfigs/default_search:answer"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "query": {
                    "text": query,
                    "queryId": query_id
                },
                "relatedQuestionsSpec": {
                    "enable": enable_related_questions
                },
                "answerGenerationSpec": {
                    "ignoreAdversarialQuery": True,
                    "ignoreNonAnswerSeekingQuery": False,
                    "ignoreLowRelevantContent": False
                }
            }
            
            # Add session if provided
            if session_id:
                data["session"] = session_id
            
            # Make the REST API call
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                raise Exception(f"REST API answer failed: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # Parse the response
            answer_text = result.get('answer', '')
            related_questions = []
            search_results = []
            
            # Extract related questions
            if 'relatedQuestions' in result:
                related_questions = [q.get('text', '') for q in result['relatedQuestions']]
            
            # Extract search results if available
            if 'searchResults' in result:
                for item in result['searchResults']:
                    document = item.get('document', {})
                    derived_data = document.get('derivedStructData', {})
                    
                    title = derived_data.get('title', '')
                    uri = derived_data.get('link', None)
                    
                    content_parts = []
                    for snippet_obj in derived_data.get('snippets', []):
                        if isinstance(snippet_obj, dict) and 'snippet' in snippet_obj:
                            content_parts.append(snippet_obj['snippet'])
                    
                    content = ' '.join(content_parts) if content_parts else ''
                    
                    metadata = dict(derived_data)
                    
                    score = None
                    rank_signals = item.get('rankSignals', {})
                    if 'defaultRank' in rank_signals:
                        score = float(rank_signals['defaultRank'])
                    
                    search_result = SearchResult(
                        title=title,
                        content=content,
                        uri=uri,
                        metadata=metadata,
                        score=score
                    )
                    search_results.append(search_result)
            
            return AnswerResponse(
                answer=answer_text,
                related_questions=related_questions,
                search_results=search_results,
                session_id=session_id,
                query_id=query_id
            )
            
        except Exception as e:
            raise Exception(f"Answer generation failed: {e}")
    
    def get_answer(
        self,
        query: str,
        query_id: Optional[str] = None,
        session_id: Optional[str] = None,
        enable_related_questions: bool = True
    ) -> AnswerResponse:
        """
        Generate an answer for a query.
        
        Args:
            query: The query text
            query_id: Optional query ID from a previous search
            session_id: Optional session ID for conversational context
            enable_related_questions: Whether to generate related questions
            
        Returns:
            AnswerResponse object
            
        Raises:
            Exception: If the API call fails
        """
        try:
            # Use the conversational search service for answer generation
            request = discoveryengine.AnswerQueryRequest(
                serving_config=f"{self.engine_path}/servingConfigs/default_search",
                query=discoveryengine.Query(
                    text=query,
                    query_id=query_id
                ),
                session=session_id,
                related_questions_spec=discoveryengine.AnswerQueryRequest.RelatedQuestionsSpec(
                    enable=enable_related_questions
                ),
                answer_generation_spec=discoveryengine.AnswerQueryRequest.AnswerGenerationSpec(
                    ignore_adversarial_query=True,
                    ignore_non_answer_seeking_query=False,
                    ignore_low_relevant_content=False
                )
            )
            
            response = self.conversational_client.answer_query(request)
            
            # Parse the response
            answer_text = ""
            related_questions = []
            search_results = []
            
            if hasattr(response, 'answer') and response.answer:
                answer_text = response.answer
                
            if hasattr(response, 'related_questions') and response.related_questions:
                related_questions = [q.text for q in response.related_questions]
            
            if hasattr(response, 'search_results') and response.search_results:
                for result in response.search_results:
                    search_result = SearchResult(
                        title=getattr(result.document, 'title', ''),
                        content=getattr(result.document, 'content', ''),
                        uri=getattr(result.document, 'uri', None),
                        metadata=getattr(result.document, 'struct_data', {}),
                        score=getattr(result, 'score', None)
                    )
                    search_results.append(search_result)
            
            return AnswerResponse(
                answer=answer_text,
                related_questions=related_questions,
                search_results=search_results,
                session_id=session_id,
                query_id=query_id
            )
            
        except gcp_exceptions.GoogleAPIError as e:
            raise Exception(f"Google API error: {e}")
        except Exception as e:
            raise Exception(f"Answer generation failed: {e}")
    
    def search_with_answer(
        self,
        query: str,
        page_size: int = 10,
        enable_related_questions: bool = True,
        user_pseudo_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> AnswerResponse:
        """
        Perform a search and generate an answer in one call.
        
        Args:
            query: The search query
            page_size: Number of search results to use for answer generation
            enable_related_questions: Whether to generate related questions
            user_pseudo_id: Optional user identifier
            session_id: Optional session ID for conversational context
            
        Returns:
            AnswerResponse object with search results and generated answer
        """
        try:
            # First, perform a search to get query_id
            search_results = self.search(
                query=query,
                page_size=page_size,
                user_pseudo_id=user_pseudo_id,
                session_id=session_id
            )
            
            # Extract query_id from search results (this would need to be implemented
            # based on the actual API response structure)
            query_id = None  # This would need to be extracted from the search response
            
            # Generate answer using the query_id
            answer_response = self.get_answer(
                query=query,
                query_id=query_id,
                session_id=session_id,
                enable_related_questions=enable_related_questions
            )
            
            # Add search results to the answer response
            answer_response.search_results = search_results
            
            return answer_response
            
        except Exception as e:
            raise Exception(f"Search with answer failed: {e}")
    
    def conversational_search(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_pseudo_id: Optional[str] = None,
        start_new_session: bool = False
    ) -> AnswerResponse:
        """
        Perform a conversational search with session management.
        
        Args:
            query: The search query
            session_id: Optional existing session ID
            user_pseudo_id: Optional user identifier
            start_new_session: Whether to start a new session
            
        Returns:
            AnswerResponse object with session information
        """
        try:
            # Handle session management
            if start_new_session or session_id is None:
                session_id = self.session_manager.create_session(user_pseudo_id)
            elif session_id and self.session_manager.is_new_session(session_id):
                # Convert new session ID to active session
                clean_session_id = self.session_manager.get_clean_session_id(session_id)
                session_id = clean_session_id
            
            # Perform search with answer
            answer_response = self.search_with_answer(
                query=query,
                user_pseudo_id=user_pseudo_id,
                session_id=session_id
            )
            
            # Update session with conversation turn
            if session_id and answer_response.query_id:
                self.session_manager.update_session(
                    session_id=session_id,
                    query=query,
                    query_id=answer_response.query_id,
                    answer_id=f"answer_{answer_response.query_id}"  # This would be the actual answer ID
                )
            
            answer_response.session_id = session_id
            return answer_response
            
        except Exception as e:
            raise Exception(f"Conversational search failed: {e}")
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Session information dictionary or None if not found
        """
        session_info = self.session_manager.get_session(session_id)
        if session_info:
            return {
                "session_id": session_info.session_id,
                "user_pseudo_id": session_info.user_pseudo_id,
                "state": session_info.state,
                "start_time": session_info.start_time.isoformat() if session_info.start_time else None,
                "end_time": session_info.end_time.isoformat() if session_info.end_time else None,
                "turns": session_info.turns
            }
        return None
    
    def list_sessions(self, user_pseudo_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List sessions.
        
        Args:
            user_pseudo_id: Optional user ID to filter sessions
            
        Returns:
            List of session information dictionaries
        """
        if user_pseudo_id:
            sessions = self.session_manager.list_sessions_for_user(user_pseudo_id)
        else:
            sessions = self.session_manager.list_active_sessions()
        
        return [
            {
                "session_id": session.session_id,
                "user_pseudo_id": session.user_pseudo_id,
                "state": session.state,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "turns": len(session.turns)
            }
            for session in sessions
        ]
    
    def extract_sows_from_results(self, results: List[SearchResult]) -> Dict[str, Any]:
        """
        Extract and analyze SOW information from search results.
        
        Args:
            results: List of SearchResult objects
            
        Returns:
            Dictionary with SOW analysis including count and details
        """
        import re
        
        sows = {}
        other_docs = []
        
        # Pattern to match SOW references in titles
        sow_pattern = re.compile(r'(CHR_)?SOW[_\s#]*([0-9X]+)', re.IGNORECASE)
        
        for result in results:
            title = result.title
            match = sow_pattern.search(title)
            
            if match:
                # Extract SOW number
                sow_num = match.group(2)
                sow_key = f"SOW#{sow_num}"
                
                if sow_key not in sows:
                    sows[sow_key] = {
                        'sow_number': sow_num,
                        'documents': [],
                        'primary_title': title
                    }
                
                sows[sow_key]['documents'].append({
                    'title': title,
                    'link': result.uri,
                    'content': result.content[:200] + '...' if len(result.content) > 200 else result.content,
                    'score': result.score
                })
            else:
                # Document doesn't clearly reference a SOW
                other_docs.append({
                    'title': title,
                    'link': result.uri,
                    'content': result.content[:200] + '...' if len(result.content) > 200 else result.content,
                    'score': result.score
                })
        
        return {
            'total_sows': len(sows),
            'sows': dict(sorted(sows.items())),
            'other_documents': other_docs,
            'total_documents': len(results)
        }
    
    def search_and_analyze_sows(
        self,
        query: str = "SOW",
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Search for SOWs and provide detailed analysis.
        
        Args:
            query: Search query (defaults to "SOW")
            page_size: Number of results to retrieve
            
        Returns:
            Dictionary with SOW analysis and search results
        """
        try:
            # Search for SOW-related documents
            results = self.search(
                query=query,
                page_size=page_size,
                query_expansion=True,
                spell_correction=True
            )
            
            # Analyze the results
            analysis = self.extract_sows_from_results(results)
            
            return {
                'query': query,
                'analysis': analysis,
                'raw_results': results
            }
            
        except Exception as e:
            raise Exception(f"SOW analysis failed: {e}")
