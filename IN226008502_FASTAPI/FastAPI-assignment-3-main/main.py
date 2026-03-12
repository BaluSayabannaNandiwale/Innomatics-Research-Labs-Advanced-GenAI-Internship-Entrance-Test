from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel

app = FastAPI()

# -----------------------------
# Product Model
# -----------------------------

class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


# -----------------------------
# Initial Product Data
# -----------------------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]


# -----------------------------
# Helper Function
# -----------------------------

def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None


# -----------------------------
# GET all products
# -----------------------------

@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


# -----------------------------
# POST add new product (Q1)
# -----------------------------

@app.post("/products")
def add_product(product: NewProduct, response: Response):

    # duplicate name check
    for p in products:
        if p["name"].lower() == product.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product already exists"}

    next_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": next_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    response.status_code = status.HTTP_201_CREATED

    return {
        "message": "Product added",
        "product": new_product
    }


# -----------------------------
# Q5 — Audit endpoint
# MUST be above /products/{product_id}
# -----------------------------

@app.get("/products/audit")
def product_audit():

    in_stock_products = [p for p in products if p["in_stock"]]
    out_stock_products = [p for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_products),
        "out_of_stock_names": [p["name"] for p in out_stock_products],
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


# -----------------------------
# BONUS — Discount endpoint
# -----------------------------

@app.put("/products/discount")
def apply_discount(
        category: str = Query(...),
        discount_percent: int = Query(..., ge=1, le=99)
):

    updated_products = []

    for p in products:
        if p["category"] == category:
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated_products.append(p)

    if not updated_products:
        return {"message": f"No products found in category {category}"}

    return {
        "message": f"{discount_percent}% discount applied to {category}",
        "updated_count": len(updated_products),
        "updated_products": updated_products
    }


# -----------------------------
# GET single product
# -----------------------------

@app.get("/products/{product_id}")
def get_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    return product


# -----------------------------
# PUT update product (Q2)
# -----------------------------

@app.put("/products/{product_id}")
def update_product(
        product_id: int,
        price: int | None = None,
        in_stock: bool | None = None,
        response: Response = None
):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {
        "message": "Product updated",
        "product": product
    }


# -----------------------------
# DELETE product (Q3)
# -----------------------------

@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {
        "message": f"Product '{product['name']}' deleted"
    }