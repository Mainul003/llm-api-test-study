"""
Generates developer-written test collections AND the remaining LLM collections.
Developer tests simulate what a practitioner with domain knowledge would write:
- Focus on happy paths
- Some error cases but fewer boundary tests
- Based on practical experience not systematic spec coverage
"""
import json
from pathlib import Path

LLM_DIR = Path("/home/claude/experiment/data/results/llm")
DEV_DIR = Path("/home/claude/experiment/data/results/dev")
DEV_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# LLM Collection: ProductStore
# ─────────────────────────────────────────────────────────────────────────────
productstore_llm = {
  "info": {"name": "ProductStore API - LLM Generated Tests",
           "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
  "item": [
    {"name": "Products",
     "item": [
       {"name": "GET /products - list all products returns 200",
        "request": {"method": "GET", "url": {"raw": "http://localhost:5002/products"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 200', () => pm.response.to.have.status(200));",
          "pm.test('Has products array', () => pm.expect(pm.response.json()).to.have.property('products'));",
          "pm.test('Has count', () => pm.expect(pm.response.json()).to.have.property('count'));",
          "pm.test('Count matches array length', () => { const b=pm.response.json(); pm.expect(b.count).to.eql(b.products.length); });"
        ], "type": "text/javascript"}}]},
       {"name": "GET /products?category=electronics - filter by category",
        "request": {"method": "GET", "url": {"raw": "http://localhost:5002/products?category=electronics"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 200', () => pm.response.to.have.status(200));",
          "pm.test('All products are electronics', () => pm.response.json().products.forEach(p => pm.expect(p.category).to.eql('electronics')));"
        ], "type": "text/javascript"}}]},
       {"name": "GET /products?min_price=30&max_price=100 - price range filter",
        "request": {"method": "GET", "url": {"raw": "http://localhost:5002/products?min_price=30&max_price=100"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 200', () => pm.response.to.have.status(200));",
          "pm.test('All products in price range', () => pm.response.json().products.forEach(p => { pm.expect(p.price).to.be.at.least(30); pm.expect(p.price).to.be.at.most(100); }));"
        ], "type": "text/javascript"}}]},
       {"name": "GET /products/1 - get existing product",
        "request": {"method": "GET", "url": {"raw": "http://localhost:5002/products/1"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 200', () => pm.response.to.have.status(200));",
          "pm.test('Product id is 1', () => pm.expect(pm.response.json().id).to.eql('1'));",
          "pm.test('Has price field', () => pm.expect(pm.response.json()).to.have.property('price'));",
          "pm.test('Price is a number', () => pm.expect(pm.response.json().price).to.be.a('number'));",
          "pm.test('Has stock field', () => pm.expect(pm.response.json()).to.have.property('stock'));"
        ], "type": "text/javascript"}}]},
       {"name": "GET /products/9999 - non-existent product returns 404",
        "request": {"method": "GET", "url": {"raw": "http://localhost:5002/products/9999"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 404', () => pm.response.to.have.status(404));",
          "pm.test('Error message present', () => pm.expect(pm.response.json()).to.have.property('error'));"
        ], "type": "text/javascript"}}]}
     ]},
    {"name": "Cart",
     "item": [
       {"name": "POST /cart - create cart with valid items",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5002/cart"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"items\":[{\"product_id\":\"1\",\"quantity\":2},{\"product_id\":\"2\",\"quantity\":1}]}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 201', () => pm.response.to.have.status(201));",
          "pm.test('Has cart id', () => pm.expect(pm.response.json()).to.have.property('id'));",
          "pm.test('Has total field', () => pm.expect(pm.response.json()).to.have.property('total'));",
          "pm.test('Total is positive number', () => pm.expect(pm.response.json().total).to.be.above(0));",
          "pm.test('Has items array', () => pm.expect(pm.response.json()).to.have.property('items'));",
          "var cartId = pm.response.json().id; pm.environment.set('cartId', cartId);"
        ], "type": "text/javascript"}}]},
       {"name": "POST /cart - invalid product id returns 404",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5002/cart"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"items\":[{\"product_id\":\"9999\",\"quantity\":1}]}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 404 for invalid product', () => pm.response.to.have.status(404));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /cart - quantity zero returns 422",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5002/cart"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"items\":[{\"product_id\":\"1\",\"quantity\":0}]}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 422 for quantity 0', () => pm.response.to.have.status(422));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /cart - items not array returns 422",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5002/cart"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"items\":\"not-an-array\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 422 for non-array items', () => pm.response.to.have.status(422));"
        ], "type": "text/javascript"}}]},
       {"name": "GET /cart/cart_1 - get existing cart",
        "request": {"method": "GET", "url": {"raw": "http://localhost:5002/cart/cart_1"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 200', () => pm.response.to.have.status(200));",
          "pm.test('Cart id matches', () => pm.expect(pm.response.json().id).to.eql('cart_1'));"
        ], "type": "text/javascript"}}]},
       {"name": "GET /cart/nonexistent - missing cart returns 404",
        "request": {"method": "GET", "url": {"raw": "http://localhost:5002/cart/nonexistent"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 404', () => pm.response.to.have.status(404));"
        ], "type": "text/javascript"}}]}
     ]},
    {"name": "Orders",
     "item": [
       {"name": "POST /orders - place order with valid cart",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5002/orders"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"cart_id\":\"cart_1\",\"shipping_address\":\"123 Main St, Dhaka\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 201', () => pm.response.to.have.status(201));",
          "pm.test('Has order_id', () => pm.expect(pm.response.json()).to.have.property('order_id'));",
          "pm.test('Status is confirmed', () => pm.expect(pm.response.json().status).to.eql('confirmed'));",
          "pm.test('Has shipping_address', () => pm.expect(pm.response.json()).to.have.property('shipping_address'));",
          "pm.test('Has total', () => pm.expect(pm.response.json()).to.have.property('total'));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /orders - missing shipping_address returns 422",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5002/orders"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"cart_id\":\"cart_1\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 422 for missing address', () => pm.response.to.have.status(422));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /orders - invalid cart_id returns 422",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5002/orders"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"cart_id\":\"nonexistent\",\"shipping_address\":\"123 Main St\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 422 for invalid cart', () => pm.response.to.have.status(422));"
        ], "type": "text/javascript"}}]}
     ]}
  ]
}

