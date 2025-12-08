"""
API Request/Response Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class SearchRequest(BaseModel):
    query: str = Field(..., description="Legal search query")
    collection: str = Field("both", description="Which collection to search")
    limit: int = Field(10, ge=1, le=50, description="Number of results")
    use_hybrid: Optional[bool] = Field(True, description="Use hybrid search (semantic + BM25)")
    use_reranking: Optional[bool] = Field(True, description="Use cross-encoder reranking")
    extract_citations: Optional[bool] = Field(True, description="Extract and link citations")

class SourceMetadata(BaseModel):
    title: str
    collection: str
    court: Optional[str] = None
    date: Optional[str] = None
    citation: Optional[str] = None
    url: Optional[str] = None

class Source(BaseModel):
    content: str
    score: float
    metadata: SourceMetadata

class SearchResponse(BaseModel):
    answer: str
    sources: List[Source]
    metadata: dict

class ErrorResponse(BaseModel):
    detail: str
    error_code: str
