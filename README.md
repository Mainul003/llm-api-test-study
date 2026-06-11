# LLM API Test Study — Replication Package

> **Paper:** "Do LLMs Generate Adequate REST API Tests? An Empirical Comparison with Developer-Written Test Suites"
> **Author:** Md. Mainul Islam
> **Venue:** RASE 2026 — 1st International Workshop on Reliable and Trustworthy Automated Software Engineering, co-located with ASE 2026, Munich, Germany, October 12–16, 2026
> **Status:** Under review

![Status](https://img.shields.io/badge/status-under%20review-orange)
![Venue](https://img.shields.io/badge/venue-RASE%20%40%20ASE%202026-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## What this repo contains

Complete replication package for our empirical study comparing LLM-generated REST API test suites against developer-written test suites across 3 REST APIs.

```
llm-api-test-study/
├── scripts/
│   ├── api_servers.py           # 3 local REST API servers (Flask)
│   ├── 01_collect_dataset.py    # Dataset collection
│   ├── 02_generate_llm_tests.py # LLM test generation (Anthropic API)
│   ├── 03_create_collections.py # Builds all Postman collections
│   └── 05_analyse.py            # Metrics + LaTeX table output
├── collections/
│   ├── developer/               # Developer-written Postman collections
│   └── llm/                     # LLM-generated Postman collections
├── results/
│   └── final_results.json       # Aggregated metrics
├── paper/
│   └── mainul_rase_acm.tex      # Paper LaTeX source (ACM format)
└── README.md
```

---

## APIs Studied

| Project | Domain | Endpoints | Dev Tests | LLM Tests |
|---|---|---|---|---|
| TaskManager | Task management | 8 | 8 | 21 |
| ProductStore | E-commerce | 5 | 5 | 14 |
| UserVault | User/Auth | 6 | 5 | 18 |
| **Total** | | **19** | **18** | **53** |

---

## Key Results

### RQ1 — Endpoint Coverage

| Project | Dev EC (%) | LLM EC (%) | Δ |
|---|---|---|---|
| TaskManager | 50.0 | 100.0 | +50.0 |
| ProductStore | 40.0 | 40.0 | +0.0 |
| UserVault | 50.0 | 66.7 | +16.7 |
| **Mean** | **46.7** | **73.1** | **+26.4** |

### RQ2 — Defect Detection Rate

| Mutation type | Dev DDR (%) | LLM DDR (%) |
|---|---|---|
| M1: Status code replacement | 72.7 | 75.0 |
| M2: Required field omission | 59.7 | 78.0 |
| M3: Field type substitution | 56.7 | 76.0 |
| M4: Boundary value inversion | 52.7 | 52.0 |
| **Overall** | **64.7** | **70.0** |

**Key finding:** LLMs outperform developers on endpoint coverage (+26.4pp) and schema-based DDR (M1–M3), but converge on boundary faults (M4) where domain knowledge matters most.

---

## How to Reproduce

### Install requirements
```bash
pip install flask flask-cors requests pyyaml
npm install -g newman
```

### Run the experiment
```bash
# 1. Start local API servers
python3 scripts/api_servers.py &

# 2. Run developer tests
newman run collections/developer/taskmanager_dev_collection.json
newman run collections/developer/productstore_dev_collection.json
newman run collections/developer/uservault_dev_collection.json

# 3. Run LLM-generated tests
newman run collections/llm/taskmanager_llm_collection.json
newman run collections/llm/productstore_llm_collection.json
newman run collections/llm/uservault_llm_collection.json

# 4. Re-generate LLM tests (requires Anthropic API key)
export ANTHROPIC_API_KEY=your-key-here
python3 scripts/02_generate_llm_tests.py

# 5. Recalculate all metrics
python3 scripts/05_analyse.py
```

---

## LLM Prompt Used (Section 3.2 of paper)

```
You are a senior REST API test engineer. Given an API description, generate a 
COMPREHENSIVE Postman Collection v2.1 JSON test suite covering:
1. Happy-path tests for every endpoint
2. Error-path tests (invalid inputs, missing fields, wrong types)
3. Boundary tests (edge cases, empty arrays, limits)
4. Negative tests (non-existent IDs, malformed bodies)

Return ONLY valid Postman Collection v2.1 JSON.
```

Model: `claude-sonnet-4-20250514` | Temperature: `0` | Max tokens: `4000`

---

## Citation

```bibtex
@inproceedings{islam2026llmapitest,
  title     = {Do {LLMs} Generate Adequate {REST} {API} Tests?
               An Empirical Comparison with Developer-Written Test Suites},
  author    = {Islam, Md. Mainul},
  booktitle = {Proc. 1st International Workshop on Reliable and Trustworthy
               Automated Software Engineering (RASE) @ ASE 2026},
  year      = {2026},
  address   = {Munich, Germany}
}
```

---

**Contact:** Md. Mainul Islam — mainulfuad95@gmail.com
ORCID: [0009-0006-6368-2987](https://orcid.org/0009-0006-6368-2987)
Department of CSE, United International University, Dhaka, Bangladesh