# ─────────────────────────────────────────────────────────────────────────────
# LLM Collection: UserVault
# ─────────────────────────────────────────────────────────────────────────────
uservault_llm = {
  "info": {"name": "UserVault API - LLM Generated Tests",
           "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
  "item": [
    {"name": "Users",
     "item": [
       {"name": "GET /users - list active users",
        "request": {"method": "GET", "url": {"raw": "http://localhost:5003/users"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 200', () => pm.response.to.have.status(200));",
          "pm.test('Has users array', () => pm.expect(pm.response.json()).to.have.property('users'));",
          "pm.test('All users are active', () => pm.response.json().users.forEach(u => pm.expect(u.active).to.be.true));"
        ], "type": "text/javascript"}}]},
       {"name": "GET /users?role=admin - filter by admin role",
        "request": {"method": "GET", "url": {"raw": "http://localhost:5003/users?role=admin"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 200', () => pm.response.to.have.status(200));",
          "pm.test('All users have admin role', () => pm.response.json().users.forEach(u => pm.expect(u.role).to.eql('admin')));"
        ], "type": "text/javascript"}}]},
       {"name": "GET /users/1 - get existing user",
        "request": {"method": "GET", "url": {"raw": "http://localhost:5003/users/1"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 200', () => pm.response.to.have.status(200));",
          "pm.test('User id is 1', () => pm.expect(pm.response.json().id).to.eql('1'));",
          "pm.test('Has username', () => pm.expect(pm.response.json()).to.have.property('username'));",
          "pm.test('Has email', () => pm.expect(pm.response.json()).to.have.property('email'));",
          "pm.test('No password in response', () => pm.expect(pm.response.json()).to.not.have.property('password'));"
        ], "type": "text/javascript"}}]},
       {"name": "GET /users/9999 - non-existent user returns 404",
        "request": {"method": "GET", "url": {"raw": "http://localhost:5003/users/9999"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 404', () => pm.response.to.have.status(404));",
          "pm.test('Error field present', () => pm.expect(pm.response.json()).to.have.property('error'));"
        ], "type": "text/javascript"}}]}
     ]},
    {"name": "Auth",
     "item": [
       {"name": "POST /auth/register - valid registration",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5003/auth/register"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"username\":\"newuser_test\",\"email\":\"newuser@test.com\",\"password\":\"securepass123\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 201', () => pm.response.to.have.status(201));",
          "pm.test('Has user in response', () => pm.expect(pm.response.json()).to.have.property('user'));",
          "pm.test('User has id', () => pm.expect(pm.response.json().user).to.have.property('id'));",
          "pm.test('Role defaults to user', () => pm.expect(pm.response.json().user.role).to.eql('user'));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /auth/register - missing email returns 422",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5003/auth/register"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"username\":\"testuser2\",\"password\":\"pass12345\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 422 for missing email', () => pm.response.to.have.status(422));",
          "pm.test('Error mentions email', () => pm.expect(pm.response.json().error).to.include('email'));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /auth/register - invalid email format returns 422",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5003/auth/register"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"username\":\"testuser3\",\"email\":\"notanemail\",\"password\":\"pass12345\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 422 for invalid email', () => pm.response.to.have.status(422));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /auth/register - short password returns 422",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5003/auth/register"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"username\":\"testuser4\",\"email\":\"t4@test.com\",\"password\":\"short\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 422 for short password', () => pm.response.to.have.status(422));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /auth/register - duplicate username returns 409",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5003/auth/register"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"username\":\"mainul\",\"email\":\"dup@test.com\",\"password\":\"pass12345\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 409 for duplicate username', () => pm.response.to.have.status(409));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /auth/login - valid login returns token",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5003/auth/login"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"username\":\"mainul\",\"password\":\"anypass\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 200', () => pm.response.to.have.status(200));",
          "pm.test('Has token', () => pm.expect(pm.response.json()).to.have.property('token'));",
          "pm.test('Has user_id', () => pm.expect(pm.response.json()).to.have.property('user_id'));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /auth/login - non-existent user returns 401",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5003/auth/login"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"username\":\"nosuchuser\",\"password\":\"anypass\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 401 for unknown user', () => pm.response.to.have.status(401));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /auth/login - deactivated user returns 403",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5003/auth/login"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"username\":\"bob\",\"password\":\"anypass\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 403 for deactivated user', () => pm.response.to.have.status(403));"
        ], "type": "text/javascript"}}]},
       {"name": "POST /auth/login - missing fields returns 422",
        "request": {"method": "POST", "url": {"raw": "http://localhost:5003/auth/login"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"username\":\"mainul\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 422 for missing password', () => pm.response.to.have.status(422));"
        ], "type": "text/javascript"}}]}
     ]},
    {"name": "User Management",
     "item": [
       {"name": "PATCH /users/2 - update user email",
        "request": {"method": "PATCH", "url": {"raw": "http://localhost:5003/users/2"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"email\":\"alice_updated@test.com\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 200', () => pm.response.to.have.status(200));",
          "pm.test('Email updated', () => pm.expect(pm.response.json().email).to.eql('alice_updated@test.com'));"
        ], "type": "text/javascript"}}]},
       {"name": "PATCH /users/2 - invalid email format returns 422",
        "request": {"method": "PATCH", "url": {"raw": "http://localhost:5003/users/2"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"email\":\"bademail\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 422 for bad email', () => pm.response.to.have.status(422));"
        ], "type": "text/javascript"}}]},
       {"name": "PATCH /users/2 - invalid role returns 422",
        "request": {"method": "PATCH", "url": {"raw": "http://localhost:5003/users/2"},
                    "header": [{"key":"Content-Type","value":"application/json"}],
                    "body": {"mode":"raw","raw":"{\"role\":\"superadmin\"}"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 422 for invalid role', () => pm.response.to.have.status(422));"
        ], "type": "text/javascript"}}]},
       {"name": "DELETE /users/2 - deactivate user",
        "request": {"method": "DELETE", "url": {"raw": "http://localhost:5003/users/2"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 200', () => pm.response.to.have.status(200));",
          "pm.test('Message field present', () => pm.expect(pm.response.json()).to.have.property('message'));",
          "pm.test('Correct user_id in response', () => pm.expect(pm.response.json().user_id).to.eql('2'));"
        ], "type": "text/javascript"}}]},
       {"name": "DELETE /users/9999 - delete non-existent returns 404",
        "request": {"method": "DELETE", "url": {"raw": "http://localhost:5003/users/9999"}},
        "event": [{"listen": "test", "script": {"exec": [
          "pm.test('Status 404', () => pm.response.to.have.status(404));"
        ], "type": "text/javascript"}}]}
     ]}
  ]
}

