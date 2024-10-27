
// Toggle password visibility
function togglePasswordVisibility(fieldId) {
    const field = document.getElementById(fieldId);
    field.type = field.type === "password" ? "text" : "password";
}

// Password strength checker
const passwordField = document.getElementById("id_password1");
const strengthIndicator = document.getElementById("password_strength");
const suggestionBox = document.getElementById("password_suggestion");

// document.getElementById("id_password1").addEventListener("input", function()

// Check password strength on input 
passwordField.addEventListener("input", function() {
    const password = this.value;
    // const strengthIndicator = document.getElementById("password_strength"); 
    const strength = checkPasswordStrength(password);

    if (password) {
        strengthIndicator.textContent = strength.message;
        strengthIndicator.className = `password_strength ${strength.class}`;

        if (password.length === 1) {
            displayPasswordSuggestion();
        }
    } else {
        strengthIndicator.textContent = '';
        strengthIndicator.className = '';
        suggestionBox.style.display = 'none'
    }
});

// Function to check password strength
function checkPasswordStrength(password) {
    const strongRegex = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$");
    const mediumRegex = new RegExp("^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*\\d))|((?=.*[A-Z])(?=.*\\d)))(?=.*[a-zA-Z]).{6,}$");

    if (strongRegex.test(password)) {
        return { message: "Strong", class: "strong" };
    } else if (mediumRegex.test(password)) {
        return { message: "Medium", class: "medium" };
    } else {
        return { message: "Weak", class: "weak" };
    }
}

// Password suggestion display function
function displayPasswordSuggestion() {
    const suggestedPassword = generatePassword();
    suggestionBox.innerHTML = `Suggested Password: <span>${suggestedPassword}</span>`;
    suggestionBox.style.display = "block";
}

// Password generator for suggestions
function generatePassword() {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+";
    let password = "";
    for (let i = 0; i < 12; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
}

// Click on suggested passworf to replace and user input
suggestionBox.addEventListener("click", function(event) {
    if (event.target.tagName === "SPAN") {
        passwordField.value = event.target.textContent;
        suggestionBox.style.display = "none";

        const strength = checkPasswordStrength(passwordField.value);
        strengthIndicator.textContent = strength.message;
        strengthIndicator.className = `password_strength ${strength.class}`;
    }
});

 // Hide suggestion box on password filed focus out
 passwordField.addEventListener("focusout", function() {
    setTimeout(() => { suggestionBox.style.display = "none"; }, 200);
});


// Password suggestion on input
document.addEventListener("DOMContentLoaded", function() {
    const suggestionBox = document.getElementById("password_suggestion");

    passwordField.addEventListener("input", function() {
        if (this.value.length === 0) {
            const suggestedPassword = generatePassword();
            suggestionBox.innerHTML = `Suggested Password: <span>${suggestedPassword}</span>`;
            suggestionBox.style.display = "block";
        } else {
            suggestionBox.style.display = "none";
        }
    });

});

document.querySelector("form").addEventListener("submit", function () {
    strengthIndicator.textContent = '';
    strengthIndicator.className = '';
});

// Terms and Conditions validation
document.getElementById("signup-submit").addEventListener("click", function(event) {
    const acceptTerms = document.getElementById("id_accept_terms.");
    if (!acceptTerms.checked) {
        event.preventDefault();
        alert("You much accept the Terms and Conditions to sign up.");
    }
})