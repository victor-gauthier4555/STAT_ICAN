// Add an event listener to the link
document.getElementById('boxappear').addEventListener('click', function(event) {
    // Prevent the default action of the link
    event.preventDefault();
    // Display the message box
    document.getElementById('messageBox').classList.remove('hidden');

});

// Add an event listener to the link
document.getElementById('boxgone').addEventListener('click', function(event) {
    // Prevent the default action of the link
    event.preventDefault();
    // Display the message box
    document.getElementById('messageBox').classList.add('hidden');

});


// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function() {
    // Get the file input element
    const fileInput = document.getElementById("fileInput");
    // Get the file label element
    const fileLabel = document.querySelector(".fileLabel");
    // Get the file text span element
    const fileText = document.querySelector(".fileText");

    // Add an event listener to the file input element
    fileInput.addEventListener("change", function() {
        // Check if a file has been selected
        if (fileInput.files.length > 0) {
            // Update the text of the file button

            var fileName = this.files[0].name;
            fileText.textContent  = 'Selected file: ' + fileName; 
            //fileText.textContent = "FILE ADDED";            

        } else {
            // If no file is selected, revert back to the original text
            fileText.textContent = "ADD FILE";
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const processForm = document.getElementById('processForm');

    processForm.addEventListener('submit', function(event) {

        const fileContent = localStorage.getItem('fileContent');

        if (fileContent) {
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'fileContent';
            hiddenInput.value = fileContent;
            processForm.appendChild(hiddenInput);

            console.log('File content retrieved from localStorage');
            processForm.submit(); // Submit the form with file content
        } else {
            alert('No file content found in localStorage');
        }
    });
});