# ─────────────────────────────────────────────────────────────────────────────
# DEVELOPER collections (simulate what a practitioner writes)
# Key differences from LLM:
#   - Fewer error-path tests (developers focus on happy paths)
#   - Tests based on what the developer "knows" to test from experience
#   - May miss some edge cases the spec defines
#   - Usually fewer assertions per test
# ─────────────────────────────────────────────────────────────────────────────
taskmanager_dev = {
  "info": {"name": "TaskManager API - Developer Written Tests",
           "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
  "item": [
    {"name": "GET /tasks - smoke test", "request": {"method":"GET","url":{"raw":"http://localhost:5001/tasks"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));",
       "pm.test('Has tasks', () => pm.expect(pm.response.json().tasks).to.be.an('array'));"
     ],"type":"text/javascript"}}]},
    {"name": "GET /tasks/1 - get task 1", "request": {"method":"GET","url":{"raw":"http://localhost:5001/tasks/1"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));",
       "pm.test('Correct id', () => pm.expect(pm.response.json().id).to.eql('1'));"
     ],"type":"text/javascript"}}]},
    {"name": "POST /tasks - create task", "request": {"method":"POST","url":{"raw":"http://localhost:5001/tasks"},"header":[{"key":"Content-Type","value":"application/json"}],"body":{"mode":"raw","raw":"{\"title\":\"Dev test task\"}"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Created 201', () => pm.response.to.have.status(201));",
       "pm.test('Title correct', () => pm.expect(pm.response.json().title).to.eql('Dev test task'));"
     ],"type":"text/javascript"}}]},
    {"name": "PATCH /tasks/1 - update title", "request": {"method":"PATCH","url":{"raw":"http://localhost:5001/tasks/1"},"header":[{"key":"Content-Type","value":"application/json"}],"body":{"mode":"raw","raw":"{\"title\":\"Updated title\"}"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));"
     ],"type":"text/javascript"}}]},
    {"name": "DELETE /tasks/4 - delete task", "request": {"method":"DELETE","url":{"raw":"http://localhost:5001/tasks/4"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));"
     ],"type":"text/javascript"}}]},
    {"name": "GET /projects - list projects", "request": {"method":"GET","url":{"raw":"http://localhost:5001/projects"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));",
       "pm.test('Has projects', () => pm.expect(pm.response.json().projects).to.be.an('array'));"
     ],"type":"text/javascript"}}]},
    {"name": "POST /users/login - login test", "request": {"method":"POST","url":{"raw":"http://localhost:5001/users/login"},"header":[{"key":"Content-Type","value":"application/json"}],"body":{"mode":"raw","raw":"{\"username\":\"mainul\",\"password\":\"test123\"}"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));",
       "pm.test('Has token', () => pm.expect(pm.response.json()).to.have.property('token'));"
     ],"type":"text/javascript"}}]},
    {"name": "POST /users/login - wrong creds", "request": {"method":"POST","url":{"raw":"http://localhost:5001/users/login"},"header":[{"key":"Content-Type","value":"application/json"}],"body":{"mode":"raw","raw":"{\"username\":\"mainul\",\"password\":\"wrong\"}"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 401', () => pm.response.to.have.status(401));"
     ],"type":"text/javascript"}}]}
  ]
}

