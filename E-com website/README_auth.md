# JWT Authentication & Authorization

## Overview

This API uses **JWT (JSON Web Tokens)** for authentication and **role-based access control (RBAC)** for authorization. There are two roles: `customer` and `admin`.

---

## Setup

Install the new dependencies:

```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

Or install everything from requirements.txt:

```bash
pip install -r requirements.txt
```

---

## How to Register, Log In, and Use the Token in Swagger UI

### 1. Register a user

`POST /auth/register`

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "secret123",
  "role": "customer"
}
```

To create an admin:

```json
{
  "username": "admin1",
  "email": "admin@example.com",
  "password": "adminpass",
  "role": "admin"
}
```

The response returns the created user **without** the password.

---

### 2. Log in and get a token

`POST /auth/token`

This endpoint accepts **OAuth2 form data** (not JSON):

| Field      | Value         |
|------------|---------------|
| `username` | alice         |
| `password` | secret123     |

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

The token expires after **30 minutes**. It contains `user_id` and `role` in its payload.

---

### 3. Use the token in Swagger UI

1. Open `http://localhost:8000/docs`
2. Click the **Authorize** button (top right, lock icon)
3. Enter `Bearer <your_token>` in the **HTTPBearer** field, or just paste the token in the **OAuth2PasswordBearer** field
4. Click **Authorize** — all subsequent requests will include the token automatically

---

## Route Protection Summary

| Route | Method | Access |
|-------|--------|--------|
| `GET /products` | GET | **Public** — no token needed |
| `GET /products/{id}` | GET | **Public** |
| `GET /products/search` | GET | **Public** |
| `POST /products` | POST | **Admin only** |
| `PUT /products/{id}` | PUT | **Admin only** |
| `DELETE /products/{id}` | DELETE | **Admin only** |
| `POST /products/{id}/restock` | POST | **Admin only** |
| `GET /cart/{customer_id}` | GET | **Logged-in user** |
| `POST /cart/{customer_id}/add` | POST | **Logged-in user** |
| `POST /cart/{customer_id}/remove` | POST | **Logged-in user** |
| `PUT /cart/{customer_id}/update` | PUT | **Logged-in user** |
| `DELETE /cart/{customer_id}/clear` | DELETE | **Logged-in user** |
| `POST /orders` | POST | **Logged-in user** |
| `GET /orders/mine` | GET | **Logged-in customer** (own orders only) |
| `GET /orders` | GET | **Admin only** |
| `GET /orders/{order_id}` | GET | **Admin** or **order owner** |
| `POST /orders/{order_id}/confirm` | POST | **Admin** or **order owner** |
| `POST /orders/{order_id}/cancel` | POST | **Admin** or **order owner** |
| `GET /orders/{order_id}/summary` | GET | **Admin** or **order owner** |
| `GET /orders/customer/{customer_id}` | GET | **Admin only** |

---

## Ownership Check

When a customer creates an order, the `user_id` from their JWT is stored as `owner_user_id` on the order record.

- `GET /orders/mine` — returns only orders where `owner_user_id` matches the token's `user_id`.
- `GET /orders/{order_id}` — if the caller is a customer and `owner_user_id` does not match their `user_id`, the API returns **403 Forbidden**.
- The same ownership check applies to confirm, cancel, apply-coupon, and summary endpoints.

Admins bypass all ownership checks and can access any order.

---

## Key Files

| File | Purpose |
|------|---------|
| `routes/auth_routes.py` | `/auth/register` and `/auth/token` endpoints |
| `dependencies.py` | `get_current_user` and `require_admin` FastAPI dependencies |
| `models/user.py` | `User` dataclass + in-memory `UserStore` |
| `schemas/user.py` | Pydantic schemas for register/login/response |
| `utils/auth.py` | `hash_password`, `verify_password`, `create_access_token`, `decode_access_token` |
