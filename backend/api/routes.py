"""
API Routes - Thin wrapper around existing RAG engine
Optimized for performance to match monolithic Streamlit version
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from auth import models as auth_models, security
from auth.database import get_db
from limiter import limiter
from .models import SearchRequest, SearchResponse, ErrorResponse
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import time
import re

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
    # Example: "123 U.S. 456" or "456 F.3d 789" or "357 F.3d 1256"
    patterns = [
        (r'(\d+)\s+U\.S\.(?:\s+App\.)?\s+(\d+)', 'us'),
        (r'(\d+)\s+F\.\s*(?:2d|3d|4th)?\s+(\d+)', 'f'),  # Handles F.2d, F.3d, F.4th
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

def _transform_sources_optimized(sources: list, query: str = "") -> list:
    """Optimized source transformation - minimize dict lookups"""
    sources_list = []
    MIN_SCORE_THRESHOLD = -0.5  # Filter out results with very negative scores

    # Detect state in query for result boosting
    state_keywords = {
        'florida': ['florida', 'fl ', 'fl.', 'fla.', 'fla ', '1st dca', '2d dca', '3d dca', '4th dca', '5th dca', 'fla.'],
        'california': ['california', 'ca ', 'cal.', 'cal '],
        'new york': ['new york', 'ny ', 'n.y.'],
        'texas': ['texas', 'tx ', 'tx.'],
    }
    detected_state = None
    query_lower = query.lower() if query else ""
    for state, keywords in state_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            detected_state = state
            break

    # Improved filtering: remove truly off-topic results
    # This improves search relevance per our core principles
    query_keywords = set(query.lower().split()) if query else set()

    # Boost results for SaaS/software-specific queries
    # This improves search relevance when query mentions specific contract types
    is_saas_query = any(term in query_lower for term in ['saas', 'software as a service', 'software contract', 'software license'])
    is_contract_query = any(term in query_lower for term in ['contract', 'agreement', 'indemnity', 'indemnification', 'warranty'])

    for src in sources:
        raw_score = src.get('score', 0.0)

        # Filter out results with very poor scores (unless it's the only result)
        if raw_score < MIN_SCORE_THRESHOLD and len(sources) > 1:
            continue

        # Additional relevance check: if query has specific keywords, check if result contains them
        # This improves search relevance by filtering truly off-topic results
        if query_keywords and len(query_keywords) > 2:  # Only if query has enough keywords
            content_lower = (src.get('full_text') or src.get('text', '')).lower()
            metadata_lower = str(src.get('metadata', {})).lower()

            # Count how many query keywords appear in the result
            keyword_matches = sum(1 for keyword in query_keywords if keyword in content_lower or keyword in metadata_lower)
            keyword_ratio = keyword_matches / len(query_keywords)

            # If less than 20% of keywords match and score is low, filter it out
            if keyword_ratio < 0.2 and raw_score < 0.1 and len(sources) > 2:
                continue

        # Get metadata - it might be nested or at top level
        metadata = src.get('metadata', {})
        if not isinstance(metadata, dict):
            metadata = {}

        # Extract court before relevance boosting so jurisdiction-specific queries
        # can safely use it. Full text fallback extraction happens below.
        court = (
            metadata.get('court') or
            src.get('court') or
            metadata.get('court_name') or
            src.get('court_name') or
            metadata.get('court_string') or
            src.get('court_string') or
            metadata.get('jurisdiction') or
            src.get('jurisdiction') or
            None
        )

        # Extract title from multiple possible locations (check both metadata and top-level)
        title = (
            metadata.get('case_name') or
            src.get('case_name') or
            metadata.get('title') or
            src.get('title') or
            metadata.get('filename') or
            src.get('filename') or
            metadata.get('name') or
            src.get('name') or
            src.get('source') or
            None
        )

        # If no title in metadata, try to extract from text content
        if not title or title == 'Unknown':
            content = src.get('full_text') or src.get('text', '')
            if content:
                # First, try to extract case name that appears before a citation
                # Pattern: Case name followed by citation (e.g., "Hickson Corp. v. N. Crossarm Co., 357 F.3d 1256")
                case_with_citation = re.search(
                    r'([A-Z][^,]{10,120}?)\s*,\s*\d+\s+(?:F\.\s*(?:2d|3d|4th)?|U\.S\.|S\.\s*Ct\.|F\.\s*Supp\.)\s+\d+',
                    content[:500],
                    re.IGNORECASE
                )
                if case_with_citation:
                    potential_title = case_with_citation.group(1).strip()
                    # Clean up: remove trailing punctuation, ensure it looks like a case name
                    potential_title = re.sub(r'[.,;]+$', '', potential_title)
                    if len(potential_title) > 10 and len(potential_title) < 150:
                        title = potential_title

                # If that didn't work, look for case name patterns (e.g., "Plaintiff v. Defendant")
                if not title or title == 'Unknown':
                    case_name_match = re.search(
                        r'([A-Z][^.,]{5,60}?)\s+(?:v\.?|vs\.?|versus)\s+([A-Z][^.,]{5,60}?)',
                        content[:500],
                        re.IGNORECASE
                    )
                    if case_name_match:
                        title = f"{case_name_match.group(1).strip()} v. {case_name_match.group(2).strip()}"

                # If still no title, try to find a title-like line
                if not title or title == 'Unknown':
                    lines = content[:800].split('\n')
                    for line in lines[:10]:  # Check first 10 lines
                        line = line.strip()
                        # Skip very short lines, lines that are all caps (often headers), and lines with citations
                        if (len(line) > 15 and len(line) < 250 and
                            not line.isupper() and
                            not re.search(r'\d+\s+(?:U\.S\.|F\.\s*(?:2d|3d|4th)?|S\.\s*Ct\.)', line, re.IGNORECASE)):
                            # Check if it looks like a case name or document title
                            if re.search(r'[A-Z][a-z]+', line):  # Has mixed case
                                title = line
                                break

        # If still no title, try to clean up filename
        if not title or title == 'Unknown':
            filename = metadata.get('filename') or src.get('filename') or src.get('source')
            if filename:
                # Clean up filename: remove extensions, underscores, dates
                title = filename
                # Remove common file extensions
                title = re.sub(r'\.(pdf|txt|docx?)$', '', title, flags=re.IGNORECASE)
                # Replace underscores and hyphens with spaces
                title = re.sub(r'[_-]', ' ', title)
                # Remove date patterns (YYYYMMDD, YYYY-MM-DD, etc.)
                title = re.sub(r'\d{4}[-_]?\d{2}[-_]?\d{2}', '', title)
                # Remove common prefixes like "EX-99.1_", "8-K_", etc.
                title = re.sub(r'^(?:EX-\d+\.\d+_|8-K_|EX-\d+_)', '', title, flags=re.IGNORECASE)
                # Clean up multiple spaces
                title = re.sub(r'\s+', ' ', title).strip()
                # Capitalize first letter of each word for readability
                if title:
                    title = ' '.join(word.capitalize() if word.islower() else word for word in title.split())

        # Final fallback
        if not title:
            title = 'Unknown'

        # Extract ALL citations from text (not just the first one)
        # This improves citation usefulness per our core principles
        all_citations = []
        content = src.get('full_text') or src.get('text', '')

        # First, check metadata for citation
        citation = (
            metadata.get('citation') or
            src.get('citation') or
            metadata.get('case_citation') or
            src.get('case_citation') or
            metadata.get('citation_string') or
            src.get('citation_string') or
            None
        )

        if citation:
            all_citations.append(citation)

        # Extract all citations from text content (up to first 3000 chars for performance)
        if content:
            # Comprehensive citation patterns
            citation_patterns = [
                # Federal Reporter with series (F.2d, F.3d, F.4th) - handles "357 F.3d 1256"
                r'\d+\s+F\.\s*(?:2d|3d|4th)?\s+\d+',
                # U.S. Reports
                r'\d+\s+U\.S\.(?:\s+App\.)?\s+\d+',
                # Supreme Court
                r'\d+\s+S\.\s*Ct\.\s+\d+',
                # Federal Supplement
                r'\d+\s+F\.\s*Supp\.\s*(?:2d|3d)?\s+\d+',
                # State reporters
                r'\d+\s+(?:Cal\.|Cal\.\s*App\.|Cal\.\s*Rptr\.)\s+\d+',  # California
                r'\d+\s+(?:N\.Y\.|N\.Y\.\s*App\.)\s+\d+',  # New York
                r'\d+\s+(?:Del\.|Del\.\s*Ch\.)\s+\d+',  # Delaware
                r'\d+\s+(?:Fla\.|Fla\.\s*App\.)\s+\d+',  # Florida
                r'\d+\s+(?:Tex\.|Tex\.\s*App\.)\s+\d+',  # Texas
            ]

            # Find all citations in the text
            found_citations = set()  # Use set to avoid duplicates
            for pattern in citation_patterns:
                matches = re.finditer(pattern, content[:3000], re.IGNORECASE)
                for match in matches:
                    cit = match.group(0).strip()
                    # Clean up citation (remove extra spaces)
                    cit = re.sub(r'\s+', ' ', cit)
                    if cit not in found_citations:
                        found_citations.add(cit)
                        all_citations.append(cit)

            # If we found citations, use the first one as primary, but keep all
            if all_citations and not citation:
                citation = all_citations[0]

        # Extract URL from multiple possible fields (PDF links, case URLs, etc.)
        url = (
            metadata.get('url') or
            src.get('url') or
            metadata.get('case_url') or
            src.get('case_url') or
            metadata.get('pdf_url') or
            src.get('pdf_url') or
            metadata.get('download_url') or
            src.get('download_url') or
            metadata.get('resource_uri') or
            src.get('resource_uri') or
            metadata.get('absolute_url') or
            src.get('absolute_url') or
            metadata.get('link') or
            src.get('link') or
            None
        )

        # If no URL but we have a citation, try to construct CourtListener URL
        if not url and citation:
            url = _construct_courtlistener_url(citation)

        # Cross-encoder scores are not probabilities. Clamp the legacy display
        # value to the API's documented [0, 1] range before applying boosts.
        display_score = min(max(float(raw_score), 0.0), 1.0)
        if detected_state:
            # Check if result is state-specific
            content_lower = (src.get('full_text') or src.get('text', '')).lower()
            metadata_lower = str(metadata).lower()
            court_lower = str(court).lower() if court else ""

            # Boost if state keywords found in content, metadata, or court
            state_boost = 0.0
            for keyword in state_keywords.get(detected_state, []):
                if keyword in content_lower or keyword in metadata_lower or keyword in court_lower:
                    state_boost = 0.15  # 15% boost for state-specific results
                    break

            # Also check for state court patterns
            if detected_state == 'florida' and ('fla.' in court_lower or 'dca' in court_lower or 'florida' in court_lower):
                state_boost = 0.15
            elif detected_state == 'california' and ('cal.' in court_lower or 'california' in court_lower):
                state_boost = 0.15
            elif detected_state == 'new york' and ('n.y.' in court_lower or 'new york' in court_lower):
                state_boost = 0.15
            elif detected_state == 'texas' and ('tex.' in court_lower or 'texas' in court_lower):
                state_boost = 0.15

            display_score = min(display_score + state_boost, 1.0)  # Cap at 1.0

        # Boost for SaaS/software contract queries
        if is_saas_query or is_contract_query:
            content_lower = (src.get('full_text') or src.get('text', '')).lower()
            metadata_lower = str(metadata).lower()

            # Check for SaaS/software-related terms
            saas_terms = ['saas', 'software as a service', 'software license', 'subscription', 'software agreement']
            contract_terms = ['contract', 'agreement', 'indemnity', 'indemnification', 'warranty']

            contract_boost = 0.0
            if is_saas_query:
                # Boost if result contains SaaS-related terms
                if any(term in content_lower or term in metadata_lower for term in saas_terms):
                    contract_boost = 0.2  # 20% boost for SaaS-specific results
            elif is_contract_query:
                # Boost if result contains contract-related terms
                if any(term in content_lower or term in metadata_lower for term in contract_terms):
                    contract_boost = 0.1  # 10% boost for contract-related results

            display_score = min(display_score + contract_boost, 1.0)  # Cap at 1.0

        # If no court in metadata, try to extract from text (e.g., "11th Cir.", "Fla. 1st DCA")
        if not court:
            content = src.get('full_text') or src.get('text', '')
            if content:
                # Look for court patterns near citations (e.g., "(11th Cir. 2004)")
                court_patterns = [
                    r'\((\d+(?:st|nd|rd|th)?\s*(?:Cir\.|D\.C\.|D\.\s*C\.))',  # "11th Cir.", "1st D.C."
                    r'\((Fla\.\s*(?:1st|2d|3d|4th|5th)?\s*DCA?)',  # "Fla. 1st DCA"
                    r'\((Cal\.\s*(?:App\.|Sup\.\s*Ct\.))',  # "Cal. App."
                    r'\((N\.Y\.\s*(?:App\.|Sup\.\s*Ct\.))',  # "N.Y. App."
                ]
                for pattern in court_patterns:
                    court_match = re.search(pattern, content[:1000], re.IGNORECASE)
                    if court_match:
                        court = court_match.group(1).strip()
                        break

        # Extract date from multiple possible fields
        date = (
            metadata.get('date') or
            src.get('date') or
            metadata.get('date_filed') or
            src.get('date_filed') or
            metadata.get('filing_date') or
            src.get('filing_date') or
            metadata.get('date_created') or
            src.get('date_created') or
            metadata.get('date_decided') or
            src.get('date_decided') or
            None
        )

        # If no date in metadata, try to extract from text (year in parentheses near citation)
        if not date:
            content = src.get('full_text') or src.get('text', '')
            if content:
                # Look for year pattern near citation (e.g., "(11th Cir. 2004)")
                year_match = re.search(r'\([^)]*(?:19|20)\d{2}\)', content[:1000])
                if year_match:
                    year = re.search(r'(19|20)\d{2}', year_match.group(0))
                    if year:
                        date = year.group(0)

        sources_list.append({
            "content": src.get('full_text') or src.get('text', ''),
            "score": display_score,
            "metadata": {
                "title": title if title != 'Unknown' else (src.get('source') or 'Unknown'),
                "collection": src.get('collection') or metadata.get('collection', 'unknown'),
                "court": court,
                "date": date,
                "citation": citation,
                "url": url
            },
            # Preserve extracted citations if available
            "citations": src.get('citations', []),
            # Store raw score for sorting
            "_sort_score": display_score
        })

    # Sort by boosted score (state-specific results first)
    sources_list.sort(key=lambda x: x.get('_sort_score', 0), reverse=True)

    # Remove internal sort key before returning
    for src in sources_list:
        src.pop('_sort_score', None)

    return sources_list

def _search_response(response: SearchResponse, cache_status: str) -> JSONResponse:
    """Build a response that browsers and shared CDNs must not persist."""
    json_response = JSONResponse(content=response.model_dump())
    json_response.headers["Cache-Control"] = "private, no-store"
    json_response.headers["Pragma"] = "no-cache"
    json_response.headers["X-Cache-Status"] = cache_status
    return json_response


def _record_search(
    db: Session,
    user: auth_models.User,
    request: SearchRequest,
    result_count: int,
) -> None:
    db.add(
        auth_models.SearchHistory(
            user_id=user.id,
            query=request.query,
            collection=request.collection,
            result_count=result_count,
        )
    )
    db.commit()


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        403: {"description": "Free search limit reached"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
@limiter.limit("20/minute")
async def search(
    search_request: SearchRequest,
    request: Request,
    current_user: auth_models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
):
    """Run an authenticated legal search and account for it server-side."""
    reserved = False
    try:
        if not getattr(request.app.state, "rag_engine", None):
            raise HTTPException(status_code=500, detail="RAG engine not initialized")

        allowed, searches_remaining = security.reserve_search(db, current_user)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Free search limit reached. Upgrade to Pro for unlimited searches!",
            )
        reserved = current_user.tier == "free"

        rag_engine = request.app.state.rag_engine
        request_start = time.time()
        cache_key = _create_cache_key(search_request)

        if cache_key in _query_cache:
            logger.info("Search cache hit")
            response = _query_cache.pop(cache_key)
            _query_cache[cache_key] = response
            response.metadata["searches_remaining"] = searches_remaining
            _record_search(db, current_user, search_request, len(response.sources))
            return _search_response(response, "HIT")

        logger.info("Executing legal search")
        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            _executor,
            rag_engine.ask,
            search_request.query,
            search_request.collection,
            search_request.limit,
            True,
            False,
            None,
            search_request.use_hybrid,
            search_request.use_reranking,
            search_request.extract_citations,
        )

        request_time = time.time() - request_start
        sources_list = _transform_sources_optimized(results.get("sources", []), search_request.query)
        response = SearchResponse(
            answer=results.get("answer", "No answer generated"),
            sources=sources_list,
            metadata={
                "total_searched": results.get("num_sources", 0),
                "query_time": results.get("search_time", 0) + results.get("generation_time", 0),
                "collection": search_request.collection,
                "searches_remaining": searches_remaining,
            },
        )

        if len(_query_cache) >= _cache_max_size:
            _query_cache.pop(next(iter(_query_cache)))
        _query_cache[cache_key] = response
        _record_search(db, current_user, search_request, len(sources_list))

        logger.info(
            "Search completed: %s sources | total %.2fs | search %.2fs | generation %.2fs",
            len(sources_list),
            request_time,
            results.get("search_time", 0),
            results.get("generation_time", 0),
        )
        return _search_response(response, "MISS")

    except HTTPException:
        if reserved:
            db.rollback()
            security.refund_search(db, current_user)
        raise
    except Exception:
        db.rollback()
        if reserved:
            try:
                security.refund_search(db, current_user)
            except Exception:
                logger.exception("Failed to refund reserved search for user_id=%s", current_user.id)
        logger.exception("Search failed for user_id=%s", current_user.id)
        raise HTTPException(status_code=500, detail="Search failed. Please try again.")