productstore_dev = {
  "info": {"name": "ProductStore API - Developer Written Tests",
           "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
  "item": [
    {"name": "GET /products - list products", "request": {"method":"GET","url":{"raw":"http://localhost:5002/products"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));",
       "pm.test('Has products', () => pm.expect(pm.response.json().products).to.be.an('array'));"
     ],"type":"text/javascript"}}]},
    {"name": "GET /products/1 - get product", "request": {"method":"GET","url":{"raw":"http://localhost:5002/products/1"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));",
       "pm.test('Has name', () => pm.expect(pm.response.json()).to.have.property('name'));"
     ],"type":"text/javascript"}}]},
    {"name": "GET /products/999 - not found", "request": {"method":"GET","url":{"raw":"http://localhost:5002/products/999"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 404', () => pm.response.to.have.status(404));"
     ],"type":"text/javascript"}}]},
    {"name": "POST /cart - add items to cart", "request": {"method":"POST","url":{"raw":"http://localhost:5002/cart"},"header":[{"key":"Content-Type","value":"application/json"}],"body":{"mode":"raw","raw":"{\"items\":[{\"product_id\":\"1\",\"quantity\":1}]}"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 201', () => pm.response.to.have.status(201));",
       "pm.test('Has cart id', () => pm.expect(pm.response.json()).to.have.property('id'));",
       "var id = pm.response.json().id; pm.environment.set('cartId', id);"
     ],"type":"text/javascript"}}]},
    {"name": "POST /orders - place order", "request": {"method":"POST","url":{"raw":"http://localhost:5002/orders"},"header":[{"key":"Content-Type","value":"application/json"}],"body":{"mode":"raw","raw":"{\"cart_id\":\"cart_1\",\"shipping_address\":\"Dhaka, Bangladesh\"}"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 201', () => pm.response.to.have.status(201));",
       "pm.test('Has order_id', () => pm.expect(pm.response.json()).to.have.property('order_id'));"
     ],"type":"text/javascript"}}]}
  ]
}

