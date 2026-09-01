# ============================================================
# CROWDSOLVE API ROUTES
# ============================================================
# Handles:
#   - Authentication
#   - Problem submission
#   - ML classification
#   - Problem retrieval
#   - Solution submission
#   - Solution retrieval
#   - Categories
# ============================================================

import os
import sys
from functools import wraps

from flask import Blueprint, request, jsonify

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from sqlalchemy import or_

from extensions import db

from models import User, Problem, Solution


# ============================================================
# MAKE PROJECT ROOT AVAILABLE
# ============================================================
# prediction_module.py is outside the backend folder.
#
# Project structure:
#
# MLM project/
# ├── prediction_module.py
# └── backend/
#     ├── app.py
#     └── routes.py
#
# This allows Flask to import prediction_module.py.
# ============================================================

BACKEND_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.dirname(
    BACKEND_DIR
)


if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ============================================================
# MACHINE LEARNING PREDICTION MODULE
# ============================================================

try:

    from prediction_module import predict_problem

    ML_AVAILABLE = True

    print(
        "ML prediction module loaded successfully."
    )

except Exception as error:

    ML_AVAILABLE = False

    predict_problem = None

    print(
        "WARNING: ML prediction module could not be loaded."
    )

    print(
        "ML Error:",
        error
    )


# ============================================================
# BLUEPRINT
# ============================================================

api = Blueprint(
    "api",
    __name__
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def error_response(
    message,
    status_code=400
):

    return jsonify({

        "success": False,

        "message": message

    }), status_code


# ============================================================
# SERIALIZE USER
# ============================================================

def user_response(user):

    return {

        "id": user.id,

        "username": user.username,

        "email": user.email,

        "role": user.role

    }


# ============================================================
# AUTHENTICATION DECORATOR
# ============================================================
# Currently the application stores the logged-in user in
# localStorage on the frontend.
#
# Therefore the API accepts user_id from the request.
#
# This keeps the current architecture simple for your
# demonstration system.
# ============================================================

def get_request_user():

    data = request.get_json(
        silent=True
    ) or {}


    user_id = (

        data.get("user_id")

        or

        request.args.get("user_id")

    )


    if not user_id:

        return None


    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return None


    return User.query.get(
        user_id
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@api.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "success": True,

        "message":
            "CrowdSolve API is running successfully.",

        "ml_available":
            ML_AVAILABLE

    })


# ============================================================
# REGISTER
# ============================================================

def register_user():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return error_response(
                "No registration data received.",
                400
            )


        username = str(
            data.get(
                "username",
                ""
            )
        ).strip()


        email = str(
            data.get(
                "email",
                ""
            )
        ).strip().lower()


        password = str(
            data.get(
                "password",
                ""
            )
        )


        role = str(
            data.get(
                "role",
                "solver"
            )
        ).strip().lower()


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not username:

            return error_response(
                "Username is required.",
                400
            )


        if not email:

            return error_response(
                "Email is required.",
                400
            )


        if not password:

            return error_response(
                "Password is required.",
                400
            )


        if len(password) < 6:

            return error_response(
                "Password must contain at least 6 characters.",
                400
            )


        if role not in [
            "solver",
            "problemer"
        ]:

            return error_response(
                "Role must be either solver or problemer.",
                400
            )


        # ----------------------------------------------------
        # CHECK USERNAME
        # ----------------------------------------------------

        existing_username = (
            User.query
            .filter_by(
                username=username
            )
            .first()
        )


        if existing_username:

            return error_response(
                "Username already exists.",
                409
            )


        # ----------------------------------------------------
        # CHECK EMAIL
        # ----------------------------------------------------

        existing_email = (
            User.query
            .filter_by(
                email=email
            )
            .first()
        )


        if existing_email:

            return error_response(
                "Email already registered.",
                409
            )


        # ----------------------------------------------------
        # HASH PASSWORD
        # ----------------------------------------------------

        password_hash = (
            generate_password_hash(
                password
            )
        )


        # ----------------------------------------------------
        # CREATE USER
        # ----------------------------------------------------

        user = User(

            username=username,

            email=email,

            password_hash=password_hash,

            role=role

        )


        db.session.add(
            user
        )

        db.session.commit()


        print(
            f"New user registered: "
            f"{username} ({role})"
        )


        return jsonify({

            "success": True,

            "message":
                "Registration successful.",

            "user":
                user_response(user)

        }), 201


    except Exception as error:

        db.session.rollback()


        print(
            "REGISTRATION ERROR:",
            error
        )


        return error_response(
            "Registration failed.",
            500
        )


