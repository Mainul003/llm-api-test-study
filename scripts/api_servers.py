"""
LOCAL API SERVERS — Three realistic REST APIs for experiment
=============================================================
Learning note: In real research you use Docker containers or live demo servers.
Here we build three representative APIs that mirror the kinds of projects
you would find on GitHub. Each has intentional bugs seeded for the DDR metric.

API 1 — TaskManager  (project management domain — your expertise)
  Endpoints: /tasks, /tasks/{id}, /projects, /users/login
  Bugs: 3 seeded mutations

API 2 — ProductStore  (e-commerce, like AutoBill/RGS work at WebAlive)
  Endpoints: /products, /products/{id}, /cart, /orders
  Bugs: 3 seeded mutations

API 3 — UserVault  (user/auth management)
  Endpoints: /users, /users/{id}, /auth/login, /auth/register
  Bugs: 3 seeded mutations

We run these locally so the experiment is fully reproducible.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading, time, sys

# ───────────────────────────────────────────────────────────────────────────────
# API 1: TaskManager (port 5001)
# ───────────────────────────────────────────────────────────────────────────────
app1 = Flask("taskmanager")
CORS(app1)

TASKS = {
    "1": {"id": "1", "title": "Write unit tests",  "status": "todo",       "priority": "high",   "due": "2026-07-01", "project_id": "p1"},
    "2": {"id": "2", "title": "Code review",        "status": "in_progress","priority": "medium", "due": "2026-06-15", "project_id": "p1"},
    "3": {"id": "3", "title": "Deploy to staging",  "status": "done",       "priority": "low",    "due": "2026-06-10", "project_id": "p2"},
    "4": {"id": "4", "title": "Fix login bug",       "status": "todo",       "priority": "high",   "due": "2026-06-20", "project_id": "p2"},
}
PROJECTS = {
    "p1": {"id": "p1", "name": "Alpha Release",  "status": "active",   "owner": "mainul"},
    "p2": {"id": "p2", "name": "Beta Dashboard", "status": "planning", "owner": "mainul"},
}

@app1.get("/tasks")
def list_tasks():
    status_filter = request.args.get("status")
    priority_filter = request.args.get("priority")
    tasks = list(TASKS.values())
    if status_filter:
        tasks = [t for t in tasks if t["status"] == status_filter]
    if priority_filter:
        tasks = [t for t in tasks if t["priority"] == priority_filter]
    return jsonify({"tasks": tasks, "count": len(tasks)}), 200

@app1.get("/tasks/<task_id>")
def get_task(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({"error": "Task not found", "task_id": task_id}), 404
    return jsonify(task), 200

@app1.post("/tasks")
def create_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    if "title" not in data:
        return jsonify({"error": "Field 'title' is required"}), 422
    if len(data.get("title","")) == 0:
        return jsonify({"error": "Title cannot be empty"}), 422
    new_id = str(len(TASKS) + 1)
    task = {
        "id":         new_id,
        "title":      data["title"],
        "status":     data.get("status", "todo"),
        "priority":   data.get("priority", "medium"),
        "due":        data.get("due", None),
        "project_id": data.get("project_id", None),
    }
    TASKS[new_id] = task
    return jsonify(task), 201

@app1.patch("/tasks/<task_id>")
def update_task(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    data = request.get_json() or {}
    valid_statuses = ["todo", "in_progress", "done", "cancelled"]
    if "status" in data and data["status"] not in valid_statuses:
        return jsonify({"error": f"Invalid status. Must be one of {valid_statuses}"}), 422
    task.update({k: v for k, v in data.items() if k != "id"})
    return jsonify(task), 200

@app1.delete("/tasks/<task_id>")
def delete_task(task_id):
    if task_id not in TASKS:
        return jsonify({"error": "Task not found"}), 404
    del TASKS[task_id]
    return jsonify({"message": "Task deleted", "task_id": task_id}), 200

@app1.get("/projects")
def list_projects():
    return jsonify({"projects": list(PROJECTS.values()), "count": len(PROJECTS)}), 200

@app1.get("/projects/<project_id>")
def get_project(project_id):
    project = PROJECTS.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(project), 200

@app1.post("/users/login")
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    if data.get("username") == "mainul" and data.get("password") == "test123":
        return jsonify({"token": "Bearer eyJhbGciOiJIUzI1NiJ9.test", "user": "mainul"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app1.get("/health")
def health1():
    return jsonify({"status": "ok", "service": "taskmanager"}), 200

# ───────────────────────────────────────────────────────────────────────────────
# API 2: ProductStore (port 5002)
# ───────────────────────────────────────────────────────────────────────────────
app2 = Flask("productstore")
CORS(app2)

PRODUCTS = {
    "1": {"id": "1", "name": "Laptop Pro",     "price": 1299.99, "stock": 15, "category": "electronics", "rating": 4.5},
    "2": {"id": "2", "name": "Wireless Mouse", "price": 29.99,   "stock": 150,"category": "electronics", "rating": 4.2},
    "3": {"id": "3", "name": "Desk Lamp",       "price": 45.00,   "stock": 80, "category": "furniture",   "rating": 4.0},
    "4": {"id": "4", "name": "Notebook Set",    "price": 12.50,   "stock": 200,"category": "stationery",  "rating": 4.7},
}
CARTS = {}   # cart_id -> {items: [{product_id, qty}], total}

@app2.get("/products")
def list_products():
    category = request.args.get("category")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    products = list(PRODUCTS.values())
    if category:
        products = [p for p in products if p["category"] == category]
    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]
    return jsonify({"products": products, "count": len(products)}), 200

@app2.get("/products/<product_id>")
def get_product(product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200

@app2.post("/cart")
def create_cart():
    data = request.get_json() or {}
    items = data.get("items", [])
    if not isinstance(items, list):
        return jsonify({"error": "'items' must be an array"}), 422
    cart_id = f"cart_{len(CARTS)+1}"
    total = 0.0
    validated_items = []
    for item in items:
        pid = str(item.get("product_id", ""))
        qty = item.get("quantity", 1)
        if pid not in PRODUCTS:
            return jsonify({"error": f"Product '{pid}' not found"}), 404
        if not isinstance(qty, int) or qty < 1:
            return jsonify({"error": "Quantity must be a positive integer"}), 422
        total += PRODUCTS[pid]["price"] * qty
        validated_items.append({"product_id": pid, "quantity": qty,
                                  "unit_price": PRODUCTS[pid]["price"]})
    cart = {"id": cart_id, "items": validated_items, "total": round(total, 2)}
    CARTS[cart_id] = cart
    return jsonify(cart), 201

@app2.get("/cart/<cart_id>")
def get_cart(cart_id):
    cart = CARTS.get(cart_id)
    if not cart:
        return jsonify({"error": "Cart not found"}), 404
    return jsonify(cart), 200

@app2.post("/orders")
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    cart_id = data.get("cart_id")
    if not cart_id or cart_id not in CARTS:
        return jsonify({"error": "Valid cart_id required"}), 422
    address = data.get("shipping_address")
    if not address:
        return jsonify({"error": "'shipping_address' is required"}), 422
    order = {
        "order_id":         f"ord_{len(CARTS)}",
        "cart_id":          cart_id,
        "shipping_address": address,
        "status":           "confirmed",
        "total":            CARTS[cart_id]["total"],
        "items":            CARTS[cart_id]["items"],
    }
    return jsonify(order), 201

@app2.get("/health")
def health2():
    return jsonify({"status": "ok", "service": "productstore"}), 200

# ───────────────────────────────────────────────────────────────────────────────
# API 3: UserVault (port 5003)
# ───────────────────────────────────────────────────────────────────────────────
app3 = Flask("uservault")
CORS(app3)

USERS = {
    "1": {"id": "1", "username": "mainul",   "email": "mainulfuad95@gmail.com", "role": "admin",  "active": True},
    "2": {"id": "2", "username": "alice",    "email": "alice@example.com",       "role": "user",   "active": True},
    "3": {"id": "3", "username": "bob",      "email": "bob@example.com",         "role": "user",   "active": False},
}

@app3.get("/users")
def list_users():
    role_filter = request.args.get("role")
    users = [u for u in USERS.values() if u["active"]]
    if role_filter:
        users = [u for u in users if u["role"] == role_filter]
    # Remove sensitive info from list
    return jsonify({"users": [{k: v for k,v in u.items() if k != "password"}
                               for u in users]}), 200

@app3.get("/users/<user_id>")
def get_user(user_id):
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({k: v for k,v in user.items() if k != "password"}), 200

@app3.post("/auth/register")
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    required = ["username", "email", "password"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Field '{field}' is required"}), 422
    # Check email format
    if "@" not in data["email"]:
        return jsonify({"error": "Invalid email format"}), 422
    # Check password strength
    if len(data["password"]) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 422
    # Check username uniqueness
    existing = [u for u in USERS.values() if u["username"] == data["username"]]
    if existing:
        return jsonify({"error": "Username already exists"}), 409
    new_id = str(len(USERS) + 1)
    user = {"id": new_id, "username": data["username"],
            "email": data["email"], "role": "user", "active": True}
    USERS[new_id] = user
    return jsonify({"message": "User registered", "user": user}), 201

@app3.post("/auth/login")
def user_login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    if "username" not in data or "password" not in data:
        return jsonify({"error": "username and password required"}), 422
    # For demo: valid if username exists in our DB
    user = next((u for u in USERS.values() if u["username"] == data["username"]), None)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    if not user["active"]:
        return jsonify({"error": "Account is deactivated"}), 403
    return jsonify({"token": f"Bearer token.for.{data['username']}", "user_id": user["id"]}), 200

@app3.patch("/users/<user_id>")
def update_user(user_id):
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json() or {}
    if "email" in data and "@" not in data["email"]:
        return jsonify({"error": "Invalid email format"}), 422
    if "role" in data and data["role"] not in ["admin", "user", "moderator"]:
        return jsonify({"error": "Invalid role"}), 422
    user.update({k: v for k,v in data.items() if k not in ["id","password"]})
    return jsonify({k: v for k,v in user.items() if k != "password"}), 200

@app3.delete("/users/<user_id>")
def delete_user(user_id):
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
    USERS[user_id]["active"] = False   # soft delete
    return jsonify({"message": "User deactivated", "user_id": user_id}), 200

@app3.get("/health")
def health3():
    return jsonify({"status": "ok", "service": "uservault"}), 200


def run_server(app, port):
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Start all three servers in background threads
    for app, port in [(app1, 5001), (app2, 5002), (app3, 5003)]:
        t = threading.Thread(target=run_server, args=(app, port), daemon=True)
        t.start()
        time.sleep(0.3)
    print("All 3 API servers started:")
    print("  TaskManager  → http://localhost:5001")
    print("  ProductStore → http://localhost:5002")
    print("  UserVault    → http://localhost:5003")
    print("\nPress Ctrl+C to stop.")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("Servers stopped.")
