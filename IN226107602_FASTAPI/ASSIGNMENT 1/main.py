from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# ------------------------------
# Basic Home Endpoint
# ------------------------------
@app.get("/")
def home():
    return {"message": "Welcome to FastAPI Assignment"}

# ------------------------------
# Math Operations
# ------------------------------
@app.get("/add")
def add(a: int, b: int):
    return {"result": a + b}

@app.get("/subtract")
def subtract(a: int, b: int):
    return {"result": a - b}

@app.get("/multiply")
def multiply(a: int, b: int):
    return {"result": a * b}

@app.get("/divide")
def divide(a: int, b: int):
    if b == 0:
        return {"error": "Cannot divide by zero"}
    return {"result": a / b}

# ------------------------------
# Products Data
# ------------------------------
products = [
    {"id": 1, "name": "Mouse", "price": 500, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 100, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB", "price": 800, "category": "Electronics", "in_stock": False}
]

# ------------------------------
# Filter Products Endpoint
# ------------------------------
@app.get("/products/filter")
def filter_products(max_price: int = Query(None), min_price: int = Query(None), category: str = Query(None)):
    result = products
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]
    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]
    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]
    return result

# ------------------------------
# Get Product Price by ID
# ------------------------------
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}

# ------------------------------
# Customer Feedback
# ------------------------------
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

feedback = []

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    # Check if product exists
    if not any(p["id"] == data.product_id for p in products):
        return {"error": "Invalid product ID"}
    
    feedback.append(data.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }

# ------------------------------
# Product Summary
# ------------------------------
@app.get("/products/summary")
def product_summary():
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]
    most_expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))
    
    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {"name": most_expensive["name"], "price": most_expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "categories": categories
    }

# ------------------------------
# Get All Products
# ------------------------------
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

# ------------------------------
# Add Product (POST)
# ------------------------------
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


@app.post("/products")
def add_product(product: NewProduct):

    # Check duplicate product name
    for p in products:
        if p["name"].lower() == product.name.lower():
            return {"error": "Product already exists"}

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added",
        "product": new_product
    }


# ------------------------------
# Product Audit Endpoint
# (Place ABOVE /products/{product_id})
# ------------------------------
@app.get("/products/audit")
def product_audit():

    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]

    stock_value = sum(p["price"] * 10 for p in in_stock_list)

    priciest = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {
            "name": priciest["name"],
            "price": priciest["price"]
        }
    }


# ------------------------------
# Get Product by ID
# ------------------------------
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for p in products:
        if p["id"] == product_id:
            return p

    return {"error": "Product not found"}


# ------------------------------
# Update Product
# ------------------------------
@app.put("/products/{product_id}")
def update_product(product_id: int, price: int = None, in_stock: bool = None):

    for p in products:

        if p["id"] == product_id:

            if price is not None:
                p["price"] = price

            if in_stock is not None:
                p["in_stock"] = in_stock

            return {
                "message": "Product updated",
                "product": p
            }

    return {"error": "Product not found"}


# ------------------------------
# Delete Product
# ------------------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for p in products:

        if p["id"] == product_id:
            products.remove(p)
            return {"message": f"Product '{p['name']}' deleted"}

    return {"error": "Product not found"}
