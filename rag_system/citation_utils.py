"""
Citation Extraction and Linking Utilities
Extracts legal citations and creates CourtListener links
"""
import re
from typing import List, Dict, Tuple, Optional


class CitationExtractor:
    """Extract and link legal citations"""
    
    # Citation patterns
    PATTERNS = {
        'us_reporter': r'\b\d+\s+U\.S\.(?:\sApp\.)?\s+\d+\b',
        'federal_reporter': r'\b\d+\s+F\.\s*(?:2d|3d|4th)?\s+\d+\b',
        'supreme_court': r'\b\d+\s+S\.\s*Ct\.\s+\d+\b',
        'federal_supplement': r'\b\d+\s+F\.\s*Supp\.\s*(?:2d|3d)?\s+\d+\b',
        'state_reporter': r'\b\d+\s+[A-Z][a-z\.]*\s*(?:2d|3d)?\s+\d+\b',
    }
    
    # CourtListener citation types
    COURTLISTENER_TYPES = {
        'us_reporter': 'us',
        'federal_reporter': 'f',
        'supreme_court': 'sct',
        'federal_supplement': 'f-supp',
    }
    
    def __init__(self):
        """Initialize citation extractor"""
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.PATTERNS.items()
        }
    
    def extract_citations(self, text: str) -> List[Dict[str, str]]:
        """
        Extract all citations from text
        
        Args:
            text: Legal text to extract citations from
        
        Returns:
            List of citation dictionaries with type, text, and link
        """
        citations = []
        seen = set()  # Avoid duplicates
        
        for citation_type, pattern in self.compiled_patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                citation_text = match.group(0)
                
                # Avoid duplicates
                if citation_text in seen:
                    continue
                seen.add(citation_text)
                
                # Create CourtListener link if possible
                link = self._create_courtlistener_link(citation_text, citation_type)
                
                citations.append({
                    'type': citation_type,
                    'text': citation_text,
                    'link': link,
                    'position': match.start()
                })
        
        # Sort by position in text
        citations.sort(key=lambda x: x['position'])
        
        return citations
    
    def _create_courtlistener_link(
        self, 
        citation_text: str, 
        citation_type: str
    ) -> Optional[str]:
        """
        Create CourtListener link for citation
        
        Args:
            citation_text: Citation text (e.g., "123 U.S. 456")
            citation_type: Type of citation
        
        Returns:
            CourtListener URL or None
        """
        # Parse volume and page
        parts = re.split(r'\s+', citation_text.strip())
        
        if len(parts) < 3:
            return None
        
        try:
            volume = parts[0]
            reporter = parts[1]
            page = parts[-1]
            
            # Get CourtListener reporter abbreviation
            cl_type = self.COURTLISTENER_TYPES.get(citation_type)
            
            if not cl_type:
                return None
            
            # Create CourtListener citation search URL
            # Format: https://www.courtlistener.com/c/{reporter}/{volume}/{page}/
            return f"https://www.courtlistener.com/c/{cl_type}/{volume}/{page}/"
        
        except (ValueError, IndexError):
            return None
    
    def highlight_citations(
        self, 
        text: str, 
        format_type: str = 'markdown'
    ) -> str:
        """
        Highlight citations in text with links
        
        Args:
            text: Text to process
            format_type: Output format ('markdown', 'html')
        
        Returns:
            Text with highlighted/linked citations
        """
        citations = self.extract_citations(text)
        
        if not citations:
            return text
        
        # Process in reverse order to maintain positions
        result = text
        for citation in reversed(citations):
            start = citation['position']
            end = start + len(citation['text'])
            citation_text = citation['text']
            link = citation['link']
            
            if link:
                if format_type == 'markdown':
                    replacement = f"[{citation_text}]({link})"
                elif format_type == 'html':
                    replacement = f'<a href="{link}" target="_blank">{citation_text}</a>'
                else:
                    replacement = citation_text
                
                result = result[:start] + replacement + result[end:]
        
        return result
    
    def extract_case_info(self, text: str) -> Dict[str, any]:
        """
        Extract case information from text
        
        Args:
            text: Legal text
        
        Returns:
            Dictionary with case metadata
        """
        citations = self.extract_citations(text)
        
        # Extract case names (basic pattern)
        case_name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        case_matches = re.finditer(case_name_pattern, text)
        
        case_names = []
        for match in case_matches:
            case_names.append({
                'plaintiff': match.group(1),
                'defendant': match.group(2),
                'full_name': match.group(0)
            })
        
        # Extract years
        year_pattern = r'\b(19|20)\d{2}\b'
        years = list(set(re.findall(year_pattern, text)))
        
        return {
            'citations': citations,
            'case_names': case_names[:5],  # Top 5
            'years': sorted(years, reverse=True)[:5],  # Most recent 5
            'num_citations': len(citations)
        }


def create_citation_link(citation: str) -> Optional[str]:
    """
    Quick function to create a CourtListener link
    
    Args:
        citation: Citation text
    
    Returns:
        CourtListener URL or None
    """
    extractor = CitationExtractor()
    citations = extractor.extract_citations(citation)
    
    if citations and citations[0]['link']:
        return citations[0]['link']
    
    return None


# Example usage
if __name__ == "__main__":
    extractor = CitationExtractor()
    
    # Test text
    test_text = """
    In Smith v. Jones, 123 U.S. 456 (1990), the Court held that...
    This was later affirmed in 456 F.3d 789 (2005).
    See also Johnson v. Williams, 234 S. Ct. 567 (1995).
    """
    
    # Extract citations
    citations = extractor.extract_citations(test_text)
    
    print("Extracted Citations:")
    for cit in citations:
        print(f"  - {cit['text']}")
        print(f"    Type: {cit['type']}")
        print(f"    Link: {cit['link']}")
        print()
    
    # Highlight citations
    highlighted = extractor.highlight_citations(test_text, format_type='markdown')
    print("Highlighted Text:")
    print(highlighted)

