"""
API Routes - Thin wrapper around existing RAG engine
Optimized for performance to match monolithic Streamlit version
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from .models import SearchRequest, SearchResponse, ErrorResponse
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import hashlib
import json
import time

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

def _transform_sources_optimized(sources: list) -> list:
    """Optimized source transformation - minimize dict lookups"""
    sources_list = []
    for src in sources:
        metadata = src.get('metadata', {})
        sources_list.append({
            "content": src.get('full_text') or src.get('text', ''),
            "score": src.get('score', 0.0),
            "metadata": {
                "title": src.get('source', 'Unknown'),
                "collection": src.get('collection', 'unknown'),
                "court": metadata.get('court'),
                "date": metadata.get('date'),
                "citation": metadata.get('citation'),
                "url": metadata.get('url')
            }
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
            return cached_result
        
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
        
        return response
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
