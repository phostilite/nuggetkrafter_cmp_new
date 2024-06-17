const form = document.querySelector('form');
const loadingOverlay = document.getElementById('loading-overlay');

form.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent form submission

    loadingOverlay.style.display = 'block'; // Show loading overlay

    // Actual form submission
    form.submit();
});

// After successful upload
loadingOverlay.style.display = 'none'; // Hide loading overlay

// Assuming you're using AJAX to submit the form
$.ajax({
    url: '/coreadmin/scorm/upload/', // Replace with your actual URL
    method: 'POST',
    data: formData,
    success: function(response) {
        // Handle successful upload
        loadingSpinner.style.display = 'none'; // Hide loading spinner
        formContainer.style.filter = 'none'; // Remove blur effect
        alert('SCORM uploaded successfully!');
    },
    error: function(xhr, status, error) {
        // Handle error
        console.error(error);
        alert('An error occurred while uploading the SCORM.', error);
    }
});