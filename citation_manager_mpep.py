import re
from find_mpep import extract_citations
from find_mpep import MPEPCitation, StatuteCitation
import eyecite
from eyecite.models import FullCaseCitation, IdCitation, ShortCaseCitation, UnknownCitation
from collections import OrderedDict
import string

'''
Purpose: Preprocessing LLM training data (e.g. the MPEP) to ensure that the LLM being trained can correctly access secondary sources in the text.  The program should be robust enough to preprocess case law during training processes. 

Goal: Extract citations (case law, law/statutes, MPEP) from text and replace the extracted citations with tokens precisely identifying the source fo the citation. 

Steps: 
    1. extract_and_clean_citations: 
        a. input: text file. 
        b. output: dictionary of extracted citations (key) and citation metadata (values) 
        c. steps:    
            i. cleaned_text: 
                (a) text string cleaned using excite.clean_text 
                (b) remove section symbol ('§')
            ii. identify citations using eyecite.get_citations (open source citation library) and find_MPEP.extract_citations (purpose built library that identifies law (USC and CFR) citations and MPEP sections) that generate metadata precisely identifying the source and location of the citation.
            iii. Clean extracted citations: 
                (a) remove_duplicates: eyecite identifies both citations in compound citations (e.g. citations pointing to both court reporters and USPQ) as separate citations. Comparing citations with "exra" in eyecite metadata is used to eliminate duplicate citations. 
                (b) get_citation_text: get citation text identified by eyecite.get_citations and find_MPEP.
                (c) clean_citation_ends: removes extra punctuation and whitespace from citations extracted by eyecite.
                (d) correct_citation_errors: eyecite inadvertantly removes puncuation between compound citations and ')' at the end of citations. This fucntion corrects these errors.
            iv. Add citations to dictionary (corrected_citation_texts)             
    2. order_citations: 
        a. input: dictionary of citations and clean_text. 
        b. output: dictionary of citations ordered by citation_start in text.
        c. steps:
            i. Find span for citations extracted:
                (a) find_citation_span: Parses eyecite citations after clearning and finds the the 'citation_start" and "citation_end" for each citation. I found a lot of errors in the span returned by eyecite. This was the most reproducible means for finding the span. 
                (b) find_citation_span uses the span returned from find_mpep.
                (c) span replaces citation text as key in output dictionary.
            ii. Arrange citations in order of citation_start using OrderedDict() library
    3. process_citations:
        a. input: dictionary of ordered citations and clean_text.
        b. output: dictionary of ordered citations and processed_text in which citations in clean_text are replaced with tokens containing metadata from eyecite and find_mpep. 
        c. steps: 
            i. loop through citations in dictionary, sorting by object type.
            ii. create token using citation text and metadata.
            iii. use span (key) to place token in clean_text.
            iv. set offset based on the difference in legnth of token and extracted citation.
    4. proofread_processed_text (eyecite citations leave 5-6 extra characters after the token that I could not fix with span.  This function removes these extra_characters): 
        a. input: processed text file.
        b. output: updated processed text file. 
        c. steps: 
            i. loop through text character-by-character. 
            ii. identify citations based on '[' and ']' flags. 
            iii. find extra characters between ']' and next non-')' punctuation for case law citations. MPEP/Law citations appear inline in the text and are excluded from this functaionality. 
'''

def extract_and_clean_citations(text):
    clean_text_1 = eyecite.clean_text(text, ["all_whitespace"])
    clean_text_2 = clean_text_1.replace('§','')
    clean_text = ' '.join(clean_text_2.split())
    ec_citations = eyecite.get_citations(clean_text)
    ec_citations_dedup =  remove_duplicate_citations(ec_citations)
    case_citations = [citation for citation in ec_citations_dedup if not isinstance(citation, (UnknownCitation))]
    citation_texts_ec = get_citation_text(case_citations)
    ec_citation_texts = clean_citation_ends(citation_texts_ec)
    
    corrected_citation_texts_ec = {}
    for citation_text, citation in zip(ec_citation_texts, case_citations):
        corrected_citation_text_ec = correct_citation_errors(citation, citation_text)
        corrected_citation_texts_ec[corrected_citation_text_ec] = citation

    # Add MPEP citations directly to the dictionary
    corrected_citation_texts = corrected_citation_texts_ec.copy()

    code_mpep_citations = extract_citations(clean_text)
    citation_texts_mpep = get_citation_text(code_mpep_citations)
    code_mpep_citation_texts = clean_citation_ends(citation_texts_mpep)

    for citation, citation_text in zip(code_mpep_citation_texts, code_mpep_citations):
        citation_key = citation
        if citation not in corrected_citation_texts:
            corrected_citation_texts[citation_key] = [citation_text]
        else:
            corrected_citation_texts[citation_key].append(citation_text)

    return corrected_citation_texts, clean_text

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

