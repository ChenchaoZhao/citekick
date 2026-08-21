# Literature Search API Survey

Web research survey (subagent research, Aug 2026) of candidate literature/paper query APIs for the `citekick` tool. Verdicts are for this use case: a Python CLI run on a laptop with occasional batch queries.

## Free and keyless (default sources)

| Source | Docs | Auth | Rate limits | Notes |
| --- | --- | --- | --- | --- |
| Semantic Scholar | [api.semanticscholar.org](https://www.semanticscholar.org/product/api) | Free key (optional) | ~1 req/s shared | Citations, abstracts, paper graph |
| arXiv | [arxiv.org/help/api](https://arxiv.org/help/api) | None (`mailto=` advised) | no hard limits | Preprints; metadata + abstracts |
| PubMed (NCBI E-utilities) | [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | None | ~3 req/s without key | Biomedical journals + abstracts |
| Crossref | [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | None (`mailto=` polite pool) | 5–10 req/s | DOI resolver; metadata; sparse abstracts |
| Europe PMC | [RESTful Web Service](https://europepmc.org/RestfulWebService) | None | ~5 req/s | Bio full text, citations, preprints, bio-annotations |
| OpenReview | [docs.openreview.net](https://docs.openreview.net/) | None (guest read) | no hard limits | ICLR/NeurIPS/ICML incl. reviews/decisions |
| DBLP | [DBLP search API](https://dblp.org/faq/How+to+use+the+dblp+search+API.html) | None | ~1 req/s | CS-venue metadata; no abstracts/citations |

## Almost free (opt-in, not default)

| Source | Docs | Auth | Rate limits | Notes |
| --- | --- | --- | --- | --- |
| OpenAlex | [developers.openalex.org](https://developers.openalex.org/) | Free API key | Budget-based (~$1/day free) | ~320M works; citations, preprints, OA/PDF links; abstracts as inverted index |

## Free but conditional — surveyed, not added

| Source | Why not added |
| --- | --- |
| bioRxiv/medRxiv | [api.biorxiv.org](https://api.biorxiv.org/) — free, but no keyword search (date/DOI/iteration only); metadata overlaps Europe PMC |
| PLOS | [api.plos.org](https://api.plos.org/) — single-publisher OA full text only; narrow corpus |
| CORE | [core.ac.uk](https://core.ac.uk/documentation/api) — free key but non-commercial licence; overlaps OpenAlex/Europe PMC |
| OpenAIRE | [Graph API](https://graph.openaire.eu/docs/apis/graph-api/) — EU-centric grant linkage; legacy Search API deprecated |
| DataCite | [support.datacite.org/docs/api](https://support.datacite.org/docs/api) — metadata-only DOI lookup (datasets/software/preprints) |
| Zenodo | [developers.zenodo.org](https://developers.zenodo.org/) — dataset/software discovery, not paper index |
| Hugging Face Papers | [huggingface.co/api/papers](https://huggingface.co/api/papers) — arXiv-derived trending/search + GitHub links |
| ACL Anthology | [aclanthology.org/faq/api](https://aclanthology.org/faq/api/) — no hosted REST API; Python package + local metadata |
| Internet Archive Scholar | [fatcat guide](https://scholar.archive.org/fatcat/guide) — free but experimental/low-availability |
| UniProt | [API docs](https://www.uniprot.org/api-documentation) — protein data + literature citations; enrichment, not search |
| IEDB Query API | [query-api.iedb.org](https://query-api.iedb.org) — epitope/antibody assay data with PubMed refs; data DB, not search |
| PubChem PUG | [PUG REST docs](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest) — not a literature search API; compound↔PMID linking only |
| OpenCitations (COCI) | [api.opencitations.net](https://api.opencitations.net) — citation lookup by DOI only, not keyword search |
| Unpaywall | [unpaywall.org/api/v2](https://unpaywall.org/api/v2) — OA-location lookup by DOI only |

### Not suitable — surveyed, excluded

| Source | Why excluded |
| --- | --- |
| Google Scholar | No official API; scraping violates ToS and is fragile (CAPTCHAs) |
| Papers with Code | Shut down by Meta, Jul 2025; only static archives remain |
| Lens.org | Subscription-gated; 14-day trial, manual approval; patents angle only if required |
| Dimensions | Institutional subscription only |
| BASE | IP-allowlist auth; incompatible with a portable laptop CLI |
| Paperity | No public search API |
| Scilit | Manual token grant; owned by MDPI (neutrality concern) |
| NeurIPS/ICLR proceedings (direct) | No API; use OpenReview instead |
| OAS / SAbDab / PLAbDab | Antibody data resources (sequences/structures), not literature search APIs |
