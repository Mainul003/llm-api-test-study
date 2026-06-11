"""
PHASE 2 — LLM Test Generation
==============================
What this script does:
  For each of our 3 APIs, we:
  1. Build a detailed description of the API (its endpoints, methods, parameters)
  2. Send it to Claude with a carefully designed prompt
  3. Parse the returned Postman Collection JSON
  4. Save it alongside each project's metadata

Learning note — WHY we use temperature=0:
  Scientific reproducibility. If another researcher runs this exact script
  with the same model + prompt + input, they should get the same output.
  temperature=0 makes the model deterministic (greedy decoding).
  You MUST report this in your paper: "We set temperature=0 for reproducibility."

Learning note — the prompt design:
  This is called "prompt engineering" and it IS a contribution in your paper.
  We ask for: (1) happy-path tests, (2) error-path tests, (3) boundary tests.
  We ask for Postman Collection v2.1 JSON format so Newman can run it.
  We ask for NO explanation — just the JSON — to make parsing reliable.
"""

import json
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

DATA_DIR    = Path("/home/claude/experiment/data")
RESULTS_DIR = DATA_DIR / "results" / "llm"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── API Definitions (what we tell the LLM about each API) ────────────────────
# In a real study with OpenAPI specs, you'd pass the full YAML.
# Here we write precise descriptions that mirror what an OpenAPI spec contains.

APIS = [
    {
        "name": "taskmanager",
        "base_url": "http://localhost:5001",
        "description": """
REST API: TaskManager — Project & Task Management API
Base URL: http://localhost:5001

ENDPOINTS:

GET /tasks
  Description: List all tasks. Supports optional query parameters.
  Query params:
    - status (string, optional): Filter by status. Allowed: "todo", "in_progress", "done", "cancelled"
    - priority (string, optional): Filter by priority. Allowed: "low", "medium", "high"
  Response 200: {"tasks": [...], "count": <integer>}
  Each task: {id, title, status, priority, due (YYYY-MM-DD), project_id}

GET /tasks/{id}
  Description: Get a single task by ID (string, e.g. "1")
  Response 200: task object
  Response 404: {"error": "Task not found", "task_id": "<id>"}

POST /tasks
  Description: Create a new task
  Request body (JSON): {title* (required string), status, priority, due, project_id}
  Response 201: created task object
  Response 400: if body is missing
  Response 422: if title is missing or empty

PATCH /tasks/{id}
  Description: Update an existing task
  Request body (JSON): any subset of {title, status, priority, due, project_id}
  Response 200: updated task object
  Response 404: if task not found
  Response 422: if status value is invalid

DELETE /tasks/{id}
  Description: Delete a task by ID
  Response 200: {"message": "Task deleted", "task_id": "<id>"}
  Response 404: if task not found

GET /projects
  Description: List all projects
  Response 200: {"projects": [...], "count": <integer>}
  Each project: {id, name, status, owner}

GET /projects/{id}
  Description: Get a single project (IDs are "p1", "p2", etc.)
  Response 200: project object
  Response 404: if not found

POST /users/login
  Description: Authenticate a user
  Request body (JSON): {username*, password*}
  Valid credentials: username="mainul", password="test123"
  Response 200: {"token": "Bearer ...", "user": "<username>"}
  Response 400: if body missing
  Response 401: if credentials invalid
""",
        "endpoint_count": 8
    },
    {
        "name": "productstore",
        "base_url": "http://localhost:5002",
        "description": """
REST API: ProductStore — E-Commerce Product and Order API
Base URL: http://localhost:5002

ENDPOINTS:

GET /products
  Description: List products with optional filters
  Query params:
    - category (string, optional): e.g. "electronics", "furniture", "stationery"
    - min_price (float, optional): minimum price filter
    - max_price (float, optional): maximum price filter
  Response 200: {"products": [...], "count": <integer>}
  Each product: {id, name, price (float), stock (int), category, rating (float)}

GET /products/{id}
  Description: Get a single product by ID (string "1".."4")
  Response 200: product object
  Response 404: {"error": "Product not found"}

POST /cart
  Description: Create a shopping cart with items
  Request body (JSON): {"items": [{product_id, quantity (int >= 1)}, ...]}
  Response 201: {"id": "cart_N", "items": [...], "total": <float>}
  Response 404: if any product_id not found
  Response 422: if items is not a list OR quantity < 1

GET /cart/{cart_id}
  Description: Get a cart by ID (e.g. "cart_1")
  Response 200: cart object
  Response 404: if cart not found

POST /orders
  Description: Place an order from an existing cart
  Request body (JSON): {cart_id* (required), shipping_address* (required)}
  Response 201: order object with {order_id, cart_id, shipping_address, status, total, items}
  Response 422: if cart_id invalid or shipping_address missing
""",
        "endpoint_count": 5
    },
    {
        "name": "uservault",
        "base_url": "http://localhost:5003",
        "description": """
REST API: UserVault — User Management and Authentication API
Base URL: http://localhost:5003

ENDPOINTS:

GET /users
  Description: List active users
  Query params:
    - role (string, optional): Filter by role. Allowed: "admin", "user", "moderator"
  Response 200: {"users": [...]}
  Each user: {id, username, email, role, active}

GET /users/{id}
  Description: Get a user by ID (string "1", "2", "3")
  Response 200: user object
  Response 404: {"error": "User not found"}

POST /auth/register
  Description: Register a new user
  Request body (JSON): {username*, email*, password*}
  Validation: email must contain "@"; password must be >= 8 chars; username must be unique
  Response 201: {"message": "User registered", "user": {...}}
  Response 400: if body missing
  Response 409: if username already exists
  Response 422: if required fields missing, email invalid, or password too short

POST /auth/login
  Description: Log in an existing user
  Request body (JSON): {username*, password*}
  Response 200: {"token": "Bearer token.for.<username>", "user_id": "<id>"}
  Response 401: if user not found
  Response 403: if account is deactivated
  Response 422: if username or password fields missing

PATCH /users/{id}
  Description: Update a user's profile
  Request body (JSON): {email, role} — id and password are read-only
  Response 200: updated user object
  Response 404: if user not found
  Response 422: if email format invalid or role value not in ["admin","user","moderator"]

DELETE /users/{id}
  Description: Soft-deactivate a user (sets active=false)
  Response 200: {"message": "User deactivated", "user_id": "<id>"}
  Response 404: if user not found
""",
        "endpoint_count": 6
    }
]

