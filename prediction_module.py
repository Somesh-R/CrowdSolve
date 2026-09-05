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

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


# ============================================================
# 2. MULTI-DOMAIN CLASSIFICATION SETTINGS
# ============================================================

# If the highest prediction is at or above this percentage,
# the model is considered sufficiently confident and only
# the highest-confidence domain will be assigned.
HIGH_CONFIDENCE_THRESHOLD = 70.0


# When the highest prediction is below the high-confidence
# threshold, every domain at or above this percentage can
# be assigned.
MULTI_DOMAIN_THRESHOLD = 15.0


# Prevent a low-confidence problem from being assigned to
# too many domains.
MAX_ASSIGNED_DOMAINS = 3


# ============================================================
# 3. DOWNLOAD REQUIRED NLTK DATA
# ============================================================

nltk.download(
    "punkt",
    quiet=True
)

nltk.download(
    "punkt_tab",
    quiet=True
)

nltk.download(
    "stopwords",
    quiet=True
)

nltk.download(
    "wordnet",
    quiet=True
)

nltk.download(
    "omw-1.4",
    quiet=True
)


# ============================================================
# 4. LOAD THE TRAINED MODEL AND TF-IDF VECTORIZER
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
# 5. INITIALIZE TEXT PREPROCESSING COMPONENTS
# ============================================================

stop_words = set(
    stopwords.words("english")
)

lemmatizer = WordNetLemmatizer()


# ============================================================
# 6. TEXT PREPROCESSING FUNCTION
# ============================================================

def preprocess_text(text):

    # --------------------------------------------------------
    # Convert to lowercase
    # --------------------------------------------------------

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

    tokens = word_tokenize(
        text
    )


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

    return " ".join(
        tokens
    )


# ============================================================
# 7. DETERMINE ASSIGNED DOMAINS
# ============================================================

def determine_assigned_domains(
    probabilities,
    classes
):

    """
    Determine whether a problem should be assigned to one
    domain or multiple domains.

    Rules:

        Highest confidence >= 70%
            -> assign only the highest-confidence domain.

        Highest confidence < 70%
            -> assign all domains with confidence >= 15%.

        Maximum assigned domains
            -> 3

    Parameters:
        probabilities:
            Probability values returned by model.predict_proba().

        classes:
            Model category/class names.

    Returns:
        list:
            A list of dictionaries containing category
            and confidence.
    """


    # --------------------------------------------------------
    # SORT ALL PREDICTIONS FROM HIGHEST TO LOWEST
    # --------------------------------------------------------

    sorted_indices = probabilities.argsort()[::-1]


    # --------------------------------------------------------
    # GET HIGHEST CONFIDENCE
    # --------------------------------------------------------

    highest_confidence = (
        probabilities[sorted_indices[0]]
        * 100
    )


    # --------------------------------------------------------
    # HIGH-CONFIDENCE CASE
    # --------------------------------------------------------

    if highest_confidence > HIGH_CONFIDENCE_THRESHOLD:

        top_index = sorted_indices[0]

        return [

            {
                "category": classes[top_index],
                "confidence": round(
                    probabilities[top_index] * 100,
                    2
                )
            }

        ]


    # --------------------------------------------------------
    # LOW-CONFIDENCE CASE
    # --------------------------------------------------------

    assigned_domains = []


    for index in sorted_indices:

        confidence = (
            probabilities[index]
            * 100
        )


        # ----------------------------------------------------
        # Only include domains at or above the threshold
        # ----------------------------------------------------

        if confidence >= MULTI_DOMAIN_THRESHOLD:

            assigned_domains.append(

                {
                    "category": classes[index],

                    "confidence": round(
                        confidence,
                        2
                    )
                }

            )


        # ----------------------------------------------------
        # Stop after maximum allowed domains
        # ----------------------------------------------------

        if len(assigned_domains) >= MAX_ASSIGNED_DOMAINS:

            break


    # --------------------------------------------------------
    # SAFETY FALLBACK
    # --------------------------------------------------------

    # The highest prediction should normally always be above
    # 15%. This fallback guarantees that at least one domain
    # is assigned if the probability distribution is unusual.

    if not assigned_domains:

        top_index = sorted_indices[0]

        assigned_domains.append(

            {
                "category": classes[top_index],

                "confidence": round(
                    probabilities[top_index] * 100,
                    2
                )
            }

        )


    return assigned_domains


