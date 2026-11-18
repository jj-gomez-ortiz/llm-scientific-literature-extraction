"""Deterministic (regex) extractors for fields that always follow the same format:
DOI, publication year, citation style, number of references and most cited reference."""

import re
from collections import Counter

MONTHS = {"January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"}
NAME = r"[A-Z][A-Za-zÀ-ÿ’'\-]+"


def extract_doi(text):
    m = re.search(r"(?i)doi:?\s*(10\.\d{4,}/[^\s]+)", text)
    return m.group(1) if m else None


def extract_year(text):
    m = re.search(r"(?i)published:?\s*\d{1,2}\s+\w+\s+(\d{4})", text)
    return int(m.group(1)) if m else None


def split_references(text):
    """Return (body, references). If there is no reference section, (text, None)."""
    headers = list(re.finditer(r"\n\s*(REFERENCES|References)\s*\n", text))
    if not headers:
        return text, None
    start = headers[-1].start()
    refs = text[start:]
    end = re.search(r"\n\s*(Conflict of [Ii]nterest|Publisher.s note|Copyright ©|Disclaimer)", refs)
    if end:
        refs = refs[:end.start()]
    return text[:start], refs


def citation_style_and_count(refs):
    """Detect 'numeric' ([15]) vs 'author-year' (Flaten, 2008) style and count references."""
    numbered = re.findall(r"(?m)^\s*(\d{1,3})\.\s", refs)
    if len(numbered) > 5:
        return "numeric", max(map(int, numbered))
    return "author-year", len(re.findall(r"\((?:\d{4}[a-z]?|in press|n\.d\.)\)\.", refs))


def compact(s):
    """Re-join words hyphenated at line ends and collapse whitespace."""
    return re.sub(r"\s+", " ", re.sub(r"-\n(?=[a-z])", "", s))


def most_cited_reference(body, refs, style, n_refs):
    """Return (reference, times cited in the body)."""
    body = compact(body)
    if style == "author-year":
        pattern = rf"({NAME}(?: et al\.| and {NAME}| & {NAME})?),? \(?(\d{{4}})[a-z]?[);,]"
        ignore = MONTHS | {"In", "The", "Published", "Received", "Accepted"}
        cites = Counter(f"{author}, {year}" for author, year in re.findall(pattern, body)
                        if author.split()[0] not in ignore)
        return cites.most_common(1)[0] if cites else (None, None)

    # Numeric style: (1, 2), [3-5], (12–14)...
    cites = Counter()
    for group in re.findall(r"[\(\[]((?:\d{1,3}\s*[,–-]\s*)*\d{1,3})[\)\]]", body):
        for part in group.split(","):
            if re.search("[–-]", part):
                a, b = map(int, re.split("[–-]", part))
                cites.update(range(a, b + 1))
            else:
                cites[int(part)] += 1
    cites = Counter({k: v for k, v in cites.items() if 1 <= k <= n_refs})
    if not cites:
        return None, None
    number, times = cites.most_common(1)[0]
    # Translate the number into "Author et al., year" using the reference list
    entries = re.split(r"(?m)^\s*\d{1,3}\.\s", refs)
    entry = compact(entries[number]) if number < len(entries) else ""
    author = re.match(NAME, entry)
    year = re.search(r"\((\d{4})\)", entry)
    if author and year:
        suffix = " et al." if "et al" in entry.split("(")[0] else ""
        return f"[{number}] {author.group(0)}{suffix}, {year.group(1)}", times
    return f"[{number}]", times


def extract_with_rules(text):
    body, refs = split_references(text)
    row = {"doi": extract_doi(text), "year": extract_year(text),
           "citation_style": None, "n_references": None,
           "most_cited_reference": None, "times_cited": None}
    if refs:
        style, n_refs = citation_style_and_count(refs)
        ref, times = most_cited_reference(body, refs, style, n_refs)
        row.update({"citation_style": style, "n_references": n_refs,
                    "most_cited_reference": ref, "times_cited": times})
    return row