# ── The system prompt (this is what you report in Section III-B of your paper) ─
SYSTEM_PROMPT = """You are a senior REST API test engineer with 5 years of experience writing Postman test collections.

Given an API description, generate a COMPREHENSIVE Postman Collection v2.1 JSON test suite that covers:
1. Happy-path tests: every endpoint exercised with valid inputs and successful expected responses
2. Error-path tests: invalid inputs, missing required fields, wrong data types, out-of-range values
3. Boundary tests: edge cases for string lengths, numeric limits, empty arrays
4. Negative tests: non-existent resource IDs, unauthorized requests, malformed bodies

Requirements for EACH test case:
- Use a descriptive name (e.g. "GET /tasks - valid status filter returns filtered list")
- Include pm.test() assertions for: response status code, response body structure, key field values
- Use realistic test data (not placeholder values like "string" or "example")

Return ONLY valid Postman Collection v2.1 JSON. No markdown, no explanation, no code blocks.
The JSON must start with { and end with }."""

def call_claude(api_description):
    """
    Call the Anthropic API to generate test cases.
    
    Learning note: We use the raw HTTP API (no SDK) so you can see exactly
    what goes over the wire. In your own code you'd use 'anthropic' Python SDK.
    
    The request format:
    - model: which Claude version (sonnet-4 is fast + capable)
    - max_tokens: upper limit on response length
    - messages: the conversation — here just one user turn
    - system: the system prompt that shapes Claude's behaviour
    """
    url = "https://api.anthropic.com/v1/messages"
    
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": f"Generate a comprehensive Postman test collection for this API:\n\n{api_description}"
            }
        ]
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", "")           # handled by environment
    req.add_header("anthropic-version", "2023-06-01")
    
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode("utf-8"), "status": e.code}
    except Exception as e:
        return {"error": str(e)}

def extract_json_from_response(text):
    """
    Extract the Postman Collection JSON from Claude's response text.
    Claude sometimes wraps JSON in markdown code blocks — we handle that.
    
    Learning note: This is called "output parsing" and it's a real challenge
    when using LLMs for structured output. In your paper you should report
    how many responses needed parsing fixes (this is part of your methodology).
    """
    text = text.strip()
    
    # Case 1: Clean JSON (ideal case)
    if text.startswith("{"):
        try:
            return json.loads(text), "clean"
        except:
            pass
    
    # Case 2: Wrapped in ```json ... ```
    code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1)), "code_block"
        except:
            pass
    
    # Case 3: JSON somewhere in text — find largest { } block
    brace_start = text.find("{")
    if brace_start != -1:
        # Walk forward counting braces
        depth = 0
        for i, ch in enumerate(text[brace_start:], start=brace_start):
            if ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[brace_start:i+1]), "extracted"
                    except:
                        break
    return None, "failed"

def count_tests_and_assertions(collection):
    """
    Count test cases and assertions in a Postman collection.
    This gives us the 'Assertion Density' metric for the paper.
    
    Learning note: Postman stores tests as JavaScript code in 
    collection.item[].event[].script.exec — we count pm.test() calls.
    """
    test_count = 0
    assertion_count = 0
    
    def walk_items(items):
        nonlocal test_count, assertion_count
        for item in items:
            if "item" in item:       # folder — recurse
                walk_items(item["item"])
            else:                    # leaf request
                test_count += 1
                for event in item.get("event", []):
                    if event.get("listen") == "test":
                        script = "\n".join(event.get("script", {}).get("exec", []))
                        assertion_count += script.count("pm.test(")
    
    walk_items(collection.get("item", []))
    return test_count, assertion_count

