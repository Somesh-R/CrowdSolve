from flask import Flask, render_template, jsonify
from flask_cors import CORS

from config import Config
from models import db
from routes import api


app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Initialize database
db.init_app(app)

# Register API routes
app.register_blueprint(api, url_prefix="/api")


# ==========================================================
# FRONTEND PAGE ROUTES
# ==========================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/problemer-dashboard")
def problemer_dashboard():
    return render_template("problemer_dashboard.html")


@app.route("/solver-dashboard")
def solver_dashboard():
    return render_template("solver_dashboard.html")


# ==========================================================
# DATABASE TEST ROUTE
# ==========================================================

@app.route("/database-test")
def database_test():

    try:

        with db.engine.connect() as connection:
            pass

        return jsonify({
            "success": True,
            "message": "Database connection successful."
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ==========================================================
# API HEALTH CHECK
# ==========================================================

@app.route("/api/health")
def health_check():

    return jsonify({
        "success": True,
        "message": "CrowdSolve backend is running successfully."
    })


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("CROWDSOLVE BACKEND SERVER")
    print("=" * 70)

    print("\nServer starting...\n")

    print("Local access:")
    print("http://127.0.0.1:5000")

    print("\nAPI health check:")
    print("http://127.0.0.1:5000/api/health")

    print("\nDatabase connection test:")
    print("http://127.0.0.1:5000/database-test")

    print("\nNetwork access:")
    print("http://YOUR_COMPUTER_IP:5000")

    print("\n" + "=" * 70 + "\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )