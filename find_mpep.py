import re
from dataclasses import dataclass, field
from typing import Optional, Sequence, List

MPEP_REGEX = r'(\bMPEP\s+)(?:§\s+)?(?P<chapter>\d+)(?:\.\s*(?P<section>[\d]+)(?P<subsection>(?:\([\da-zA-Z]+\)(?:\(\d+\))?|(?:\.([\da-zA-Z]+)(?:\.\([\da-zA-Z]+)\)?)?)?)?)?'

#MPEP_REGEX = r'(\bMPEP\s+)(?:§\s+)?(?P<chapter>\d+)(?:\.\s*(?P<section>[\d]+)(?:\.(?P<subsection>[\da-zA-Z]+(?:\([\da-zA-Z]+\)(?:\(\d+\))?)?)?)?)?'


# Example MPEP citation: MPEP 2145 or MPEP § 701.32(a)(1)
mpep_pattern = re.compile(MPEP_REGEX)

@dataclass(eq=True, unsafe_hash=True)
class MPEPCitation:
    """Class representing an MPEP citation."""
    metadata: Optional[dict] = field(default=None)

    def formatted(self):
        """Return a formatted version of the extracted MPEP citation."""
        m = self.metadata
        if m:
            parts = [f'MPEP {m["chapter"]}']
            if "section" in m:
                parts.append(f'{m["section"]}')
            if "subsection" in m:
                parts.append(f'{m["subsection"]}')
            return ' '.join(parts)
        return ''

def extract_mpep_citation(text):
    """Extract MPEP citations from the given text."""
    matches = mpep_pattern.finditer(text)
    citations = []
    for match in matches:
        citation = MPEPCitation(metadata=match.groupdict())
        citations.append(citation)
    return citations