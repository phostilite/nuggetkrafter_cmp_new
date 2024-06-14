$(".edit-client-link").click(function (event) {
    event.preventDefault();
    var clientId = $(this).data("clientId");

    $.ajax({
        url: "/coreadmin/clients/" + clientId + "/details/",
        dataType: "json",
        success: function (data) {
            $("#id_first_name").val(data.first_name);
            $("#id_last_name").val(data.last_name);
            $("#id_email").val(data.email);
            $("#id_contact_phone").val(data.contact_phone);
            $("#id_company").val(data.company);
            $("#id_domains").val(data.domains);
            $("#id_lms_url").val(data.lms_url);
            $("#id_lms_api_key").val(data.lms_api_key);
            $("#id_lms_api_secret").val(data.lms_api_secret);
            $("#clientUpdateForm").data("clientId", clientId);
            $("#editClientModal").modal("show");
        },
    });
});

$("#clientUpdateForm").submit(function (event) {
    event.preventDefault();
    var formData = $(this).serialize();
    var clientId = $(this).data("clientId");

    $.ajax({
        url: "/coreadmin/clients/" + clientId + "/update/",
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
                var modal = document.querySelector("#editClientModal");
                modal.classList.add("hidden");
                modal.setAttribute("aria-hidden", "true");

                alert("Client updated successfully!");
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