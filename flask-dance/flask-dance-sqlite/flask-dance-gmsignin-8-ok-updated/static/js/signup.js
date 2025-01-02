function validatePassword() {
    var password = document.getElementById("password").value;
    var strengthText = document.getElementById("password-strength-text");
    var passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;

    if (passwordPattern.test(password)) {
        strengthText.textContent = "Password is strong";
        strengthText.className = "password-strength strong";
    } else {
        strengthText.textContent = "Password must be at least 8 characters long and include uppercase letters, lowercase letters, numbers, and special characters.";
        strengthText.className = "password-strength weak";
    }
}

function validateConfirmPassword() {
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("confirm_password").value;
    var confirmPasswordText = document.getElementById("confirm-password-text");

    if (password !== confirmPassword) {
        confirmPasswordText.textContent = "Passwords do not match!";
        confirmPasswordText.className = "password-strength weak";
    } else {
        confirmPasswordText.textContent = "";
    }
}

function validateForm() {
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("confirm_password").value;
    var passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;

    if (!passwordPattern.test(password)) {
        alert("Password must be at least 8 characters long and include uppercase letters, lowercase letters, numbers, and special characters.");
        return false;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return false;
    }
    return true;
}