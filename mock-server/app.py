import json
import os
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_PATH = Path(__file__).parent / "data" / "customers.json"

with open(DATA_PATH) as f:
    CUSTOMERS: list[dict] = json.load(f)

CUSTOMERS_BY_ID: dict[str, dict] = {c["customer_id"]: c for c in CUSTOMERS}


@app.route("/api/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/customers")
def list_customers():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    start = (page - 1) * limit
    end = start + limit

    return jsonify({
        "data": CUSTOMERS[start:end],
        "total": len(CUSTOMERS),
        "page": page,
        "limit": limit,
    })


@app.route("/api/customers/<customer_id>")
def get_customer(customer_id: str):
    customer = CUSTOMERS_BY_ID.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer)


if __name__ == "__main__":
    debug = os.getenv("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug)
