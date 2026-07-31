"""
API Request/Response Models
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional, List

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000, description="Legal search query")
    collection: Literal["both", "contracts", "cases"] = Field("both", description="Which collection to search")
    limit: int = Field(10, ge=1, le=50, description="Number of results")
    use_hybrid: bool = Field(True, description="Use hybrid search (semantic + BM25)")
    use_reranking: bool = Field(True, description="Use cross-encoder reranking")
    extract_citations: bool = Field(True, description="Extract and link citations")

class SourceMetadata(BaseModel):
    title: str
    collection: str
    court: Optional[str] = None
    date: Optional[str] = None
    citation: Optional[str] = None
    url: Optional[str] = None

class Citation(BaseModel):
    type: Optional[str] = None
    text: str
    link: Optional[str] = None
    position: Optional[int] = None

class Source(BaseModel):
    content: str
    score: float
    metadata: SourceMetadata
    citations: List[Citation] = Field(default_factory=list)

class SearchResponse(BaseModel):
    answer: str
    sources: List[Source]
    metadata: dict

class ErrorResponse(BaseModel):
    detail: str
    error_code: str
