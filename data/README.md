# Data

## `pdfs/` — source articles

Six open-access articles published by Frontiers, on placebo/nocebo effects, depression and mental health. They are redistributed here under their Creative Commons Attribution (CC BY) licence; all rights remain with their authors.

| File | First author | Year | DOI |
|---|---|---|---|
| `fpsyg-08-00308.pdf` | Corsi | 2017 | [10.3389/fpsyg.2017.00308](https://doi.org/10.3389/fpsyg.2017.00308) |
| `fpsyg-09-01240.pdf` | Tommasi | 2018 | [10.3389/fpsyg.2018.01240](https://doi.org/10.3389/fpsyg.2018.01240) |
| `fpsyg-11-01354.pdf` | Bernstein | 2020 | [10.3389/fpsyg.2020.01354](https://doi.org/10.3389/fpsyg.2020.01354) |
| `fpsyg-12-639236.pdf` | Vambheim | 2021 | [10.3389/fpsyg.2021.639236](https://doi.org/10.3389/fpsyg.2021.639236) |
| `fpsyt-14-1301143.pdf` | Seymour | 2024 | [10.3389/fpsyt.2023.1301143](https://doi.org/10.3389/fpsyt.2023.1301143) |
| `fpubh-10-1045777.pdf` | Wang | 2023 | [10.3389/fpubh.2022.1045777](https://doi.org/10.3389/fpubh.2022.1045777) |

## `extracted_table.csv` — pipeline output

One row per article.

| Column | Method | Description |
|---|---|---|
| `file` | — | PDF file name |
| `title` | LLM | Article title |
| `first_author` | LLM | Surname of the first author |
| `year` | regex | Publication year ("Published: dd Month yyyy") |
| `doi` | regex | Digital Object Identifier |
| `study_type` | LLM | `experimental`, `observational`, `methodological`, `computational` or `review/theoretical` |
| `n_participants` | LLM | Human participants recruited (sum of all experiments); null if none |
| `country` | LLM + normalisation | Country of the first author's affiliation |
| `citation_style` | regex | `author-year` or `numeric` |
| `n_references` | regex | Number of entries in the reference list |
| `most_cited_reference` | regex | Reference cited most often in the body |
| `times_cited` | regex | Times that reference is cited in the body |

## `ground_truth.csv` — manual review

Values checked by hand in each article for the four LLM fields that are validated (`first_author`, `study_type`, `n_participants`, `country`). An empty `n_participants` means the article recruited no participants.
