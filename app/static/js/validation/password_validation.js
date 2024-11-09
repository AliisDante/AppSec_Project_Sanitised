const newPasswordInput = document.querySelector('input[name="new_password"]');
const confirmPasswordInput = document.querySelector('input[name="cfm_password"]');
const passwordErrorText = document.getElementById('password-error-text');

newPasswordInput.addEventListener('input', validatePasswords);
confirmPasswordInput.addEventListener('input', validatePasswords);

function validatePasswords() {
    const passwordPattern = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{4,64}$/;

    if (newPasswordInput.value === '' && confirmPasswordInput.value === '') {
        confirmPasswordInput.setCustomValidity('');
        newPasswordInput.setCustomValidity('');
        passwordErrorText.textContent = ''; // Clear error message
        passwordErrorText.classList.add('hidden'); // Hide error message
    } else if (!passwordPattern.test(newPasswordInput.value)) {
        passwordErrorText.textContent = "Password must contain at least one digit, one lowercase letter, one uppercase letter, and be 8-64 characters long.";
        confirmPasswordInput.setCustomValidity("Passwords must match and meet the requirements");
        newPasswordInput.setCustomValidity("Passwords must match and meet the requirements");
        passwordErrorText.classList.remove('hidden'); // Show error message
    } else if (newPasswordInput.value !== confirmPasswordInput.value) {
        passwordErrorText.textContent = "Passwords do not match.";
        confirmPasswordInput.setCustomValidity("Passwords do not match");
        newPasswordInput.setCustomValidity("Passwords do not match");
        passwordErrorText.classList.remove('hidden'); // Show error message
    } else {
        confirmPasswordInput.setCustomValidity('');
        newPasswordInput.setCustomValidity("");
        passwordErrorText.textContent = ''; // Clear error message
        passwordErrorText.classList.add('hidden'); // Hide error message
    }
}