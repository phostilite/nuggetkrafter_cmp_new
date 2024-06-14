$(document).ready(function() {
    $.ajax({
        url: "/scorm/get_all_scorms/",
        type: "GET",
        dataType: "html",
        success: function(data) {
            $("#dropdownSearch ul").html(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error("AJAX request failed:", textStatus, errorThrown);
        }
    });
});

$(document).on(
    "click",
    "#dropdownSearchButton",
    function(e) {
        e.preventDefault(); 
        $("#dropdownSearch").dropdown("show");
    }
);