# ============================================================
# 8. MAIN PREDICTION FUNCTION
# ============================================================

def predict_problem(problem_text):

    """
    Predict the category/domain(s) of a new problem.

    Parameters:
        problem_text (str):
            The problem submitted by the user.

    Returns:
        dict:
            Contains:

            - original_problem
            - cleaned_problem
            - predicted_category
            - confidence
            - top_predictions
            - predicted_domains
    """


    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    if not isinstance(
        problem_text,
        str
    ):

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
    # STEP 3: PREDICT PRIMARY CATEGORY
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
    # STEP 5: GET HIGHEST CONFIDENCE
    # --------------------------------------------------------

    confidence = (
        max(probabilities)
        * 100
    )


    # --------------------------------------------------------
    # STEP 6: GET TOP 3 PREDICTIONS
    # --------------------------------------------------------

    top_indices = probabilities.argsort()[-3:][::-1]

    top_predictions = []


    for index in top_indices:

        top_predictions.append(

            {
                "category": model.classes_[index],

                "confidence": round(
                    probabilities[index] * 100,
                    2
                )
            }

        )


    # --------------------------------------------------------
    # STEP 7: DETERMINE ASSIGNED DOMAINS
    # --------------------------------------------------------

    predicted_domains = determine_assigned_domains(

        probabilities,

        model.classes_

    )


    # --------------------------------------------------------
    # STEP 8: RETURN COMPLETE RESULT
    # --------------------------------------------------------

    result = {

        "original_problem": problem_text,

        "cleaned_problem": cleaned_problem,

        # Primary/top prediction
        "predicted_category": prediction,

        # Highest model confidence
        "confidence": round(
            confidence,
            2
        ),

        # Top 3 model predictions
        "top_predictions": top_predictions,

        # Actual domains assigned to the problem
        "predicted_domains": predicted_domains

    }


    return result


# ============================================================
# 9. DISPLAY RESULT FUNCTION
# ============================================================

def display_prediction(result):

    print("\n")

    print("=" * 70)

    print(
        "PROBLEM CLASSIFICATION RESULT"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # ORIGINAL PROBLEM
    # --------------------------------------------------------

    print("\nOriginal Problem:")

    print(
        result["original_problem"]
    )


    # --------------------------------------------------------
    # PREPROCESSED PROBLEM
    # --------------------------------------------------------

    print("\nPreprocessed Problem:")

    print(
        result["cleaned_problem"]
    )


    # --------------------------------------------------------
    # PRIMARY PREDICTED CATEGORY
    # --------------------------------------------------------

    print("\nPrimary Predicted Category:")

    print(
        result["predicted_category"]
    )


    # --------------------------------------------------------
    # PRIMARY CONFIDENCE
    # --------------------------------------------------------

    print("\nPrediction Confidence:")

    print(
        f"{result['confidence']}%"
    )


    # --------------------------------------------------------
    # TOP 3 PREDICTIONS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # ASSIGNED DOMAINS
    # --------------------------------------------------------

    print("\nAssigned Domain(s):")


    for i, domain in enumerate(

        result["predicted_domains"],

        start=1

    ):

        print(

            f"{i}. "
            f"{domain['category']} "
            f"→ "
            f"{domain['confidence']}%"

        )


    # --------------------------------------------------------
    # CLASSIFICATION MODE
    # --------------------------------------------------------

    print("\nClassification Mode:")


    if result["confidence"] >= HIGH_CONFIDENCE_THRESHOLD:

        print(
            "High confidence → Single-domain assignment"
        )

    else:

        print(
            "Low confidence → Multi-domain assignment"
        )


    print(
        "\n" + "=" * 70
    )


# ============================================================
# 10. TEST THE MODULE
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "REUSABLE PREDICTION MODULE TEST"
    )

    print("=" * 70)


    test_problems = [

        "My React component does not update when the state changes.",

        "How can I optimize a slow SQL query with multiple joins?",

        "I am getting an error when using async functions in Python.",

        "How do I create middleware in an Express.js application?",

        "Why is my TypeScript interface giving me a type error?",

        "In login page how to assign a button to a hyperlink?"

    ]


    for problem in test_problems:

        result = predict_problem(
            problem
        )

        display_prediction(
            result
        )


    print("\n")

    print(
        "PREDICTION MODULE TEST COMPLETED SUCCESSFULLY"
    )