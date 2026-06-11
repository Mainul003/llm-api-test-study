# LLM API Test Study — Replication Package

> **Paper:** "Do LLMs Generate Adequate REST API Tests? An Empirical Comparison with Developer-Written Test Suites"  
> **Authors:** Md. Mainul Islam, A.K.M. Muzahidul Islam  
> **Target venue:** ASE 2026 NIER Track

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
│   └── mainul_nier_final.tex    # Paper LaTeX source
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
| TaskManager | 50.0 | 112.5 | +62.5 |
| ProductStore | 40.0 | 40.0 | +0.0 |
| UserVault | 50.0 | 66.7 | +16.7 |
| **Mean** | **46.7** | **73.1** | **+26.4** |

### RQ2 — Defect Detection Rate

| Mutation type | Dev (%) | LLM (%) |
|---|---|---|
| M1: Status code replacement | 72.7 | 75.0 |
| M2: Required field omission | 59.7 | 78.0 |
| M3: Field type substitution | 56.7 | 76.0 |
| M4: Boundary value inversion | 52.7 | 52.0 |
| **Overall** | **64.7** | **70.0** |

**Key finding:** LLMs outperform developers on endpoint coverage (+26.4pp) and schema-based DDR, but are near-parity on boundary faults where domain knowledge matters.

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

# 4. Re-generate LLM tests (needs Anthropic API key)
export ANTHROPIC_API_KEY=your-key-here
python3 scripts/02_generate_llm_tests.py

# 5. Recalculate all metrics
python3 scripts/05_analyse.py
```

---

## LLM Prompt (Section III-B of paper)

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
  title     = {Do {LLMs} Generate Adequate {REST} {API} Tests?},
  author    = {Islam, Md. Mainul and Islam, A.K.M. Muzahidul},
  booktitle = {ASE 2026 NIER Track},
  year      = {2026}
}
```

**Contact:** mainulfuad95@gmail.com
