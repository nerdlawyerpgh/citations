import re
from dataclasses import dataclass, field
from typing import Optional, Sequence, List, Any

# Example MPEP citation: MPEP 2145 or MPEP § 701.32(a)(1)
MPEP_REGEX = r'(\bMPEP\s+)(?:§\s+)?(?P<chapter>\d+)(?:\.\s*(?P<section>[\d]+)(?P<subsection>(?:\([\da-zA-Z]+\)(?:\(\d+\))?|(?:\.([\da-zA-Z]+)(?:\.\([\da-zA-Z]+)\)?)?)?)?)?'
mpep_pattern = re.compile(MPEP_REGEX)

# Statute capture.  Examples: 35 U.S.C. 112 or 37 cfr 3.73(c)
STATUTE_REGEX = r'(?P<title>\d+)\s+(?P<code>U\.S\.C\.|USC|C.F.R.|CFR|(stat(?:\.)?))\s+(?P<section>[\d]+(?:\([\da-zA-Z]+\))?)?(?:\s*\.\s*(?P<subsection>[\da-zA-Z]+(?:\([\da-zA-Z]+\))?)?)?'
statute_pattern = re.compile(STATUTE_REGEX, re.IGNORECASE)

@dataclass(eq=True, unsafe_hash=True)
class MPEPCitation:
    """Class representing an MPEP citation."""
    index: int  # index of _token in the token list
    groups: dict = field(default=dict)
    span_start: Optional[int] = None
    span_end: Optional[int] = None
    metadata: Any = None

    def formatted(self):
        """Return a formatted version of the extracted MPEP citation."""
        m = self.metadata
        g = self.groups
        if m:
            parts = [f'MPEP {m["chapter"]}.{m["section"] or ""}{m["subsection"] or ""}']
            return ' '.join(parts), g
        return '', g
    
    def span(self):
        """Start and stop offsets in source text for matched_text()."""
        return self.span_start, self.span_end

@dataclass(eq=True, unsafe_hash=True)
class StatuteCitation:
    """Class representing a statute citation."""
    index: int  # index of _token in the token list
    groups: dict = field(default=dict)
    span_start: Optional[int] = None
    span_end: Optional[int] = None
    metadata: Any = None

    def formatted(self):
        """Return a formatted version of the extracted statute citation."""
        m = self.metadata
        g = self.groups
        if m:
            parts = [f'{m["title"]} {m["code"]} {m["section"]}{m["subsection"] or ""}']
            return ' '.join(parts), g
        return '', g
    
    def span(self):
        """Start and stop offsets in source text for matched_text()."""
        return self.span_start, self.span_end
    
def extract_citations(text):
    """Extract both MPEP and statute citations from the given text."""
    mpep_matches = mpep_pattern.finditer(text)
    statute_matches = statute_pattern.finditer(text)
    
    citations = []

    for match in mpep_matches:
        groups = match.groupdict()
        citation = MPEPCitation(
            metadata=groups,
            groups=groups,
            index=match.start(),
            span_start=match.start(),
            span_end=match.end()    # Use the start position as the index
        )
        citations.append(citation)
    
    for match in statute_matches:
        groups = match.groupdict()
        citation = StatuteCitation(
            metadata=groups,
            groups=groups,
            index=match.start(),
            span_start=match.start(),
            span_end=match.end('subsection') if groups['subsection'] else match.end('section')
        )
        citations.append(citation)
    
    return citations