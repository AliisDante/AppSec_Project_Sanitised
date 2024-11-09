const newEmailInput = document.querySelector('input[name="new_email"]');
const emailErrorText = document.getElementById('email-error-text');

newEmailInput.addEventListener('input', validateEmail);

function validateEmail() {
    const emailPattern = /^[\w\.-]+@[\w\.-]+\.\w+$/;
    const emailValue = newEmailInput.value;

    if (emailValue === '') {
        emailErrorText.textContent = ''; // Clear error message
        emailErrorText.classList.add('hidden'); // Hide error message
        newEmailInput.setCustomValidity('');
    } else if (emailPattern.test(emailValue)) {
        emailErrorText.textContent = ''; // Clear error message
        emailErrorText.classList.add('hidden'); // Hide error message
        newEmailInput.setCustomValidity('');
    } else {
        emailErrorText.textContent = "Invalid email format.";
        emailErrorText.classList.remove('hidden'); // Show error message
        newEmailInput.setCustomValidity("Invalid email format");
    }
}