# ------------------------------------------------------------
# AUTH REGISTER
# ------------------------------------------------------------

api.add_url_rule(

    "/auth/register",

    endpoint="auth_register",

    view_func=register_user,

    methods=["POST"]

)


# ------------------------------------------------------------
# REGISTER ALIAS
# ------------------------------------------------------------
# Keeps /api/register working too.

api.add_url_rule(

    "/register",

    endpoint="register",

    view_func=register_user,

    methods=["POST"]

)


# ============================================================
# LOGIN
# ============================================================

def login_user():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return error_response(
                "No login data received.",
                400
            )


        # ----------------------------------------------------
        # ACCEPT EMAIL OR USERNAME
        # ----------------------------------------------------

        identifier = (

            data.get("email")

            or

            data.get("username")

            or

            data.get("identifier")

            or

            ""

        )


        identifier = str(
            identifier
        ).strip()


        password = str(
            data.get(
                "password",
                ""
            )
        )


        if not identifier:

            return error_response(
                "Email or username is required.",
                400
            )


        if not password:

            return error_response(
                "Password is required.",
                400
            )


        # ----------------------------------------------------
        # FIND USER
        # ----------------------------------------------------

        user = (

            User.query

            .filter(

                or_(

                    User.email.ilike(
                        identifier
                    ),

                    User.username.ilike(
                        identifier
                    )

                )

            )

            .first()

        )


        if not user:

            return error_response(
                "Invalid username or password.",
                401
            )


        # ----------------------------------------------------
        # VERIFY PASSWORD HASH
        # ----------------------------------------------------

        password_valid = (
            check_password_hash(

                user.password_hash,

                password

            )
        )


        if not password_valid:

            return error_response(
                "Invalid username or password.",
                401
            )


        print(
            f"User logged in: "
            f"{user.username} ({user.role})"
        )


        return jsonify({

            "success": True,

            "message":
                "Login successful.",

            "user":
                user_response(user)

        }), 200


    except Exception as error:

        print(
            "LOGIN ERROR:",
            error
        )


        return error_response(
            "An error occurred during login.",
            500
        )


# ------------------------------------------------------------
# AUTH LOGIN
# ------------------------------------------------------------

api.add_url_rule(

    "/auth/login",

    endpoint="auth_login",

    view_func=login_user,

    methods=["POST"]

)


# ------------------------------------------------------------
# LOGIN ALIAS
# ------------------------------------------------------------

api.add_url_rule(

    "/login",

    endpoint="login",

    view_func=login_user,

    methods=["POST"]

)


# ============================================================
# ML CLASSIFICATION
# ============================================================

