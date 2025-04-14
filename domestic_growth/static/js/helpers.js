const emailInput = document.getElementById('id_email')
const queryString = window.location.search;

if (emailInput && queryString.includes('resend_email=True')){
    emailInput.focus()
}
