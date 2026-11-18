"""Read PDF files into plain text."""

import glob
import os
import unicodedata

import pymupdf


def read_pdf(path):
    """Return (text, n_pages). Text is NFKC-normalised to undo typographic
    ligatures (ﬁ, ﬂ, ﬀ) that would break regular-expression searches."""
    with pymupdf.open(path) as doc:
        text = "\n".join(page.get_text() for page in doc)
        n_pages = len(doc)
    return unicodedata.normalize("NFKC", text), n_pages


def read_folder(folder):
    """Read every PDF in a folder. Returns {file name: text}."""
    return {os.path.basename(p): read_pdf(p)[0]
            for p in sorted(glob.glob(os.path.join(folder, "*.pdf")))}
