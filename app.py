from flask import jsonify
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/health")
def health():
    return jsonify({"message": "API is running"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