def classify_problem_text(
    title,
    description
):

    if not ML_AVAILABLE:

        raise RuntimeError(
            "Machine Learning prediction module is unavailable."
        )


    # --------------------------------------------------------
    # COMBINE TITLE + DESCRIPTION
    # --------------------------------------------------------

    combined_text = (

        str(title).strip()

        + " "

        +

        str(description).strip()

    )


    # --------------------------------------------------------
    # CALL REUSABLE ML MODULE
    # --------------------------------------------------------

    result = predict_problem(
        combined_text
    )


    # --------------------------------------------------------
    # NORMALIZE RESULT
    # --------------------------------------------------------
    # The prediction module created earlier returns:
    #
    # predicted_category
    # confidence
    # top_predictions
    # preprocessed_problem
    #
    # This section also handles alternative key names
    # so the API remains robust.
    # --------------------------------------------------------

    if not isinstance(
        result,
        dict
    ):

        raise RuntimeError(
            "Prediction module returned an invalid result."
        )


    predicted_category = (

        result.get(
            "predicted_category"
        )

        or

        result.get(
            "category"
        )

        or

        result.get(
            "prediction"
        )

    )


    confidence = (

        result.get(
            "confidence"
        )

        or

        result.get(
            "prediction_confidence"
        )

    )


    top_predictions = (

        result.get(
            "top_predictions"
        )

        or

        result.get(
            "top_3_predictions"
        )

        or

        []

    )


    cleaned_text = (

        result.get(
            "preprocessed_problem"
        )

        or

        result.get(
            "cleaned_problem"
        )

        or

        result.get(
            "cleaned_text"
        )

        or

        combined_text

    )


    if not predicted_category:

        raise RuntimeError(
            "ML model did not return a predicted category."
        )


    # --------------------------------------------------------
    # NORMALIZE CONFIDENCE
    # --------------------------------------------------------

    if confidence is not None:

        confidence = float(
            confidence
        )


        # If model returned 0.9686,
        # convert to 96.86.

        if confidence <= 1:

            confidence *= 100


        confidence = round(
            confidence,
            2
        )


    # --------------------------------------------------------
    # NORMALIZE TOP PREDICTIONS
    # --------------------------------------------------------

    normalized_predictions = []


    if isinstance(
        top_predictions,
        list
    ):

        for item in top_predictions:

            if isinstance(
                item,
                dict
            ):

                category = (

                    item.get(
                        "category"
                    )

                    or

                    item.get(
                        "label"
                    )

                    or

                    item.get(
                        "class"
                    )

                )


                score = (

                    item.get(
                        "confidence"
                    )

                    or

                    item.get(
                        "score"
                    )

                    or

                    item.get(
                        "probability"
                    )

                )


                if category:

                    if score is not None:

                        score = float(
                            score
                        )


                        if score <= 1:

                            score *= 100


                        score = round(
                            score,
                            2
                        )


                    normalized_predictions.append({

                        "category":
                            category,

                        "confidence":
                            score

                    })

            elif isinstance(
                item,
                (list, tuple)
            ):

                if len(item) >= 2:

                    category = str(
                        item[0]
                    )


                    score = float(
                        item[1]
                    )


                    if score <= 1:

                        score *= 100


                    normalized_predictions.append({

                        "category":
                            category,

                        "confidence":
                            round(
                                score,
                                2
                            )

                    })


    return {

        "predicted_category":
            predicted_category,

        "confidence":
            confidence,

        "top_predictions":
            normalized_predictions,

        "cleaned_text":
            cleaned_text

    }


# ============================================================
# CREATE PROBLEM
# ============================================================

