"""
API Routes - Thin wrapper around existing RAG engine
Optimized for performance to match monolithic Streamlit version
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from .models import SearchRequest, SearchResponse, ErrorResponse
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import hashlib
import json
import time
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

# Dedicated thread pool executor for RAG operations (reused across requests)
# This is more efficient than asyncio.to_thread which uses a shared pool
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="rag_worker")

# Simple in-memory cache for query results (LRU cache with 100 entries)
_query_cache = {}
_cache_max_size = 100

def _create_cache_key(request: SearchRequest) -> str:
    """Create cache key from request parameters"""
    cache_data = {
        'query': request.query.lower().strip(),
        'collection': request.collection,
        'limit': request.limit,
        'use_hybrid': getattr(request, 'use_hybrid', True),
        'use_reranking': getattr(request, 'use_reranking', True),
        'extract_citations': getattr(request, 'extract_citations', True)
    }
    cache_str = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(cache_str.encode()).hexdigest()

def _construct_courtlistener_url(citation: str) -> str:
    """
    Construct CourtListener URL from citation string
    Format: https://www.courtlistener.com/c/{reporter}/{volume}/{page}/
    """
    if not citation:
        return None
    
    # Try to parse common citation formats
    # Example: "123 U.S. 456" or "456 F.3d 789"
    patterns = [
        (r'(\d+)\s+U\.S\.(?:\s+App\.)?\s+(\d+)', 'us'),
        (r'(\d+)\s+F\.\s*(?:2d|3d|4th)?\s+(\d+)', 'f'),
        (r'(\d+)\s+S\.\s*Ct\.\s+(\d+)', 'sct'),
        (r'(\d+)\s+F\.\s*Supp\.\s*(?:2d|3d)?\s+(\d+)', 'f-supp'),
    ]
    
    for pattern, reporter in patterns:
        match = re.search(pattern, citation, re.IGNORECASE)
        if match:
            volume = match.group(1)
            page = match.group(2)
            return f"https://www.courtlistener.com/c/{reporter}/{volume}/{page}/"
    
    return None

def _transform_sources_optimized(sources: list) -> list:
    """Optimized source transformation - minimize dict lookups"""
    sources_list = []
    MIN_SCORE_THRESHOLD = -0.5  # Filter out results with very negative scores
    
    for src in sources:
        raw_score = src.get('score', 0.0)
        
        # Filter out results with very poor scores (unless it's the only result)
        if raw_score < MIN_SCORE_THRESHOLD and len(sources) > 1:
            continue
        
        # Get metadata - it might be nested or at top level
        metadata = src.get('metadata', {})
        if not isinstance(metadata, dict):
            metadata = {}
        
        # Extract title from multiple possible locations
        title = (
            metadata.get('case_name') or 
            metadata.get('filename') or 
            metadata.get('title') or
            src.get('source') or 
            'Unknown'
        )
        
        # Extract citation from multiple possible fields
        citation = (
            metadata.get('citation') or 
            metadata.get('case_citation') or
            metadata.get('docket_number') or
            metadata.get('citation_string')
        )
        
        # Extract URL from multiple possible fields (PDF links, case URLs, etc.)
        url = (
            metadata.get('url') or 
            metadata.get('case_url') or 
            metadata.get('pdf_url') or 
            metadata.get('download_url') or
            metadata.get('resource_uri') or
            metadata.get('absolute_url')
        )
        
        # If no URL but we have a citation, try to construct CourtListener URL
        if not url and citation:
            url = _construct_courtlistener_url(citation)
        
        # Normalize score to 0-1 range for display (negative scores become 0)
        display_score = max(raw_score, 0.0)
        
        sources_list.append({
            "content": src.get('full_text') or src.get('text', ''),
            "score": display_score,
            "metadata": {
                "title": title,
                "collection": src.get('collection', 'unknown'),
                "court": metadata.get('court') or metadata.get('court_name') or metadata.get('court_string'),
                "date": metadata.get('date') or metadata.get('date_filed') or metadata.get('filing_date') or metadata.get('date_created'),
                "citation": citation,
                "url": url
            },
            # Preserve extracted citations if available
            "citations": src.get('citations', [])
        })
    return sources_list

@router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def search(request: SearchRequest, req: Request):
    """
    Search legal documents using existing RAG engine
    
    PERFORMANCE OPTIMIZED:
    - Dedicated thread pool executor (reused across requests)
    - Query result caching (LRU cache)
    - Optimized data transformation
    - Response compression (handled by FastAPI middleware)
    """
    try:
        # Get RAG engine from app state
        if not hasattr(req.app.state, 'rag_engine') or not req.app.state.rag_engine:
            raise HTTPException(
                status_code=500,
                detail="RAG engine not initialized"
            )
        
        rag_engine = req.app.state.rag_engine
        
        request_start = time.time()
        
        # Check cache first (only for exact query matches)
        cache_key = _create_cache_key(request)
        if cache_key in _query_cache:
            logger.info(f"Cache HIT for query: {request.query[:100]}...")
            cached_result = _query_cache[cache_key]
            # Move to end (LRU behavior)
            _query_cache.pop(cache_key)
            _query_cache[cache_key] = cached_result
            
            # Return cached result with aggressive caching headers for CDN
            response = JSONResponse(content=cached_result.model_dump())
            response.headers["Cache-Control"] = "public, max-age=3600, s-maxage=3600"  # 1 hour CDN cache
            response.headers["ETag"] = f'"{cache_key}"'
            response.headers["Vary"] = "Accept-Encoding"
            response.headers["X-Cache-Status"] = "HIT"  # For debugging
            return response
        
        logger.info(f"Search query: {request.query[:100]}...")
        
        # Use dedicated thread pool executor (more efficient than asyncio.to_thread)
        # This executor is reused across all requests
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            _executor,
            rag_engine.ask,
            request.query,
            request.collection,
            request.limit,
            True,  # return_sources
            False,  # stream
            None,  # filters
            getattr(request, 'use_hybrid', True),
            getattr(request, 'use_reranking', True),
            getattr(request, 'extract_citations', True)
        )
        
        request_time = time.time() - request_start
        
        # Optimized source transformation
        sources_list = _transform_sources_optimized(results.get('sources', []))
        
        # Build response
        response = SearchResponse(
            answer=results.get('answer', 'No answer generated'),
            sources=sources_list,
            metadata={
                "total_searched": results.get('num_sources', 0),
                "query_time": results.get('search_time', 0) + results.get('generation_time', 0),
                "collection": request.collection
            }
        )
        
        # Cache the result (LRU eviction if cache is full)
        if len(_query_cache) >= _cache_max_size:
            # Remove oldest entry (first key)
            oldest_key = next(iter(_query_cache))
            _query_cache.pop(oldest_key)
        _query_cache[cache_key] = response
        
        logger.info(
            f"Search completed: {len(sources_list)} sources found | "
            f"Total time: {request_time:.2f}s | "
            f"Search time: {results.get('search_time', 0):.2f}s | "
            f"Generation time: {results.get('generation_time', 0):.2f}s"
        )
        
        # Add caching headers for CDN (Cloudflare)
        # Cache-Control: public = can be cached by CDN, max-age = browser cache, s-maxage = CDN cache
        # ETag: allows conditional requests (304 Not Modified)
        json_response = JSONResponse(content=response.model_dump())
        json_response.headers["Cache-Control"] = "public, max-age=300, s-maxage=1800"  # 5min browser, 30min CDN
        json_response.headers["ETag"] = f'"{cache_key}"'
        json_response.headers["Vary"] = "Accept-Encoding"
        json_response.headers["X-Cache-Status"] = "MISS"  # For debugging
        
        return json_response
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
