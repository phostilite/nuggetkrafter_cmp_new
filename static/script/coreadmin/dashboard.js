$(document).ready(function() {
    $.ajax({
        url: '/api/stats/', 
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            if (data.error) {
                console.error('Error: ' + data.error);
            } else {
                var stats = data.statistics_data;
                if (stats) {
                    $('#clients').text(stats.clients || 'N/A');
                    $('#users').text(stats.users || 'N/A');
                    $('#scorm_packages').text(stats.scorm_packages || 'N/A');
                    $('#assignments').text(stats.assignments || 'N/A');
                    $('#resets').text(stats.resets || 'N/A');
                    $('#status_checks').text(stats.status_checks || 'N/A');
                } else {
                    console.error('Error: statistics_data is not available');
                }
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error('AJAX error: ' + textStatus + ' : ' + errorThrown);
        }
    });
});