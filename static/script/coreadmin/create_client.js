function createClient(event) {
    event.preventDefault();

    const form = document.getElementById('create-client-form');
    const formData = new FormData(form);

    fetch('/coreadmin/clients/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
        },
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        console.log('Server response:', data);
        if (data.success) {
            alert('Client created successfully!');
            form.reset();
        } else {
            const errorMessages = JSON.parse(data.errors);
            let allErrors = [];
            for (const field in errorMessages) {
                for (const error of errorMessages[field]) {
                    allErrors.push(`${field}: ${error.message}`);
                }
            }
            alert(allErrors.join('\n'));
        }
    })
    .catch(error => {
        alert('An error occurred while creating the client.');
        console.error('Error:', error);
    });
}

function checkUsernameAvailability(username) {
    if (username.trim() !== '') {
        fetch('/api/check_username/' + username)
        .then(response => response.json())
        .then(data => {
            const messageElement = document.getElementById('usernameAvailabilityMessage');
            if (data.is_available) {
                messageElement.textContent = 'Username is available';
                messageElement.style.color = 'green';
            } else {
                messageElement.textContent = 'Username is not available';
                messageElement.style.color = 'red';
            }
        });
    } else {
        const messageElement = document.getElementById('usernameAvailabilityMessage');
        messageElement.textContent = '';
    }
}

function checkPasswordMatch() {
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');
    const messageElement = document.getElementById('passwordMatchMessage');
    const passwordFields = document.getElementsByClassName('password-field');

    if (password1.value !== '' && password2.value !== '') {
        if (password1.value === password2.value) {
            messageElement.textContent = 'Passwords match';
            messageElement.style.color = 'green';
            for (let i = 0; i < passwordFields.length; i++) {
                passwordFields[i].style.borderColor = 'green';
            }
        } else {
            messageElement.textContent = 'Passwords do not match';
            messageElement.style.color = 'red';
            for (let i = 0; i < passwordFields.length; i++) {
                passwordFields[i].style.borderColor = 'red';
            }
        }
    } else {
        messageElement.textContent = '';
        for (let i = 0; i < passwordFields.length; i++) {
            passwordFields[i].style.borderColor = '';
        }
    }
}