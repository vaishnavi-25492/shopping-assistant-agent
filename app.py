from flask import Flask, render_template, request
from google import genai
import os
import json

app = Flask(__name__)


# --------------------------------
# Load products
# --------------------------------
def load_products():
    try:
        with open("products.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print("Product loading error:", e)
        return []


# --------------------------------
# Simple product matching
# --------------------------------
def find_products(query, products):

    query = query.lower()

    results = []

    # Detect category
    if "phone" in query or "mobile" in query:
        category = "phone"
    elif "laptop" in query:
        category = "laptop"
    else:
        category = None

    # Extract budget
    budget = None

    words = query.replace("₹", "").replace(",", "").split()

    for i, word in enumerate(words):

        if word.isdigit():
            number = int(word)

            # Example:
            # phone under 30000
            if number >= 1000:
                budget = number
                break

    for product in products:

        # Category filter
        if category:
            if product["category"].lower() != category:
                continue

        # Budget filter
        if budget:
            if product["price"] > budget:
                continue

        results.append(product)

    return results


# --------------------------------
# AI Shopping Agent
# --------------------------------
def shopping_agent(user_query, products):

    api_key = os.environ.get("GEMINI_API_KEY")

    # If Gemini key is missing
    if not api_key:

        return (
            "AI service is not configured yet.\n\n"
            "Please add GEMINI_API_KEY in Render Environment Variables."
        )

    if not products:

        return (
            "I could not find products matching your requirements."
        )

    try:

        client = genai.Client(api_key=api_key)

        product_text = json.dumps(
            products,
            indent=2,
            ensure_ascii=False
        )

        prompt = f"""
You are a helpful AI Shopping Assistant.

User request:
{user_query}

Available products:
{product_text}

Choose the best product for the user.

Consider:
1. User budget
2. Product category
3. Rating
4. Features
5. User requirements

Give a simple answer.

Use this format:

BEST PRODUCT:
Product name

PRICE:
₹price

RATING:
rating

WHY:
Explain in 2 or 3 simple sentences why this product is suitable.

ALTERNATIVE:
Give another suitable product if available.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        print("Gemini error:", e)

        return (
            "The AI recommendation service is temporarily unavailable.\n\n"
            "However, matching products are shown below."
        )


# --------------------------------
# Home page
# --------------------------------
@app.route("/", methods=["GET"])
def home():

    return render_template("index.html")


# --------------------------------
# Search
# --------------------------------
@app.route("/search", methods=["POST"])
def search():

    query = request.form.get("query", "").strip()

    if not query:

        return render_template(
            "index.html",
            error="Please enter a product requirement."
        )

    products = load_products()

    # Find matching products
    matching_products = find_products(
        query,
        products
    )

    # Get AI recommendation
    recommendation = shopping_agent(
        query,
        matching_products
    )

    return render_template(
        "results.html",
        query=query,
        products=matching_products,
        recommendation=recommendation
    )


# --------------------------------
# Run application
# --------------------------------
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
