"""
API Routes - Thin wrapper around existing RAG engine
"""
from fastapi import APIRouter, HTTPException, Request
from .models import SearchRequest, SearchResponse, ErrorResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

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
    
    This endpoint wraps your existing rag_system/rag_engine.py
    WITHOUT modifying any of your existing code!
    """
    try:
        # Get RAG engine from app state
        if not hasattr(req.app.state, 'rag_engine') or not req.app.state.rag_engine:
            raise HTTPException(
                status_code=500,
                detail="RAG engine not initialized"
            )
        
        rag_engine = req.app.state.rag_engine
        
        logger.info(f"Search query: {request.query[:100]}...")
        
        # Call your EXISTING RAG engine using ask() for full RAG pipeline
        results = rag_engine.ask(
            query=request.query,
            collection_type=request.collection,
            limit=request.limit,
            return_sources=True,
            stream=False,
            use_hybrid=True,
            use_reranking=True,
            extract_citations=True
        )
        
        logger.info(f"Search completed: {len(results.get('sources', []))} sources found")
        
        # Transform to API response format
        sources_list = []
        for src in results.get('sources', []):
            # Map from RAG engine format to API format
            metadata = src.get('metadata', {})
            sources_list.append({
                "content": src.get('full_text', src.get('text', '')),
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
        
        return SearchResponse(
            answer=results.get('answer', 'No answer generated'),
            sources=sources_list,
            metadata={
                "total_searched": results.get('num_sources', 0),
                "query_time": results.get('search_time', 0) + results.get('generation_time', 0),
                "collection": request.collection
            }
        )
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
