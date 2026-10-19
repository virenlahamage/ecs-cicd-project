
import os

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "1.1.0")
GIT_COMMIT = os.getenv("GIT_COMMIT", "local")
ENVIRONMENT = os.getenv("APP_ENV", "development")

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ECS CI/CD Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 50px 20px;
            color: #172033;
        }
        .container {
            max-width: 650px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 14px;
            box-shadow: 0 8px 25px rgba(0,0,0,.08);
        }
        h1 { color: #0f766e; }
        .status { color: #15803d; font-weight: bold; }
        .detail {
            padding: 12px;
            margin-top: 12px;
            background: #f8fafc;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ECS CI/CD Demo Application</h1>
        <p class="status">● Application is running</p>
        <div class="detail"><b>Version:</b> {{ version }}</div>
        <div class="detail"><b>Git commit:</b> {{ commit }}</div>
        <div class="detail"><b>Environment:</b> {{ environment }}</div>
        <div class="detail"><b>Platform:</b> Docker / Amazon ECS Fargate</div>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
    return render_template_string(
        HTML_PAGE,
        version=APP_VERSION,
        commit=GIT_COMMIT,
        environment=ENVIRONMENT,
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="healthy"), 200


@app.route("/version", methods=["GET"])
def version():
    return jsonify(
        app="ecs-cicd-demo",
        version=APP_VERSION,
        commit=GIT_COMMIT,
        environment=ENVIRONMENT,
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

