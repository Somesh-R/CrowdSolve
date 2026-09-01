/* =========================================================
   CROWDSOLVE - COMMON JAVASCRIPT
========================================================= */


/* =========================================================
   WAIT FOR PAGE TO LOAD
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializePasswordToggles();

        initializeNavigation();

        initializeFormEnhancements();

    }
);


/* =========================================================
   PASSWORD SHOW / HIDE TOGGLE
========================================================= */

function initializePasswordToggles() {

    const passwordToggles =
        document.querySelectorAll(
            ".password-toggle"
        );


    passwordToggles.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const passwordInput =
                        button.parentElement.querySelector(
                            "input"
                        );


                    if (!passwordInput) {

                        return;

                    }


                    if (
                        passwordInput.type ===
                        "password"
                    ) {

                        passwordInput.type =
                            "text";


                        button.textContent =
                            "Hide";

                    }

                    else {

                        passwordInput.type =
                            "password";


                        button.textContent =
                            "Show";

                    }

                }
            );

        }
    );

}


/* =========================================================
   NAVIGATION INITIALIZATION
========================================================= */

function initializeNavigation() {

    const logo =
        document.querySelector(
            ".logo"
        );


    if (logo) {

        logo.addEventListener(
            "click",
            function () {

                /*
                 Prevent unnecessary behavior only
                 if the logo does not already have
                 a valid link.
                */

            }
        );

    }

}


/* =========================================================
   FORM ENHANCEMENTS
========================================================= */

function initializeFormEnhancements() {

    const inputs =
        document.querySelectorAll(
            "input, textarea, select"
        );


    inputs.forEach(
        function (input) {

            input.addEventListener(
                "focus",
                function () {

                    input.classList.add(
                        "input-focused"
                    );

                }
            );


            input.addEventListener(
                "blur",
                function () {

                    input.classList.remove(
                        "input-focused"
                    );

                }
            );

        }
    );

}


/* =========================================================
   GENERIC API REQUEST FUNCTION

   Can be reused throughout the application.
========================================================= */

async function apiRequest(
    url,
    method = "GET",
    data = null
) {

    const options = {

        method: method,

        headers: {

            "Content-Type":
                "application/json"

        }

    };


    if (
        data !== null
    ) {

        options.body =
            JSON.stringify(
                data
            );

    }


    try {

        const response =
            await fetch(
                url,
                options
            );


        const result =
            await response.json();


        return {

            success:
                response.ok,

            status:
                response.status,

            data:
                result

        };

    }

    catch (error) {

        console.error(
            "API Request Error:",
            error
        );


        return {

            success:
                false,

            status:
                0,

            data: {

                success:
                    false,

                message:
                    "Unable to connect to the server."

            }

        };

    }

}


/* =========================================================
   ESCAPE HTML

   Protects dynamically displayed text.
========================================================= */

function escapeHTML(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


/* =========================================================
   TRUNCATE TEXT
========================================================= */

function truncateText(
    text,
    maxLength = 150
) {

    if (!text) {

        return "";

    }


    if (
        text.length <=
        maxLength
    ) {

        return text;

    }


    return (
        text.substring(
            0,
            maxLength
        ) +
        "..."
    );

}


/* =========================================================
   FORMAT CONFIDENCE

   Supports both:
   0.95
   and
   95
========================================================= */

function formatConfidence(
    confidence
) {

    if (
        confidence === null ||
        confidence === undefined ||
        confidence === ""
    ) {

        return "N/A";

    }


    const number =
        Number(
            confidence
        );


    if (
        Number.isNaN(
            number
        )
    ) {

        return "N/A";

    }


    const percentage =
        number <= 1
            ? number * 100
            : number;


    return (
        percentage.toFixed(
            2
        ) +
        "%"
    );

}


/* =========================================================
   SHOW TEMPORARY MESSAGE

   Can be used by future pages.
========================================================= */

function showTemporaryMessage(
    elementId,
    message,
    type = "success",
    duration = 5000
) {

    const messageElement =
        document.getElementById(
            elementId
        );


    if (!messageElement) {

        return;

    }


    messageElement.textContent =
        message;


    messageElement.className =
        "message-box " +
        type;


    setTimeout(
        function () {

            messageElement.className =
                "message-box hidden";

        },

        duration

    );

}


/* =========================================================
   LOGOUT HELPER
========================================================= */

function logoutUser() {

    localStorage.removeItem(
        "crowdsolve_user"
    );


    window.location.href =
        "/";

}


/* =========================================================
   GET CURRENT LOGGED-IN USER
========================================================= */

function getCurrentUser() {

    const storedUser =
        localStorage.getItem(
            "crowdsolve_user"
        );


    if (!storedUser) {

        return null;

    }


    try {

        return JSON.parse(
            storedUser
        );

    }

    catch (error) {

        console.error(
            "Invalid stored user:",
            error
        );


        localStorage.removeItem(
            "crowdsolve_user"
        );


        return null;

    }

}