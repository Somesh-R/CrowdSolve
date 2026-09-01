# ============================================================
# REUSABLE PREDICTION MODULE
# PROJECT: CROWDSOURCED PROBLEM-SOLVING PLATFORM
# ============================================================


# ============================================================
# 1. IMPORT REQUIRED LIBRARIES
# ============================================================

import re
import joblib
import nltk
import os
import sys

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


# ============================================================
# 2. DOWNLOAD REQUIRED NLTK DATA
# ============================================================

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)


# ============================================================
# 3. LOAD THE TRAINED MODEL AND TF-IDF VECTORIZER
# ============================================================

# ============================================================
# GET THE DIRECTORY WHERE THIS FILE IS LOCATED
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

model_path = os.path.join(
    BASE_DIR,
    "final_problem_classifier.pkl"
)

model = joblib.load(
    model_path
)


# ============================================================
# LOAD TF-IDF VECTORIZER
# ============================================================

vectorizer_path = os.path.join(
    BASE_DIR,
    "final_tfidf_vectorizer.pkl"
)

tfidf_vectorizer = joblib.load(
    vectorizer_path
)


# ============================================================
# LOAD PROBLEM CATEGORIES
# ============================================================

categories_path = os.path.join(
    BASE_DIR,
    "problem_categories.pkl"
)

categories = joblib.load(
    categories_path
)


# ============================================================
# 4. INITIALIZE TEXT PREPROCESSING COMPONENTS
# ============================================================

stop_words = set(
    stopwords.words("english")
)

lemmatizer = WordNetLemmatizer()


# ============================================================
# 5. TEXT PREPROCESSING FUNCTION
# ============================================================

def preprocess_text(text):

    # Convert to lowercase
    text = text.lower()


    # --------------------------------------------------------
    # PRESERVE IMPORTANT TECHNOLOGY NAMES
    # --------------------------------------------------------

    text = text.replace(
        "node.js",
        "nodejs"
    )

    text = text.replace(
        "next.js",
        "nextjs"
    )

    text = text.replace(
        "express.js",
        "expressjs"
    )

    text = text.replace(
        "c++",
        "cplusplus"
    )

    text = text.replace(
        "c#",
        "csharp"
    )


    # --------------------------------------------------------
    # REMOVE SPECIAL CHARACTERS
    # --------------------------------------------------------

    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text
    )


    # --------------------------------------------------------
    # TOKENIZATION
    # --------------------------------------------------------

    tokens = word_tokenize(text)


    # --------------------------------------------------------
    # REMOVE STOPWORDS AND SHORT WORDS
    # --------------------------------------------------------

    tokens = [

        word

        for word in tokens

        if word not in stop_words
        and len(word) > 1

    ]


    # --------------------------------------------------------
    # LEMMATIZATION
    # --------------------------------------------------------

    tokens = [

        lemmatizer.lemmatize(word)

        for word in tokens

    ]


    # --------------------------------------------------------
    # JOIN WORDS BACK INTO TEXT
    # --------------------------------------------------------

    return " ".join(tokens)


# ============================================================
# 6. MAIN PREDICTION FUNCTION
# ============================================================

def predict_problem(problem_text):

    """
    Predict the category of a new problem.

    Parameters:
        problem_text (str):
            The problem submitted by the user.

    Returns:
        dict:
            Contains the original problem, processed text,
            predicted category, confidence, and top 3 predictions.
    """


    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    if not isinstance(problem_text, str):

        raise ValueError(
            "Problem text must be a string."
        )


    if not problem_text.strip():

        raise ValueError(
            "Problem text cannot be empty."
        )


    # --------------------------------------------------------
    # STEP 1: PREPROCESS THE PROBLEM
    # --------------------------------------------------------

    cleaned_problem = preprocess_text(
        problem_text
    )


    # --------------------------------------------------------
    # STEP 2: CONVERT TO TF-IDF FEATURES
    # --------------------------------------------------------

    problem_tfidf = tfidf_vectorizer.transform(
        [cleaned_problem]
    )


    # --------------------------------------------------------
    # STEP 3: PREDICT CATEGORY
    # --------------------------------------------------------

    prediction = model.predict(
        problem_tfidf
    )[0]


    # --------------------------------------------------------
    # STEP 4: GET PREDICTION PROBABILITIES
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        problem_tfidf
    )[0]


    # --------------------------------------------------------
    # STEP 5: GET CONFIDENCE
    # --------------------------------------------------------

    confidence = max(
        probabilities
    ) * 100


    # --------------------------------------------------------
    # STEP 6: GET TOP 3 PREDICTIONS
    # --------------------------------------------------------

    top_indices = probabilities.argsort()[-3:][::-1]

    top_predictions = []


    for index in top_indices:

        top_predictions.append({

            "category": model.classes_[index],

            "confidence": round(
                probabilities[index] * 100,
                2
            )

        })


    # --------------------------------------------------------
    # RETURN COMPLETE RESULT
    # --------------------------------------------------------

    result = {

        "original_problem": problem_text,

        "cleaned_problem": cleaned_problem,

        "predicted_category": prediction,

        "confidence": round(
            confidence,
            2
        ),

        "top_predictions": top_predictions

    }


    return result


# ============================================================
# 7. DISPLAY RESULT FUNCTION
# ============================================================

def display_prediction(result):

    print("\n")
    print("=" * 70)

    print("PROBLEM CLASSIFICATION RESULT")

    print("=" * 70)


    print("\nOriginal Problem:")

    print(
        result["original_problem"]
    )


    print("\nPreprocessed Problem:")

    print(
        result["cleaned_problem"]
    )


    print("\nPredicted Category:")

    print(
        result["predicted_category"]
    )


    print("\nPrediction Confidence:")

    print(
        f"{result['confidence']}%"
    )


    print("\nTop 3 Predictions:")


    for i, prediction in enumerate(
        result["top_predictions"],
        start=1
    ):

        print(

            f"{i}. "
            f"{prediction['category']} "
            f"→ "
            f"{prediction['confidence']}%"

        )


    print("\n" + "=" * 70)


# ============================================================
# 8. TEST THE MODULE
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print("REUSABLE PREDICTION MODULE TEST")

    print("=" * 70)


    test_problems = [

        "My React component does not update when the state changes.",

        "How can I optimize a slow SQL query with multiple joins?",

        "I am getting an error when using async functions in Python.",

        "How do I create middleware in an Express.js application?",

        "Why is my TypeScript interface giving me a type error?"

    ]


    for problem in test_problems:

        result = predict_problem(
            problem
        )

        display_prediction(
            result
        )


    print("\n")

    print("PREDICTION MODULE TEST COMPLETED SUCCESSFULLY")