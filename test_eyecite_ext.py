import unittest
from find import get_citations

class TestFindModule(unittest.TestCase):

    def test_get_citations_no_citations(self):
        plain_text = "This is a plain text without any citations."
        citations = get_citations(plain_text)
        self.assertEqual(len(citations), 0)
        print(citations)

    def test_get_citations_usc(self):
        plain_text = "According to 42 U.S.C. § 1983"
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
    def test_get_citations_public_law(self):
        plain_text = "According to Public Law 112-29"
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)

    def test_get_citations_statute(self):
        plain_text = "According to 125 Stat. 284."
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
    def test_get_citations_usc_plus(self):
        plain_text = "According to 35 U.S.C. 1."
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
    def test_get_citations_with_infra(self):
        plain_text = "According to infra at 732"
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
    def test_get_citations_with_mpep1(self):
        plain_text = "According to mpep § 701.32. "
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
    def test_get_citations_with_mpep2(self):
        plain_text = "According to mpep 701.32. "
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
    def test_get_citations_with_id1(self):
        plain_text = "According to Id. at 410."
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
    def test_get_citations_with_id2(self):
        plain_text = "See id at 765."
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
    def test_get_citations_with_supra(self):
        plain_text = "According to supra, 1909 ..."
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
    def test_get_citations_full(self):
        plain_text = "According to Bonito Boats, Inc. v. Thunder Craft Boats, Inc., 489 U.S. 141, 151, 109 S. Ct. 971, 103 L. Ed. 2d 118 (1989) ..."
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
    def test_get_citations_short1(self):
        plain_text = "Adarand, 515 U.S., at 241"
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
    def test_get_citations_short2(self):
        plain_text = "the opinion is real, 515 U.S. at 241"
        citations = get_citations(plain_text)
        self.assertGreater(len(citations), 0)
        print(citations)
    
'''
Art. 1, Sec. 8. Leahy-Smith America Invents Act (AIA), Public Law 112-29, 125 Stat. 284., 35 U.S.C. 1 Establishment.
ante,  at 510-980, infra at 732, mpep § 701.32, mpep chapter 2100, Id. at 410, id at 765, supra, 1909, id, 465
177 L. Ed. 2d, at 809
mpep § 701.32, mpep chapter 2100
Bonito Boats, Inc. v. Thunder Craft Boats, Inc., 489 U.S. 141, 151, 109 S. Ct. 971, 103 L. Ed. 2d 118 (1989)
eyecite
Adarand, 515 U.S., at 241
    Adarand, 515 U.S. at 241
    515 U.S., at 241
'''

if __name__ == '__main__':
    unittest.main()