import re
from find_mpep import extract_citations
from find_mpep import MPEPCitation, StatuteCitation
import eyecite
from eyecite.models import FullCaseCitation, Resource, FullLawCitation, IdCitation, FullJournalCitation, ShortCaseCitation, UnknownCitation

def remove_duplicate_citations(citations):
    cleaned_citations = []
    prev_extra = ""

    for citation in citations:
        if isinstance(citation, FullCaseCitation):
            current_extra = citation.metadata.extra

            # Compare "extra" text with the previous citation
            if current_extra and current_extra != prev_extra:
                cleaned_citations.append(citation)
                prev_extra = current_extra
        else:
            cleaned_citations.append(citation)

    return cleaned_citations

def get_citation_start(citation):
    if isinstance(citation, (MPEPCitation, StatuteCitation)):
        return citation.span()[0]
    elif isinstance(citation, (FullCaseCitation, ShortCaseCitation, IdCitation)):
        return citation.full_span()[0]
    else:
        return 0  # Adjust this value based on your specific case

def extract_and_replace_citations_tokens(text):

    clean_text = eyecite.clean_text(text, ["all_whitespace"])

    case_citations = eyecite.get_citations(clean_text)

    code_mpep_citations = extract_citations(clean_text)

    all_citations = case_citations + code_mpep_citations

    citations = [citation for citation in all_citations if not isinstance(citation, (UnknownCitation, IdCitation))]

    cleaned_citations = remove_duplicate_citations(citations)

    ordered_citations = sorted(cleaned_citations, key=get_citation_start)

    offset = 0

    for citation in ordered_citations:

        print(f"New Offset: {offset}")
        
        if isinstance(citation, (MPEPCitation, StatuteCitation)):
            citation_start, citation_end = citation.span()
            print(f"Home_Start: {citation_start}")
            print(f"Home_End: {citation_end}")
            print(f"Dif_Home: {citation_end - citation_start}")
        
        if isinstance(citation, (FullCaseCitation, ShortCaseCitation, IdCitation)):
            citation_start, citation_end = citation.full_span()
            print(f"Eyecite_Start: {citation_start}")
            print(f"Eyecite_End: {citation_end}")
            print(f"Dif_Eyecite: {citation_end - citation_start}")

        if isinstance(citation, MPEPCitation):
            mpep_citation_token = f"[MPEP: {citation.formatted()}]"
            print(mpep_citation_token)
            print(f"Token_Len: {len(mpep_citation_token)}")
            new_offset = offset + max(0, len(mpep_citation_token) - (citation_end-citation_start))
            replace_start = max(0, citation_start + offset)
            print(f"Replace_start: {replace_start}")
            #replace_end = replace_start + (citation_end - citation_start)

            if new_offset == 0:
                replace_end = citation_end + offset
            else:
                replace_end = replace_start + (citation_end - citation_start)

            print(f"Replace_end: {replace_end}")
            offset += max(0, len(mpep_citation_token) - (citation_end-citation_start))
            clean_text = clean_text[:replace_start] + mpep_citation_token + clean_text[replace_end:]
            

        if isinstance(citation, StatuteCitation):
            law_citation_token = f"[LAW: {citation.formatted()}]"
            print(law_citation_token)
            print(f"Token_Len: {len(law_citation_token)}")
            new_offset = offset + max(0, len(law_citation_token) - (citation_end-citation_start))
            replace_start = max(0, citation_start + offset)
            print(f"Replace_start: {replace_start}")
            #replace_end = replace_start + (citation_end - citation_start)

            if new_offset == 0:
                replace_end = citation_end + offset
            else:
                replace_end = replace_start + (citation_end - citation_start)

            print(f"Replace_end: {replace_end}")
            offset += max(0, len(law_citation_token) - (citation_end-citation_start))
            clean_text = clean_text[:replace_start] + law_citation_token + clean_text[replace_end:]            
            
        if isinstance(citation, (FullCaseCitation)):
            full_case_citation_token = f"[FULL CASE: {citation.corrected_citation_full()}]"
            print(full_case_citation_token)
            print(f"Token_Len: {len(full_case_citation_token)}")
            new_offset = offset + max(0, len(full_case_citation_token) - (citation_end-citation_start))
            replace_start = max(0, citation_start + offset)
            print(f"Replace_start: {replace_start}")
            #replace_end = replace_start + (citation_end - citation_start)

            if new_offset == 0:
                replace_end = citation_end + offset
            else:
                replace_end = replace_start + (citation_end - citation_start)

            print(f"Replace_end: {replace_end}")
            offset += max(0, len(full_case_citation_token) - (citation_end-citation_start))
            clean_text = clean_text[:replace_start] + full_case_citation_token + clean_text[replace_end:]

        if isinstance(citation, ShortCaseCitation):
            short_case_citation_token = f"[SHORT CASE: {citation.corrected_citation_full()}]"
            print(short_case_citation_token)
            print(f"Token_Len: {len(short_case_citation_token)}")
            new_offset = offset + max(0, len(short_case_citation_token) - (citation_end-citation_start))
            replace_start = max(0, citation_start + offset)
            print(f"Replace_start: {replace_start}")
            #replace_end = replace_start + (citation_end - citation_start)

            if new_offset == 0:
                replace_end = citation_end + offset
            else:
                replace_end = replace_start + (citation_end - citation_start)

            print(f"Replace_end: {replace_end}")
            offset += max(0, len(short_case_citation_token) - (citation_end-citation_start))
            clean_text = clean_text[:replace_start] + short_case_citation_token + clean_text[replace_end:]
        
        if isinstance(citation, IdCitation):
            id_citation_token = f"[ID CITATION: {citation.formatted()}]"
            print(id_citation_token)
            print(f"Token_Len: {len(id_citation_token)}")
            new_offset = offset + max(0, len(id_citation_token) - (citation_end-citation_start))
            replace_start = max(0, citation_start + offset)
            print(f"Replace_start: {replace_start}")
            #replace_end = replace_start + (citation_end - citation_start)

            if new_offset == 0:
                replace_end = citation_end + offset
            else:
                replace_end = replace_start + (citation_end - citation_start)

            print(f"Replace_end: {replace_end}")
            offset += max(0, len(id_citation_token) - (citation_end-citation_start))
            clean_text = clean_text[:replace_start] + id_citation_token + clean_text[replace_end:]
        
        else:
            pass

    return citations, ordered_citations, clean_text