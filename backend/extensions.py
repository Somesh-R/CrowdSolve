# ============================================================
# FLASK EXTENSIONS
# PROJECT: CROWDSOURCED PROBLEM-SOLVING PLATFORM
# ============================================================

from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO


# ============================================================
# SQLALCHEMY DATABASE OBJECT
# ============================================================

db = SQLAlchemy()


# ============================================================
# SOCKET.IO OBJECT
# ============================================================

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading"
)