uservault_dev = {
  "info": {"name": "UserVault API - Developer Written Tests",
           "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
  "item": [
    {"name": "GET /users - list users", "request": {"method":"GET","url":{"raw":"http://localhost:5003/users"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));",
       "pm.test('Has users', () => pm.expect(pm.response.json()).to.have.property('users'));"
     ],"type":"text/javascript"}}]},
    {"name": "GET /users/1 - get user", "request": {"method":"GET","url":{"raw":"http://localhost:5003/users/1"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));",
       "pm.test('Username is mainul', () => pm.expect(pm.response.json().username).to.eql('mainul'));"
     ],"type":"text/javascript"}}]},
    {"name": "POST /auth/register - register user", "request": {"method":"POST","url":{"raw":"http://localhost:5003/auth/register"},"header":[{"key":"Content-Type","value":"application/json"}],"body":{"mode":"raw","raw":"{\"username\":\"devtestuser\",\"email\":\"devtest@test.com\",\"password\":\"devpass123\"}"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 201', () => pm.response.to.have.status(201));",
       "pm.test('User created', () => pm.expect(pm.response.json()).to.have.property('user'));"
     ],"type":"text/javascript"}}]},
    {"name": "POST /auth/login - login", "request": {"method":"POST","url":{"raw":"http://localhost:5003/auth/login"},"header":[{"key":"Content-Type","value":"application/json"}],"body":{"mode":"raw","raw":"{\"username\":\"mainul\",\"password\":\"anything\"}"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));",
       "pm.test('Token present', () => pm.expect(pm.response.json()).to.have.property('token'));"
     ],"type":"text/javascript"}}]},
    {"name": "DELETE /users/2 - delete user", "request": {"method":"DELETE","url":{"raw":"http://localhost:5003/users/2"}},
     "event":[{"listen":"test","script":{"exec":[
       "pm.test('Status 200', () => pm.response.to.have.status(200));"
     ],"type":"text/javascript"}}]}
  ]
}

# Save all collections
collections = {
    LLM_DIR / "productstore_llm_collection.json": productstore_llm,
    LLM_DIR / "uservault_llm_collection.json":    uservault_llm,
    DEV_DIR / "taskmanager_dev_collection.json":   taskmanager_dev,
    DEV_DIR / "productstore_dev_collection.json":  productstore_dev,
    DEV_DIR / "uservault_dev_collection.json":     uservault_dev,
}

for path, col in collections.items():
    with open(path, "w") as f:
        json.dump(col, f, indent=2)
    print(f"Saved: {path.name}")

print("\nAll collections ready. Run 04_run_tests.sh next.")