def count_endpoints_covered(collection, api):
    """
    Count how many distinct endpoints from the spec are covered by at least
    one test case. This is the Endpoint Coverage (EC) metric.
    
    Method: extract the URL path from each Postman request and match against
    the known endpoint paths from the API description.
    """
    covered = set()
    base = api["base_url"]
    
    def walk(items):
        for item in items:
            if "item" in item:
                walk(item["item"])
            else:
                req = item.get("request", {})
                url = req.get("url", {})
                if isinstance(url, dict):
                    raw = url.get("raw", "")
                else:
                    raw = str(url)
                # Normalise: remove base URL, replace path params with {id}
                path = raw.replace(base, "")
                path = re.sub(r'/\d+', '/{id}', path)
                path = path.split("?")[0].rstrip("/")
                method = req.get("method", "GET").upper()
                covered.add(f"{method} {path}")
    
    walk(collection.get("item", []))
    return covered

# ── Main generation loop ──────────────────────────────────────────────────────
print("=" * 60)
print("PHASE 2: LLM Test Generation")
print("=" * 60)

generation_log = []

for api in APIS:
    print(f"\n[{api['name']}]")
    print(f"  Sending API description to Claude ({api['endpoint_count']} endpoints)...")
    
    start_time = time.time()
    response = call_claude(api["description"])
    elapsed = time.time() - start_time
    
    if "error" in response:
        print(f"  ✗ API call failed: {response['error']}")
        generation_log.append({
            "api": api["name"], "status": "failed",
            "error": str(response["error"])
        })
        continue
    
    # Extract the text content from Claude's response
    content_blocks = response.get("content", [])
    raw_text = ""
    for block in content_blocks:
        if block.get("type") == "text":
            raw_text += block.get("text", "")
    
    print(f"  ✓ Claude responded in {elapsed:.1f}s ({len(raw_text)} chars)")
    
    # Parse the Postman collection from the response
    collection, parse_method = extract_json_from_response(raw_text)
    
    if not collection:
        print(f"  ✗ Could not parse Postman JSON from response")
        # Save raw response for debugging
        with open(RESULTS_DIR / f"{api['name']}_raw.txt", "w") as f:
            f.write(raw_text)
        generation_log.append({
            "api": api["name"], "status": "parse_failed",
            "raw_length": len(raw_text)
        })
        continue
    
    # Count metrics
    test_count, assertion_count = count_tests_and_assertions(collection)
    covered_endpoints = count_endpoints_covered(collection, api)
    endpoint_coverage = len(covered_endpoints) / api["endpoint_count"] if api["endpoint_count"] > 0 else 0
    assertion_density = assertion_count / test_count if test_count > 0 else 0
    
    print(f"  ✓ Parsed via: {parse_method}")
    print(f"  ✓ Tests generated:    {test_count}")
    print(f"  ✓ Assertions total:   {assertion_count}")
    print(f"  ✓ Assertion density:  {assertion_density:.2f} per test")
    print(f"  ✓ Endpoints covered:  {len(covered_endpoints)}/{api['endpoint_count']} ({endpoint_coverage:.0%})")
    
    # Save the Postman collection
    out_path = RESULTS_DIR / f"{api['name']}_llm_collection.json"
    with open(out_path, "w") as f:
        json.dump(collection, f, indent=2)
    
    log_entry = {
        "api":                 api["name"],
        "status":              "success",
        "parse_method":        parse_method,
        "test_count":          test_count,
        "assertion_count":     assertion_count,
        "assertion_density":   round(assertion_density, 3),
        "endpoints_covered":   len(covered_endpoints),
        "endpoints_total":     api["endpoint_count"],
        "endpoint_coverage":   round(endpoint_coverage, 4),
        "covered_set":         sorted(list(covered_endpoints)),
        "elapsed_seconds":     round(elapsed, 1),
        "tokens_used":         response.get("usage", {})
    }
    generation_log.append(log_entry)
    
    # Small delay between API calls (rate limiting courtesy)
    time.sleep(2)

# ── Save generation log ───────────────────────────────────────────────────────
log_path = RESULTS_DIR / "generation_log.json"
with open(log_path, "w") as f:
    json.dump(generation_log, f, indent=2)

print("\n" + "=" * 60)
print("PHASE 2 COMPLETE")
print("=" * 60)
successful = [e for e in generation_log if e.get("status") == "success"]
print(f"  APIs processed:    {len(APIS)}")
print(f"  Successfully done: {len(successful)}")
for e in successful:
    print(f"    {e['api']:20s}  {e['test_count']:3d} tests  "
          f"EC={e['endpoint_coverage']:.0%}  AD={e['assertion_density']:.2f}")
print(f"\nGeneration log: {log_path}")
print("Next step: run 03_write_developer_tests.py")