def correct_citation_errors(citation, citation_text):
    # Check if metadata.extra exists
    if hasattr(citation.metadata, 'extra') and citation.metadata.extra:
        # Find the position of metadata.extra in the citation_text
        extra_position = citation_text.find(citation.metadata.extra)

        # Add a comma before metadata.extra
        corrected_citation_text = (
            citation_text[:extra_position].rstrip(', ') + 
            f", {citation.metadata.extra}" + 
            citation_text[extra_position + len(citation.metadata.extra):]
        )
    else:
        corrected_citation_text = citation_text

    # Add the missing ')' in the court date part of the citation
    parts = corrected_citation_text.split('(')
    if len(parts) > 1:
        court_date_part = parts[1].strip()
        if not court_date_part.endswith(')'):
            parts[1] = court_date_part + ') '

    return '('.join(parts)

def clean_citation_ends(citations):
    clean_citations = []

    for citation in citations:
        characters_to_strip = string.whitespace + string.punctuation.replace(')', '')
        clean_citation = citation.strip(characters_to_strip)
        clean_citations.append(clean_citation)

    return(clean_citations)

def get_citation_text(citations):
    if isinstance(citations, list):
        # Handle the list of citations
        citation_texts = []
        for citation in citations:
            text = get_citation_text(citation)  # Recursively handle individual citations
            if text:
                citation_texts.append(text)
        return citation_texts
    elif isinstance(citations, (MPEPCitation, StatuteCitation)):
        return citations.formatted()[0]
    elif isinstance(citations, (FullCaseCitation, ShortCaseCitation, IdCitation)):
        #print(f"eyecite_citation: {citations.corrected_citation_full()}")
        return citations.corrected_citation_full() # + ")"
    else:
        raise ValueError(f"Unsupported citation type: {type(citations)}")
    

def find_citation_span(text, citation_text, token_data=None):
    
    if isinstance(token_data, (FullCaseCitation, ShortCaseCitation, IdCitation)):
        citation_start, _ = token_data.span()
        citation_start_f, _ = token_data.full_span()
        citation_end = citation_start_f + len(citation_text) + 5
        #print(f"text: {citation_text}")
        #print(f"eyecite_start, end: {citation_start, citation_end}")
        return citation_start, citation_end
    
    # Handle token_data_list as a list containing MPEPCitation or StatuteCitation instances
    else:
        #print(f"Token span for: {citation_text}")
        # Extract the first (and only) element from the list
        citation_start, citation_end = token_data.span()
        return citation_start, citation_end
    


def order_citations(citation_dict, clean_text):
    ordered_citations = OrderedDict()

    for citation_text, token_data in citation_dict.items():
        if isinstance(token_data, list):
            for indi_token_data in token_data:
                if isinstance(indi_token_data, (StatuteCitation, MPEPCitation)):
                    span_info = find_citation_span(clean_text, citation_text, indi_token_data)
                    if span_info:
                        replace_start, replace_end = span_info
                        add_citation = True
                        
                        # Check for overlaps with existing citations
                        for existing_start, existing_end in ordered_citations.keys():
                            if replace_start < existing_end and replace_end > existing_start:
                                add_citation = False
                                break
                        
                        if add_citation:
                            ordered_citations[(replace_start, replace_end)] = indi_token_data
                            #print(f"Span for statute '{citation_text}': {span_info}")
        else:
            span_info = find_citation_span(clean_text, citation_text, token_data)
            if span_info:
                replace_start, replace_end = span_info[:2]
                add_citation = True

                # Check for overlaps with existing citations
                for existing_start, existing_end in ordered_citations.keys():
                    if replace_start < existing_end and replace_end > existing_start:
                        add_citation = False
                        break
                
                if add_citation:
                    ordered_citations[(replace_start, replace_end)] = token_data
                    #print(f"Span for '{citation_text}': {span_info}")

    ordered_citations = OrderedDict(sorted(ordered_citations.items(), key=lambda x: x[0]))

    return ordered_citations

