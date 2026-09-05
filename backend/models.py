# ============================================================
# DATABASE MODELS
# PROJECT: CROWDSOURCED PROBLEM-SOLVING PLATFORM
# ============================================================

from datetime import datetime

from extensions import db


# ============================================================
# USER MODEL
# ============================================================

class User(db.Model):

    __tablename__ = "users"

    # Primary Key
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Username
    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    # Email
    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    # Hashed Password
    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # User Role
    # Allowed values: "problemer" or "solver"
    role = db.Column(
        db.String(20),
        nullable=False
    )

    # Account Creation Time
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    problems = db.relationship(
        "Problem",
        backref="creator",
        lazy=True,
        foreign_keys="Problem.created_by"
    )

    solutions = db.relationship(
        "Solution",
        backref="solver",
        lazy=True,
        foreign_keys="Solution.submitted_by"
    )


    # --------------------------------------------------------
    # CONVERT USER TO DICTIONARY
    # --------------------------------------------------------

    def to_dict(self):

        return {

            "id": self.id,

            "username": self.username,

            "email": self.email,

            "role": self.role,

            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            )

        }


# ============================================================
# PROBLEM MODEL
# ============================================================

class Problem(db.Model):

    __tablename__ = "problems"


    # Primary Key
    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # Problem Title
    title = db.Column(
        db.String(255),
        nullable=False
    )


    # Original Problem Description
    description = db.Column(
        db.Text,
        nullable=False
    )


    # Preprocessed Text Used by ML
    cleaned_text = db.Column(
        db.Text
    )


    # --------------------------------------------------------
    # PRIMARY ML PREDICTION
    # --------------------------------------------------------

    # Highest-confidence predicted category
    predicted_category = db.Column(
        db.String(100)
    )


    # --------------------------------------------------------
    # ML PREDICTION CONFIDENCE
    # --------------------------------------------------------

    # Confidence of the primary prediction
    confidence = db.Column(
        db.Numeric(5, 2)
    )


    # --------------------------------------------------------
    # TOP 3 ML PREDICTIONS
    # --------------------------------------------------------

    # Stores the top 3 model predictions and probabilities
    top_predictions = db.Column(
        db.JSON
    )


    # --------------------------------------------------------
    # ASSIGNED ML DOMAINS
    # --------------------------------------------------------

    # Stores the actual domain(s) assigned to the problem
    # based on the confidence thresholds in prediction_module.py.
    #
    # Example:
    #
    # [
    #     {
    #         "category": "html / css",
    #         "confidence": 25.26
    #     },
    #     {
    #         "category": "javascript",
    #         "confidence": 25.10
    #     }
    # ]
    #
    # High-confidence problem:
    #
    # [
    #     {
    #         "category": "node.js",
    #         "confidence": 91.31
    #     }
    # ]

    predicted_domains = db.Column(
        db.JSON
    )


    # --------------------------------------------------------
    # USER WHO CREATED THE PROBLEM
    # --------------------------------------------------------

    created_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )


    # Creation Time
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    # Problem Status
    # open / closed / resolved
    status = db.Column(
        db.String(20),
        nullable=False,
        default="open"
    )


    # --------------------------------------------------------
    # RELATIONSHIP WITH SOLUTIONS
    # --------------------------------------------------------

    solutions = db.relationship(
        "Solution",
        backref="problem",
        lazy=True,
        cascade="all, delete-orphan"
    )


    # --------------------------------------------------------
    # CONVERT PROBLEM TO DICTIONARY
    # --------------------------------------------------------

    def to_dict(self):

        return {

            "id": self.id,

            "title": self.title,

            "description": self.description,

            "cleaned_text": self.cleaned_text,

            # Primary ML prediction
            "predicted_category": (
                self.predicted_category
            ),

            # Primary prediction confidence
            "confidence": (
                float(self.confidence)
                if self.confidence is not None
                else None
            ),

            # Top 3 model predictions
            "top_predictions": (
                self.top_predictions
                if self.top_predictions
                else []
            ),

            # Actual assigned domains
            "predicted_domains": (
                self.predicted_domains
                if self.predicted_domains
                else []
            ),

            "created_by": self.created_by,

            "creator": (
                self.creator.username
                if self.creator
                else None
            ),

            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),

            "status": self.status,

            "solution_count": len(
                self.solutions
            )

        }


# ============================================================
# SOLUTION MODEL
# ============================================================

class Solution(db.Model):

    __tablename__ = "solutions"


    # Primary Key
    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # Related Problem
    problem_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "problems.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )


    # Solution Content
    solution_text = db.Column(
        db.Text,
        nullable=False
    )


    # Solver Who Submitted the Solution
    submitted_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )


    # Submission Time
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    # --------------------------------------------------------
    # CONVERT SOLUTION TO DICTIONARY
    # --------------------------------------------------------

    def to_dict(self):

        return {

            "id": self.id,

            "problem_id": self.problem_id,

            "solution_text": self.solution_text,

            "submitted_by": self.submitted_by,

            "solver": (
                self.solver.username
                if self.solver
                else None
            ),

            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            )

        }