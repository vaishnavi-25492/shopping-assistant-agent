from flask import Flask, render_template, request
import json

app = Flask(__name__)


# Load products from JSON file
def load_products():
    with open("products.json", "r", encoding="utf-8") as file:
        return json.load(file)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():

    query = request.form.get("query", "").lower()

    products = load_products()

    # Find products matching the user's words
    matching_products = []

    for product in products:

        product_text = json.dumps(product).lower()

        if any(word in product_text for word in query.split()):
            matching_products.append(product)

    return render_template(
        "results.html",
        query=query,
        products=matching_products
    )


if __name__ == "__main__":
    app.run(debug=True)