def process_citations(ordered_citations, clean_text):
    processed_text = clean_text
    offset = 0
    
    for (replace_start, replace_end), token_data in ordered_citations.items():
        #print("----")
        #print(f"New Offset: {offset}")
        
        if isinstance(token_data, MPEPCitation):
            mpep_citation_token = f"[MPEP: {token_data.formatted()}]"
            new_offset = offset + max(0, len(mpep_citation_token) - (replace_end-replace_start))
            #print(f"Raplace_Start: {replace_start}")
            new_start = replace_start + offset
            #print(f"New_start: {new_start}")
            if new_offset == 0:
                new_end = replace_end + offset
            else:
                new_end = new_start + (replace_end-replace_start)
            #print(f"Replace_end: {replace_end}")
            #print(f"New_end: {new_end}")
            offset += max(0, len(mpep_citation_token) - (replace_end-replace_start))
            processed_text = processed_text[:new_start] + mpep_citation_token + processed_text[new_end:] 

        if isinstance(token_data, StatuteCitation):
            law_citation_token = f"[LAW: {token_data.formatted()}]"
            new_offset = offset + max(0, len(law_citation_token) - (replace_end-replace_start))
            #print(f"Raplace_Start: {replace_start}")
            new_start = replace_start + offset
            #print(f"New_start: {new_start}")
            if new_offset == 0:
                new_end = replace_end + offset
            else:
                new_end = new_start + (replace_end-replace_start)
            #print(f"Replace_end: {replace_end}")
            #print(f"New_end: {new_end}")
            offset += max(0, len(law_citation_token) - (replace_end-replace_start))
            processed_text = processed_text[:new_start] + law_citation_token + processed_text[new_end:]            
            
        if isinstance(token_data, (FullCaseCitation)):
            full_case_citation_token = f"[FULL CASE: {token_data.corrected_citation_full()}) {token_data.metadata}]"
            new_offset = offset + max(0, len(full_case_citation_token) - (replace_end-replace_start))
            #print(f"Raplace_Start: {replace_start}")
            new_start = replace_start + offset
            #print(f"New_start: {new_start}")
            if new_offset == 0:
                new_end = replace_end + offset
            else:
                new_end = new_start + (replace_end-replace_start)
            #replace_end = new_end
            #print(f"Replace_end: {replace_end}")
            #print(f"New_end: {new_end}")
            offset += max(0, len(full_case_citation_token) - (replace_end-replace_start))
            processed_text = processed_text[:new_start] + full_case_citation_token + processed_text[new_end:]

        if isinstance(token_data, ShortCaseCitation):
            short_case_citation_token = f"[SHORT CASE: {token_data.corrected_citation_full()}) {token_data.metadata}]"
            new_offset = offset + max(0, len(short_case_citation_token) - (replace_end-replace_start))
            #print(f"Raplace_Start: {replace_start}")
            new_start = replace_start + offset
            #print(f"New_start: {new_start}")
            if new_offset == 0:
                new_end = replace_end + offset
            else:
                new_end = new_start + (replace_end-replace_start)
            #print(f"Replace_end: {replace_end}")
            #print(f"New_end: {new_end}")
            offset += max(0, len(short_case_citation_token) - (replace_end-replace_start))
            processed_text = processed_text[:new_start] + short_case_citation_token + processed_text[new_end:]
        
        if isinstance(token_data, IdCitation):
            id_citation_token = f"[ID CITATION: {token_data.corrected_citation_full()}) {token_data.metadata}]"
            new_offset = offset + max(0, len(id_citation_token) - (replace_end-replace_start))
            #print(f"Raplace_Start: {replace_start}")
            new_start = replace_start + offset
            #print(f"New_start: {new_start}")
            if new_offset == 0:
                new_end = replace_end + offset
            else:
                new_end = new_start + (replace_end-replace_start)
            #print(f"Replace_end: {replace_end}")
            #print(f"New_end: {new_end}")
            offset += max(0, len(id_citation_token) - (replace_end-replace_start))
            processed_text = processed_text[:new_start] + id_citation_token + processed_text[new_end:]
        
        else:
            pass

    return ordered_citations, processed_text

def determine_citation_type(citation_text):
    if "LAW" in citation_text:
        return StatuteCitation
    elif "MPEP" in citation_text:
        return MPEPCitation
    elif "FULL CASE" in citation_text:
        return FullCaseCitation
    elif "SHORT CASE" in citation_text:
        return ShortCaseCitation
    elif "ID" in citation_text:
        return IdCitation
    else:
        return None

def proofread_processed_text(processed_text):
    # List to store cleaned parts of the text
    cleaned_parts = []

    # Variable to track whether the current part is part of a citation token
    in_citation = False
    in_extra_characters = False

    citation_part = []
    citations_found = []
    extra_characters = []
    last_citation_type = None
    char_count = 0
    in_extra_characters_char_count = 0
 
    for char in processed_text:
        char_count += 1
        # Check if the character is part of a citation token
        if char == "[" and char_count < 20:
            in_citation = False
            in_extra_characters = False    
        if char == "[" and not in_citation: 
            in_citation = True
            in_extra_characters = False
            citation_part = [char]  # Start a new list for citation parts
        elif char == "]" and in_citation: 
            in_citation = False
            in_extra_characters = True
            citation_part.append(char)
            citations_found.append(''.join(citation_part))
            last_citation_type = determine_citation_type(''.join(citation_part))
            #print(f'Citation Type: {last_citation_type}')
        elif in_citation:
            citation_part.append(char)
        # Check if the last citation type should be followed by extra characters
        if in_extra_characters:
            in_extra_characters_char_count += 1
            if last_citation_type in [FullCaseCitation, ShortCaseCitation]: 
                if char == ']':
                    cleaned_parts.append(char)
                elif char in string.punctuation and char not in (')', ']'):
                    in_citation = False
                    in_extra_characters = False
                    last_citation_type = None
                    citation_part.clear()
                    cleaned_parts.append(char)
                else: 
                    extra_characters.append(char)
            else:
                in_citation = False
                in_extra_characters = False
                cleaned_parts.append(char)
        else:
            cleaned_parts.append(char)
 
        
    cleaned_text = ''.join(cleaned_parts)
    #print(f"Characters Analyzed: {char_count}")

    return cleaned_text, citations_found

corrected_citation_texts, clean_text = extract_and_clean_citations(text_file)
ordered_citations = order_citations(corrected_citation_texts, clean_text)
ordered_citations, processed_text = process_citations(ordered_citations, clean_text)
cleaned_text, _ = proofread_processed_text(processed_text)