$(".edit-scorm-link").click(function (event) {
    event.preventDefault();
    var scormId = $(this).data("scormId");

    $.ajax({
        url: "/coreadmin/scorm/" + scormId + "/details/",
        dataType: "json",
        success: function (data) {
            $("#id_title").val(data.title);
            $("#id_course_code").val(data.course_code);
            $("#id_category").val(data.category);
            $("#id_duration").val(data.duration);
            $("#id_scorm_id").val(data.scorm_id);
            $("#id_launch_url").val(data.launch_url);
            $("#id_short_description").val(data.short_description);
            $("#id_long_description").val(data.long_description);
            $("#scormUpdateForm").data("scormId", scormId);
            $("#editScormModal").modal("show");
        },
    });
});


$("#scormUpdateForm").submit(function (event) {
    event.preventDefault();
    var formData = $(this).serialize();
    var scormId = $(this).data("scormId");

    $.ajax({
        url: "/coreadmin/scorm/" + scormId + "/update/",
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
                var modal = document.querySelector("#editScormModal");
                modal.classList.add("hidden");
                modal.setAttribute("aria-hidden", "true");

                alert("SCORM updated successfully!");
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