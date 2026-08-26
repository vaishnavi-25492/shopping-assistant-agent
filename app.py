from flask import Flask, render_template, request
from google import genai
import os
import json

app = Flask(__name__)


# Gemini client
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


# Load products
def load_products():
    with open("products.json", "r", encoding="utf-8") as file:
        return json.load(file)


# AI Shopping Assistant
def shopping_agent(user_query, products):

    product_text = json.dumps(products, indent=2)

    prompt = f"""
You are an AI Shopping Assistant.

User request:
{user_query}

Available products:
{product_text}

Choose the best products for the user.

Consider:
- User's budget
- Product category
- User requirements
- Product rating
- Product features

Give a simple recommendation.

Return the answer in this format:

Best Product:
Product name

Price:
Product price

Why:
Short explanation

Alternative:
Another suitable product
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():

    query = request.form.get("query", "")

    products = load_products()

    # Ask Gemini to recommend products
    recommendation = shopping_agent(query, products)

    return render_template(
        "results.html",
        query=query,
        products=products,
        recommendation=recommendation
    )


if __name__ == "__main__":
    app.run(debug=True)
