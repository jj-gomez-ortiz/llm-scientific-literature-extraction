"""Extract semantic fields from the first page of an article with a local Hugging Face LLM."""

import json
import re

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.utils import logging as hf_logging

DEFAULT_MODEL = "Qwen/Qwen2.5-3B-Instruct"

PROMPT = """Read the beginning of a scientific article and extract these fields.
Answer ONLY with a JSON object with these keys:
- "first_author": surname of the FIRST author in the author list printed below the title (not the editor, reviewer or corresponding author)
- "study_type": exactly one of:
    "experimental" (the authors ran an experiment with participants),
    "observational" (survey or cohort data collected by the authors),
    "methodological" (proposes or evaluates a statistical/measurement method using published data),
    "computational" (machine learning / NLP models on datasets or corpora),
    "review/theoretical" (review, theory or conceptual analysis without new data)
- "n_participants": total number of human participants recruited by the authors (sum all experiments), as an integer; null if there were no participants
- "country": country of the first author's affiliation, in English
- "title": the title of the article
If a field is not in the text, use null. Do not invent values.

ARTICLE:
{text}"""

LLM_FIELDS = ["first_author", "study_type", "n_participants", "country", "title"]

# The LLM does not always write a country the same way ("USA" / "United States")
COUNTRY_ALIASES = {"usa": "United States", "us": "United States", "u.s.": "United States",
                   "u.s.a.": "United States", "united states of america": "United States",
                   "uk": "United Kingdom", "u.k.": "United Kingdom", "england": "United Kingdom",
                   "pr china": "China", "p.r. china": "China"}


def normalise_country(country):
    if not country:
        return None
    return COUNTRY_ALIASES.get(country.strip().lower(), country.strip())


def article_start(text):
    """Title, authors, affiliations and abstract: everything before 'Keywords'."""
    m = re.search(r"Keywords|KEYWORDS", text)
    fragment = text[:m.start()] if m else text[:5000]
    return re.sub(r"[ \t]+", " ", fragment)


def parse_json(answer):
    """Extract the JSON object from the answer; if it fails, every field is null."""
    m = re.search(r"\{.*\}", answer, re.S)
    try:
        data = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        data = {}
    return {field: data.get(field) for field in LLM_FIELDS}


class LLMExtractor:
    """Runs a local instruction-tuned model (no data leaves the machine)."""

    def __init__(self, model_name=DEFAULT_MODEL, device=None):
        hf_logging.disable_progress_bar()
        self.device = device or ("mps" if torch.backends.mps.is_available()
                                 else "cuda" if torch.cuda.is_available() else "cpu")
        dtype = torch.float16 if self.device != "cpu" else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = (AutoModelForCausalLM.from_pretrained(model_name, dtype=dtype)
                      .to(self.device).eval())

    def ask(self, text, max_tokens=250):
        """Raw model answer for one article (greedy decoding, deterministic)."""
        messages = [{"role": "user", "content": PROMPT.format(text=article_start(text))}]
        inputs = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
        ).to(self.device)
        with torch.no_grad():
            output = self.model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False)
        return self.tokenizer.decode(output[0][inputs["input_ids"].shape[1]:],
                                     skip_special_tokens=True)

    def extract(self, text):
        fields = parse_json(self.ask(text))
        fields["country"] = normalise_country(fields["country"])
        return fields
