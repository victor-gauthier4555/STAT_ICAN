document.addEventListener("DOMContentLoaded", function() {
    // Get the file input element
    const fileInput = document.getElementById("fileInput");
    // Get the file text span element
    const fileText = document.querySelector(".fileText");

    // Add an event listener to the file input element
    fileInput.addEventListener("change", function() {
        // Check if a file has been selected
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0]; // Get the selected file
            // Update the text of the file button
            fileText.textContent = "FILE ADDED"; 

            const reader = new FileReader();
            reader.onload = function(e) {
                const fileContent = e.target.result;
                localStorage.setItem('fileContent', fileContent);
                console.log('File content saved to localStorage');
            };
            reader.readAsDataURL(file); // Read the file as a base64 data URL

        } else {
            // If no file is selected, revert back to the original text
            fileText.textContent = "ADD FILE";
        }
    });
});