@api.route(
    "/problems",
    methods=["POST"]
)
def create_problem():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return error_response(
                "No problem data received.",
                400
            )


        # ----------------------------------------------------
        # READ INPUT
        # ----------------------------------------------------

        title = str(
            data.get(
                "title",
                ""
            )
        ).strip()


        description = str(
            data.get(
                "description",
                ""
            )
        ).strip()


        user_id = (

            data.get(
                "user_id"
            )

            or

            data.get(
                "created_by"
            )

        )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not title:

            return error_response(
                "Problem title is required.",
                400
            )


        if not description:

            return error_response(
                "Problem description is required.",
                400
            )


        if not user_id:

            return error_response(
                "User ID is required.",
                400
            )


        try:

            user_id = int(
                user_id
            )

        except (
            TypeError,
            ValueError
        ):

            return error_response(
                "Invalid user ID.",
                400
            )


        # ----------------------------------------------------
        # CHECK USER
        # ----------------------------------------------------

        user = User.query.get(
            user_id
        )


        if not user:

            return error_response(
                "User not found.",
                404
            )


        if user.role != "problemer":

            return error_response(
                "Only problemers can submit problems.",
                403
            )


        # ----------------------------------------------------
        # RUN MACHINE LEARNING CLASSIFICATION
        # ----------------------------------------------------

        print(
            "\n" + "=" * 70
        )

        print(
            "NEW PROBLEM - ML CLASSIFICATION"
        )

        print(
            "=" * 70
        )

        print(
            "Title:",
            title
        )

        print(
            "Description:",
            description
        )


        ml_result = classify_problem_text(

            title,

            description

        )


        print(
            "Predicted Category:",
            ml_result[
                "predicted_category"
            ]
        )


        print(
            "Confidence:",
            ml_result[
                "confidence"
            ]
        )


        # ----------------------------------------------------
        # CREATE DATABASE RECORD
        # ----------------------------------------------------

        problem = Problem(

            title=title,

            description=description,

            cleaned_text=
                ml_result[
                    "cleaned_text"
                ],

            predicted_category=
                ml_result[
                    "predicted_category"
                ],

            confidence=
                ml_result[
                    "confidence"
                ],

            top_predictions=
                ml_result[
                    "top_predictions"
                ],

            created_by=user.id,

            status="open"

        )


        db.session.add(
            problem
        )

        db.session.commit()


        print(
            "Problem saved with ID:",
            problem.id
        )

        print(
            "=" * 70 + "\n"
        )


        return jsonify({

            "success": True,

            "message":
                "Problem submitted and classified successfully.",

            "problem":
                problem.to_dict(),

            "classification": {

                "predicted_category":
                    ml_result[
                        "predicted_category"
                    ],

                "confidence":
                    ml_result[
                        "confidence"
                    ],

                "top_predictions":
                    ml_result[
                        "top_predictions"
                    ],

                "cleaned_text":
                    ml_result[
                        "cleaned_text"
                    ]

            }

        }), 201


    except Exception as error:

        db.session.rollback()


        print(
            "\nPROBLEM CREATION ERROR:"
        )

        print(
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to submit problem.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET PROBLEMS
# ============================================================

@api.route(
    "/problems",
    methods=["GET"]
)
def get_problems():

    try:

        user_id = request.args.get(
            "user_id"
        )


        # ----------------------------------------------------
        # GET ALL OPEN PROBLEMS
        # ----------------------------------------------------

        query = (

            Problem.query

            .filter(
                Problem.status == "open"
            )

            .order_by(
                Problem.created_at.desc()
            )

        )


        problems = query.all()


        # ----------------------------------------------------
        # CONVERT TO DICTIONARY
        # ----------------------------------------------------

        problem_list = []


        for problem in problems:

            problem_data = problem.to_dict()


            # Add convenient aliases
            # used by the frontend.

            problem_data[
                "category"
            ] = problem.predicted_category


            problem_data[
                "prediction_confidence"
            ] = problem.confidence


            problem_list.append(
                problem_data
            )


        return jsonify({

            "success": True,

            "count":
                len(problem_list),

            "problems":
                problem_list

        }), 200


    except Exception as error:

        print(
            "GET PROBLEMS ERROR:",
            error
        )


        return error_response(
            "Unable to retrieve problems.",
            500
        )


# ============================================================
# GET SINGLE PROBLEM
# ============================================================

@api.route(
    "/problems/<int:problem_id>",
    methods=["GET"]
)
def get_single_problem(
    problem_id
):

    try:

        problem = Problem.query.get(
            problem_id
        )


        if not problem:

            return error_response(
                "Problem not found.",
                404
            )


        problem_data = problem.to_dict()


        problem_data[
            "category"
        ] = problem.predicted_category


        problem_data[
            "prediction_confidence"
        ] = problem.confidence


        return jsonify({

            "success": True,

            "problem":
                problem_data

        })


    except Exception as error:

        print(
            "GET SINGLE PROBLEM ERROR:",
            error
        )


        return error_response(
            "Unable to retrieve problem.",
            500
        )


# ============================================================
# SUBMIT SOLUTION
# ============================================================

@api.route(
    "/solutions",
    methods=["POST"]
)
def submit_solution():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return error_response(
                "No solution data received.",
                400
            )


        problem_id = data.get(
            "problem_id"
        )


        submitted_by = (

            data.get(
                "user_id"
            )

            or

            data.get(
                "submitted_by"
            )

        )


        solution_text = (

            data.get(
                "solution"
            )

            or

            data.get(
                "solution_text"
            )

            or

            ""

        )


        solution_text = str(
            solution_text
        ).strip()


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not problem_id:

            return error_response(
                "Problem ID is required.",
                400
            )


        if not submitted_by:

            return error_response(
                "Solver user ID is required.",
                400
            )


        if not solution_text:

            return error_response(
                "Solution cannot be empty.",
                400
            )


        try:

            problem_id = int(
                problem_id
            )

            submitted_by = int(
                submitted_by
            )

        except (
            TypeError,
            ValueError
        ):

            return error_response(
                "Invalid problem or user ID.",
                400
            )


        # ----------------------------------------------------
        # FIND PROBLEM
        # ----------------------------------------------------

        problem = Problem.query.get(
            problem_id
        )


        if not problem:

            return error_response(
                "Problem not found.",
                404
            )


        # ----------------------------------------------------
        # FIND SOLVER
        # ----------------------------------------------------

        solver = User.query.get(
            submitted_by
        )


        if not solver:

            return error_response(
                "Solver not found.",
                404
            )


        if solver.role != "solver":

            return error_response(
                "Only solvers can submit solutions.",
                403
            )


        # ----------------------------------------------------
        # CREATE SOLUTION
        # ----------------------------------------------------

        solution = Solution(

            problem_id=problem.id,

            solution_text=solution_text,

            submitted_by=solver.id

        )


        db.session.add(
            solution
        )

        db.session.commit()


        print(
            f"Solution {solution.id} submitted "
            f"by solver {solver.username} "
            f"for problem {problem.id}"
        )


        return jsonify({

            "success": True,

            "message":
                "Solution submitted successfully.",

            "solution":
                solution.to_dict()

        }), 201


    except Exception as error:

        db.session.rollback()


        print(
            "SOLUTION SUBMISSION ERROR:",
            error
        )


        return error_response(
            "Unable to submit solution.",
            500
        )


# ============================================================
# GET SOLUTIONS FOR A PROBLEM
# ============================================================

@api.route(
    "/problems/<int:problem_id>/solutions",
    methods=["GET"]
)
def get_problem_solutions(
    problem_id
):

    try:

        problem = Problem.query.get(
            problem_id
        )


        if not problem:

            return error_response(
                "Problem not found.",
                404
            )


        solutions = (

            Solution.query

            .filter_by(
                problem_id=problem_id
            )

            .order_by(
                Solution.created_at.asc()
            )

            .all()

        )


        return jsonify({

            "success": True,

            "problem_id":
                problem_id,

            "solution_count":
                len(solutions),

            "solutions": [

                solution.to_dict()

                for solution in solutions

            ]

        })


    except Exception as error:

        print(
            "GET SOLUTIONS ERROR:",
            error
        )


        return error_response(
            "Unable to retrieve solutions.",
            500
        )


# ============================================================
# GET PROBLEMS CREATED BY CURRENT USER
# ============================================================

@api.route(
    "/my-problems",
    methods=["GET"]
)
def get_my_problems():

    try:

        user_id = request.args.get(
            "user_id"
        )


        if not user_id:

            return error_response(
                "User ID is required.",
                400
            )


        try:

            user_id = int(
                user_id
            )

        except (
            TypeError,
            ValueError
        ):

            return error_response(
                "Invalid user ID.",
                400
            )


        problems = (

            Problem.query

            .filter_by(
                created_by=user_id
            )

            .order_by(
                Problem.created_at.desc()
            )

            .all()

        )


        return jsonify({

            "success": True,

            "problems": [

                problem.to_dict()

                for problem in problems

            ]

        })


    except Exception as error:

        print(
            "MY PROBLEMS ERROR:",
            error
        )


        return error_response(
            "Unable to retrieve your problems.",
            500
        )


# ============================================================
# CATEGORIES
# ============================================================

@api.route(
    "/categories",
    methods=["GET"]
)
def get_categories():

    try:

        categories = [

            "express.js",

            "html / css",

            "javascript",

            "next.js",

            "node.js",

            "php / laravel",

            "python",

            "react",

            "sql",

            "typescript"

        ]


        return jsonify({

            "success": True,

            "categories":
                categories

        })


    except Exception as error:

        return error_response(
            "Unable to retrieve categories.",
            500
        )


# ============================================================
# DATABASE TEST
# ============================================================

@api.route(
    "/database-test",
    methods=["GET"]
)
def database_test():

    try:

        db.session.execute(
            db.text(
                "SELECT 1"
            )
        )


        return jsonify({

            "success": True,

            "message":
                "Database connection successful."

        })


    except Exception as error:

        print(
            "DATABASE TEST ERROR:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Database connection failed.",

            "error":
                str(error)

        }), 500


# ============================================================
# ML TEST ENDPOINT
# ============================================================

@api.route(
    "/classify",
    methods=["POST"]
)
def classify():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return error_response(
                "No text received.",
                400
            )


        title = str(
            data.get(
                "title",
                ""
            )
        ).strip()


        description = str(
            data.get(
                "description",
                ""
            )
        ).strip()


        text = str(
            data.get(
                "text",
                ""
            )
        ).strip()


        # If direct text is supplied,
        # use it as the description.

        if not description and text:

            description = text


        if not title:

            title = "Problem"


        if not description:

            return error_response(
                "Problem text is required.",
                400
            )


        result = classify_problem_text(

            title,

            description

        )


        return jsonify({

            "success": True,

            "classification":
                result

        })


    except Exception as error:

        print(
            "CLASSIFICATION ERROR:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Machine Learning classification failed.",

            "error":
                str(error)

        }), 500