"""
Advanced Query Handler
Handles query preprocessing, routing, and result formatting
"""

import re
from typing import Dict, List
from .rag_engine import LegalRAGEngine

class QueryHandler:
    """Advanced query handling and routing"""
    
    def __init__(self, rag_engine: LegalRAGEngine):
        """
        Initialize query handler
        
        Args:
            rag_engine: Initialized RAG engine
        """
        self.engine = rag_engine
        
        # Query type patterns
        self.query_patterns = {
            'statute_limitations': r'statute of limitations',
            'contract': r'contract|agreement|indemnification|warranty',
            'tort': r'negligence|liability|damages|injury',
            'property': r'property|landlord|tenant|lease|eviction',
            'employment': r'employment|discrimination|wrongful termination',
        }
    
    def classify_query(self, query: str) -> str:
        """
        Classify query type
        
        Args:
            query: User query
        
        Returns:
            Query type
        """
        query_lower = query.lower()
        
        for query_type, pattern in self.query_patterns.items():
            if re.search(pattern, query_lower):
                return query_type
        
        return 'general'
    
    def extract_jurisdiction(self, query: str) -> str:
        """
        Extract jurisdiction from query
        
        Args:
            query: User query
        
        Returns:
            Jurisdiction or None
        """
        # Common jurisdiction patterns
        jurisdictions = {
            'california': r'california|ca\b',
            'new york': r'new york|ny\b',
            'texas': r'texas|tx\b',
            'florida': r'florida|fl\b',
            'federal': r'federal|circuit\b',
        }
        
        query_lower = query.lower()
        
        for jurisdiction, pattern in jurisdictions.items():
            if re.search(pattern, query_lower):
                return jurisdiction
        
        return None
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess and enhance query with legal term expansion
        
        Args:
            query: Raw user query
        
        Returns:
            Processed query with expanded terms
        """
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Expand common legal abbreviations
        abbreviations = {
            'K': 'contract',
            'P': 'plaintiff',
            'D': 'defendant',
            'SOL': 'statute of limitations',
            'MSJ': 'motion for summary judgment',
            'MTD': 'motion to dismiss',
            'MTS': 'motion to suppress',
            'MTC': 'motion to compel',
            'SJ': 'summary judgment',
            'DJ': 'declaratory judgment',
            'PI': 'preliminary injunction',
            'TRO': 'temporary restraining order',
            'FRCP': 'federal rules of civil procedure',
            'FRE': 'federal rules of evidence',
        }
        
        for abbr, full in abbreviations.items():
            query = re.sub(rf'\b{abbr}\b', full, query, flags=re.IGNORECASE)
        
        # Expand legal term synonyms (add common alternatives)
        legal_synonyms = {
            r'\bmotion to suppress\b': 'motion to suppress exclusionary rule fourth amendment',
            r'\bconsent search\b': 'consent search warrantless search fourth amendment',
            r'\bbreach of contract\b': 'breach of contract contract violation',
            r'\bqualified immunity\b': 'qualified immunity government immunity',
            r'\bsummary judgment\b': 'summary judgment no genuine issue material fact',
            r'\bnegligence\b': 'negligence duty breach causation damages',
            r'\bveil piercing\b': 'veil piercing alter ego corporate veil',
        }
        
        for pattern, expansion in legal_synonyms.items():
            if re.search(pattern, query, re.IGNORECASE):
                # Add expansion terms if not already present
                expansion_terms = expansion.split()
                for term in expansion_terms:
                    if term.lower() not in query.lower():
                        query += f' {term}'
        
        return query
    
    def route_query(self, query: str) -> Dict:
        """
        Route query to appropriate collection
        
        Args:
            query: User query
        
        Returns:
            Routing configuration
        """
        query_type = self.classify_query(query)
        
        # Route contracts to contract collection
        if query_type == 'contract':
            return {
                'collection': 'legal_contracts',
                'top_k': 5,
                'filters': None
            }
        
        # Route everything else to case law
        else:
            jurisdiction = self.extract_jurisdiction(query)
            filters = None
            
            # Add jurisdiction filter if detected
            # (Note: would need jurisdiction field in documents)
            
            return {
                'collection': 'legal_cases',
                'top_k': 5,
                'filters': filters
            }
    
    def handle_query(self, query: str) -> Dict:
        """
        Complete query handling pipeline
        
        Args:
            query: User query
        
        Returns:
            Research results
        """
        # Preprocess
        processed_query = self.preprocess_query(query)
        
        # Route
        routing = self.route_query(processed_query)
        
        # Execute research
        result = self.engine.research(
            processed_query,
            collection=routing['collection'],
            top_k=routing['top_k'],
            filters=routing['filters']
        )
        
        # Add metadata
        result['query_type'] = self.classify_query(query)
        result['jurisdiction'] = self.extract_jurisdiction(query)
        result['collection_used'] = routing['collection']
        
        return result
    
    def format_result(self, result: Dict) -> str:
        """
        Format result for display
        
        Args:
            result: Research result
        
        Returns:
            Formatted string
        """
        output = []
        
        # Header
        if 'query' in result:
            output.append(f"Query: {result['query']}")
        output.append(f"Type: {result.get('query_type', 'general')}")
        if result.get('jurisdiction'):
            output.append(f"Jurisdiction: {result['jurisdiction']}")
        output.append("\n" + "="*80 + "\n")
        
        # Answer
        output.append("ANSWER:")
        output.append(result.get('answer', 'No answer generated'))
        output.append("\n" + "="*80 + "\n")
        
        # Sources
        output.append("SOURCES:")
        sources = result.get('sources', [])
        if not sources:
            output.append("No sources found.")
        else:
            for i, source in enumerate(sources, 1):
                output.append(f"\n{i}. {source.get('title', 'Untitled Document')}")
                score = source.get('score', 0)
                if isinstance(score, float):
                    output.append(f"   Relevance: {score:.2%}")
                if source.get('court') and source.get('court') != 'N/A':
                    output.append(f"   Court: {source['court']}")
                if source.get('citations') and source.get('citations') != 'N/A':
                    output.append(f"   Citation: {source['citations']}")
                text = source.get('text', '')
                if text:
                    output.append(f"   Excerpt: {text[:200]}...")
        
        return "\n".join(output)


def main():
    """Test query handler"""
    # Initialize
    engine = LegalRAGEngine()
    handler = QueryHandler(engine)
    
    # Test queries
    queries = [
        "What's the SOL for breach of K in California?",
        "Indemnification provisions in commercial contracts",
        "Elements of negligence in tort law",
    ]
    
    for query in queries:
        print(f"\n{'#'*80}")
        result = handler.handle_query(query)
        print(handler.format_result(result))


if __name__ == "__main__":
    main()