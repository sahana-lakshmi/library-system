
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "v2")
books = []


@app.route("/")
def home():
    if VERSION == "v1":
        features = ["Add Books", "View Books"]
    elif VERSION == "v2":
        features = ["Add Books", "View Books", "Issue Books"]
    else:
        features = [
            "Add Books",
            "View Books",
            "Issue Books",
            "Return Books"
        ]

    return jsonify({
        "application": "Library Management System",
        "version": VERSION,
        "features": features
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": VERSION})


@app.route("/books", methods=["GET"])
def get_books():
    return jsonify(books)


@app.route("/books", methods=["POST"])
def add_book():
    data = request.get_json(silent=True) or {}

    book_id = data.get("id")
    title = data.get("title")
    author = data.get("author")

    if not book_id or not title or not author:
        return jsonify({
            "error": "ID, title and author are required"
        }), 400

    if any(book["id"] == book_id for book in books):
        return jsonify({"error": "Book ID already exists"}), 409

    book = {
        "id": book_id,
        "title": title,
        "author": author,
        "status": "Available",
        "student_id": None
    }

    books.append(book)
    return jsonify(book), 201


@app.route("/issue/<book_id>", methods=["POST"])
def issue_book(book_id):
    if VERSION == "v1":
        return jsonify({
            "error": "Issuing is available from v2"
        }), 404

    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")

    book = next((b for b in books if b["id"] == book_id), None)

    if book is None:
        return jsonify({"error": "Book not found"}), 404

    if not student_id:
        return jsonify({"error": "Student ID is required"}), 400

    if book["status"] != "Available":
        return jsonify({"error": "Book is not available"}), 409

    book["status"] = "Issued"
    book["student_id"] = student_id

    return jsonify(book)


@app.route("/return/<book_id>", methods=["POST"])
def return_book(book_id):
    if VERSION != "v3":
        return jsonify({
            "error": "Returning is available in v3"
        }), 404

    book = next((b for b in books if b["id"] == book_id), None)

    if book is None:
        return jsonify({"error": "Book not found"}), 404

    if book["status"] != "Issued":
        return jsonify({"error": "Book has not been issued"}), 409

    book["status"] = "Available"
    book["student_id"] = None

    return jsonify(book)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
