$(".edit-user-link").click(function (event) {
    event.preventDefault();
    var clientId = $(this).data("clientId");
    var userId = $(this).data("userId");

    $.ajax({
        url: "/coreadmin/clients/" + clientId + "/users/" + userId + "/details/",   
        dataType: "json",
        success: function (data) {
            $("#id_first_name").val(data.first_name);
            $("#id_last_name").val(data.last_name);
            $("#id_email").val(data.email);
            $("#id_scorm_consumed").val(data.scorm_consumed);
            $("#id_learner_id").val(data.learner_id);
            $("#id_cloudscorm_user_id").val(data.cloudscorm_user_id);
            $("#userUpdateForm").data("userId", userId);
            $("#editUserModal").modal("show");
        },
    });
});


$("#userUpdateForm").submit(function (event) {
    event.preventDefault();
    var formData = $(this).serialize();
    var userId = $(this).data("userId");
    var clientId = $(this).data("clientId");

    $.ajax({
        url: "/coreadmin/clients/" + clientId + "/users/" + userId + "/update/",
        type: "POST",
        data: formData,
        beforeSend: function (xhr) {
            xhr.setRequestHeader(
                "X-CSRFToken",
                $("input[name=csrfmiddlewaretoken]").val()
            );
        },
        success: function (data) {
            console.log('Success callback called. Server response:', data); // Log server response

            if (data.success) {
                var modal = document.querySelector("#editUserModal");
                modal.classList.add("hidden");
                modal.setAttribute("aria-hidden", "true");

                alert("User updated successfully!");
                location.reload();
            } else {
                var errors = data.errors;
                for (var field in errors) {
                    var errorMessages = errors[field];
                    alert("Error in " + field + ": " + errorMessages.join(", "));
                }
            }
            location.reload();
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log('Error callback called. jqXHR:', jqXHR, 'textStatus:', textStatus, 'errorThrown:', errorThrown); // Log error info
        },
    });
});