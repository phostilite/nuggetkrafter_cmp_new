function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function syncScorm(clientId, scormId) {
    $.ajax({
        url: '/api/get_scorm_data/' + clientId + '/' + scormId + '/',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            data.clientId = clientId;
            data.scormId = scormId;
            $.ajax({
                url: '/api/sync_courses/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(data),
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                },
                success: function (response) {
                    console.log('Course synced successfully:', response);
                    alert('Course synced successfully: ' + JSON.stringify(response));
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.error('Failed to sync course:', textStatus, errorThrown);
                    alert('Failed to sync course: ' + textStatus + ' ' + errorThrown);
                }
            });
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error('AJAX request failed:', textStatus, errorThrown);
            alert('AJAX request failed: ' + textStatus + ' ' + errorThrown);
        }
    });
}