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


$(document).ready(function() {
    $.ajax({
        url: '/api/activities/',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            if (data.error) {
                console.error('Error: ' + data.error);
            } else {
                var activities = data.activities_data;
                if (activities) {
                    var activitiesList = $('#recent-activities-list');
                    activitiesList.empty();  // Clear the list
                    activities.forEach(function(activity) {
                        var li = $('<li></li>').text(activity.message);
                        activitiesList.append(li);
                    });
                } else {
                    console.error('Error: activities_data is not available');
                }
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error('AJAX error: ' + textStatus + ' : ' + errorThrown);
        }
    });
});

$(document).ready(function() {
    $.ajax({
        url: '/api/client_users/',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            if (data.error) {
                console.error('Error: ' + data.error);
            } else {
                var clientUsers = data.client_users_data;
                if (clientUsers) {
                    var userManagementTable = $('#user-management-table tbody');
                    userManagementTable.empty();
                    clientUsers.forEach(function(user) {
                        var tr = $('<tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700"></tr>');
                        tr.append($('<td class="px-6 py-4"></td>').text(user.id));
                        tr.append($('<td class="px-6 py-4"></td>').text(user.first_name + ' ' + user.last_name));
                        tr.append($('<td class="px-6 py-4"></td>').text(user.email));
                        tr.append($('<td class="px-6 py-4"></td>').text(user.client));
                        tr.append($('<td class="px-6 py-4"></td>').text(user.scorm_consumed));
                        userManagementTable.append(tr);
                    });
                } else {
                    console.error('Error: client_users_data is not available');
                }
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error('AJAX error: ' + textStatus + ' : ' + errorThrown);
        }
    });
});

$(document).ready(function() {
    $.ajax({
        url: '/api/clients/',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            if (data.error) {
                console.error('Error: ' + data.error);
            } else {
                var clients = data.clients_data;
                if (clients) {
                    var clientManagementTable = $('#client-management-table tbody');
                    clientManagementTable.empty();
                    clients.forEach(function(client) {
                        var tr = $('<tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700"></tr>');
                        tr.append($('<td class="px-6 py-4"></td>></td>').text(client.id));
                        tr.append($('<td class="px-6 py-4"></td>></td>').text(client.first_name + ' ' + client.last_name));
                        tr.append($('<td class="px-6 py-4"></td>></td>').text(client.email));
                        tr.append($('<td class="px-6 py-4"></td>></td>').text(client.contact_phone));
                        tr.append($('<td class="px-6 py-4"></td>></td>').text(client.company));
                        clientManagementTable.append(tr);
                    });
                } else {
                    console.error('Error: clients_data is not available');
                }
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error('AJAX error: ' + textStatus + ' : ' + errorThrown);
        }
    });
});


// Fetch data from the server_status_api endpoint
fetch('https://cmp.nuggetkrafter.com/api/server_status_api/')
    .then(response => response.json())
    .then(data => {
        // Extract the server status and instance details from the response
        const serverStatus = data.server_status;
        const instanceDetails = data.instance_details;

        // Assign the server status to the server-status element
        document.getElementById('server-status').textContent = serverStatus;

        // Change the indicator color based on the server status
        const indicator = document.getElementById('server-status-indicator');
        if (serverStatus === 'Operational') {
            indicator.classList.remove('bg-red-500');
            indicator.classList.add('bg-green-500');
        } else {
            indicator.classList.remove('bg-green-500');
            indicator.classList.add('bg-red-500');
        }

        // Assign the instance details to the respective elements
        document.getElementById('instance-id').textContent = instanceDetails.instance_id;
        document.getElementById('instance-type').textContent = instanceDetails.instance_type;
        document.getElementById('instance-state').textContent = instanceDetails.instance_state;
        document.getElementById('launch-time').textContent = instanceDetails.launch_time;
        document.getElementById('private-ip').textContent = instanceDetails.private_ip;
        document.getElementById('public-ip').textContent = instanceDetails.public_ip;
        document.getElementById('availability-zone').textContent = instanceDetails.availability_zone;
        document.getElementById('subnet-id').textContent = instanceDetails.subnet_id;
        document.getElementById('vpc-id').textContent = instanceDetails.vpc_id;
        document.getElementById('uptime').textContent = instanceDetails.uptime;
    })
    .catch(error => console.error('Error:', error));