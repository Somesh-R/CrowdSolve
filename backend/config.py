# ============================================================
# APPLICATION CONFIGURATION
# PROJECT: CROWDSOURCED PROBLEM-SOLVING PLATFORM
# ============================================================

import os

from dotenv import load_dotenv


# Load variables from the .env file
load_dotenv()


class Config:

    # --------------------------------------------------------
    # FLASK SECRET KEY
    # --------------------------------------------------------

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "fallback_development_secret_key"
    )


    # --------------------------------------------------------
    # POSTGRESQL DATABASE CONFIGURATION
    # --------------------------------------------------------

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"
    )


    # Disable unnecessary tracking to improve performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False