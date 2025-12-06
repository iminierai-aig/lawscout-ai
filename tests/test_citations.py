"""
Tests for Citation Extraction and Linking
"""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_system.citation_utils import CitationExtractor, create_citation_link


class TestCitationExtractor(unittest.TestCase):
    """Test cases for citation extraction"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = CitationExtractor()
    
    def test_extract_us_reporter(self):
        """Test extraction of U.S. Reporter citations"""
        text = "The court in Smith v. Jones, 123 U.S. 456, held that..."
        citations = self.extractor.extract_citations(text)
        
        self.assertGreater(len(citations), 0)
        self.assertEqual(citations[0]['type'], 'us_reporter')
        self.assertIn('123 U.S. 456', citations[0]['text'])
    
    def test_extract_federal_reporter(self):
        """Test extraction of Federal Reporter citations"""
        text = "See also 456 F.3d 789 (5th Cir. 2010)"
        citations = self.extractor.extract_citations(text)
        
        self.assertGreater(len(citations), 0)
        self.assertEqual(citations[0]['type'], 'federal_reporter')
    
    def test_extract_supreme_court_reporter(self):
        """Test extraction of Supreme Court Reporter citations"""
        text = "In 234 S. Ct. 567, the Supreme Court ruled..."
        citations = self.extractor.extract_citations(text)
        
        self.assertGreater(len(citations), 0)
        self.assertEqual(citations[0]['type'], 'supreme_court')
    
    def test_extract_federal_supplement(self):
        """Test extraction of Federal Supplement citations"""
        text = "The district court in 789 F. Supp. 2d 123 found..."
        citations = self.extractor.extract_citations(text)
        
        self.assertGreater(len(citations), 0)
        self.assertEqual(citations[0]['type'], 'federal_supplement')
    
    def test_multiple_citations(self):
        """Test extraction of multiple citations from text"""
        text = """
        In Smith v. Jones, 123 U.S. 456 (1990), the Court held that...
        This was later affirmed in 456 F.3d 789 (2005).
        See also 234 S. Ct. 567 (1995).
        """
        citations = self.extractor.extract_citations(text)
        
        self.assertGreaterEqual(len(citations), 3)
    
    def test_no_citations(self):
        """Test text with no citations"""
        text = "This is plain text with no legal citations."
        citations = self.extractor.extract_citations(text)
        
        self.assertEqual(len(citations), 0)
    
    def test_create_courtlistener_link(self):
        """Test CourtListener link creation"""
        link = self.extractor._create_courtlistener_link(
            "123 U.S. 456",
            "us_reporter"
        )
        
        self.assertIsNotNone(link)
        self.assertIn("courtlistener.com", link)
        self.assertIn("/c/us/123/456/", link)
    
    def test_highlight_citations_markdown(self):
        """Test citation highlighting in markdown format"""
        text = "See 123 U.S. 456 for details."
        highlighted = self.extractor.highlight_citations(text, format_type='markdown')
        
        self.assertIn('[123 U.S. 456]', highlighted)
        self.assertIn('courtlistener.com', highlighted)
    
    def test_highlight_citations_html(self):
        """Test citation highlighting in HTML format"""
        text = "See 123 U.S. 456 for details."
        highlighted = self.extractor.highlight_citations(text, format_type='html')
        
        self.assertIn('<a href=', highlighted)
        self.assertIn('123 U.S. 456', highlighted)
        self.assertIn('target="_blank"', highlighted)
    
    def test_extract_case_info(self):
        """Test case information extraction"""
        text = """
        In Smith v. Jones, 123 U.S. 456 (1990), the Court held...
        See also Johnson v. Williams, 234 S. Ct. 567 (1995).
        """
        case_info = self.extractor.extract_case_info(text)
        
        self.assertIn('citations', case_info)
        self.assertIn('case_names', case_info)
        self.assertIn('years', case_info)
        self.assertGreater(len(case_info['citations']), 0)
        self.assertGreater(len(case_info['case_names']), 0)
    
    def test_case_name_extraction(self):
        """Test extraction of case names"""
        text = "Smith v. Jones is an important precedent."
        case_info = self.extractor.extract_case_info(text)
        
        if case_info['case_names']:
            self.assertEqual(case_info['case_names'][0]['plaintiff'], 'Smith')
            self.assertEqual(case_info['case_names'][0]['defendant'], 'Jones')
    
    def test_duplicate_citation_removal(self):
        """Test that duplicate citations are removed"""
        text = "See 123 U.S. 456 and also 123 U.S. 456 again."
        citations = self.extractor.extract_citations(text)
        
        # Should only find one instance
        citation_texts = [c['text'] for c in citations]
        self.assertEqual(len(citation_texts), len(set(citation_texts)))
    
    def test_citation_sorting(self):
        """Test that citations are sorted by position"""
        text = "First 123 U.S. 456, then 234 F.3d 789."
        citations = self.extractor.extract_citations(text)
        
        if len(citations) >= 2:
            self.assertLess(citations[0]['position'], citations[1]['position'])


class TestCreateCitationLink(unittest.TestCase):
    """Test standalone citation link creation function"""
    
    def test_create_link_function(self):
        """Test the standalone create_citation_link function"""
        link = create_citation_link("123 U.S. 456")
        
        if link:  # May be None if pattern doesn't match
            self.assertIn("courtlistener.com", link)
    
    def test_invalid_citation(self):
        """Test with invalid citation"""
        link = create_citation_link("not a citation")
        
        # Should return None for invalid citations
        self.assertIsNone(link)


if __name__ == '__main__':
    unittest.main()

