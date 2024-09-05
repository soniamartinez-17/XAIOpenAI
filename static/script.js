//------------- aesthetic of the page -------------
document.addEventListener('DOMContentLoaded', function() {
    const textInput = document.getElementById('textInput');
    const dropdown1 = document.getElementById('dropdown1');
    const fileInput = document.getElementById('fileInput');
    const submitButton = document.getElementById('submitButton');

    function validateForm() {
        if (textInput.value && dropdown1.value && fileInput.files.length > 0) {
            submitButton.disabled = false;
        } else {
            submitButton.disabled = true;
        }
    }

    textInput.addEventListener('input', validateForm);
});

function toggleTextInput() {
    var textInput = document.getElementById("textInput");

    if (textInput.style.display === "none" || textInput.style.display === "") {
        textInput.style.display = "block";
    } else {
        textInput.style.display = "none";
    }
}

document.getElementById('userForm').addEventListener('submit', function(event) {

    document.getElementById('confirmation').style.display = 'block';

});