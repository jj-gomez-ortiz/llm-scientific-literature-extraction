# Prompt and model design

Notes on the iterations that led to the final configuration.

## Model choice

| Model | Result |
|---|---|
| `Qwen/Qwen2.5-1.5B-Instruct` | Fast, but confused the **first author** with the **corresponding author** and failed to find the number of participants |
| `Qwen/Qwen2.5-3B-Instruct` | 23–24 of 24 validated fields correct on the 6 articles (see below) → **selected** |

Both run locally with Hugging Face `transformers` (Apple GPU via `mps`, `float16`). Greedy decoding (`do_sample=False`) makes the output deterministic and reproducible.

## Input: only the start of the article

The model receives the text before the "Keywords" heading: title, authors, affiliations and abstract. That is where all requested fields are, and it keeps the prompt short (faster, and less room for the model to pick values from the reference list).

## Prompt decisions

1. **JSON-only answer with fixed keys**, parsed with a regex + `json.loads`. If parsing fails, every field becomes null instead of breaking the pipeline.
2. **Closed list of categories** for `study_type`, each with a one-line definition. Free-text answers were inconsistent.
3. **Explicit disambiguation** for the first author: *"in the author list printed below the title (not the editor, reviewer or corresponding author)"*. Frontiers' first page also lists editors and reviewers.
4. **Sum participants across experiments**, and `null` when there are none, to avoid the model returning sample sizes of cited studies.
5. **"Do not invent values"**: missing information must be null.
6. **Field order matters:** with `title` as the first key, the other fields got worse. Asking for the title **last** fixed it.

## Sensitivity to label wording

| Version | JSON keys and `study_type` labels | Result |
|---|---|---|
| Original (course submission) | Spanish (`metodológico`, `revisión/teórico`...) with English definitions | 24 / 24 |
| Current | English (`methodological`, `review/theoretical`...) | 23 / 24 |

The only changes are the language of the JSON keys and category labels (the instructions were already in English). The difference is one borderline article (Tommasi et al., 2018, which evaluates Bayes' theorem for depression tests). It shows that small models are sensitive to wording, and that a 6-article sample is too small to choose between prompt variants: tuning the prompt until this sample scores 100 % would just overfit it. A larger labelled set is the right next step.

## Post-processing

Country names are normalised (`USA` → `United States`, `UK` → `United Kingdom`, ...), since the model does not always use the same form.

## Split between rules and LLM

| Field | Why |
|---|---|
| DOI, year, citation style, references, most cited reference | Fixed formats → regular expressions are exact, fast and auditable |
| Title, first author, study type, participants, country | Require reading comprehension → LLM |
