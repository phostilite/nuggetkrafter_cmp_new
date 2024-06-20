document.getElementById('table-search').addEventListener('input', searchUsers);

function searchUsers() {
    const searchInput = document.getElementById('table-search').value.toLowerCase();
    const tableRows = document.getElementsByTagName('tr');

    for (let i = 1; i < tableRows.length; i++) {
    const row = tableRows[i];
    const name = row.getElementsByTagName('td')[0].textContent.toLowerCase();
    const email = row.getElementsByTagName('td')[1].textContent.toLowerCase();
    const client = row.getElementsByTagName('td')[2].textContent.toLowerCase();

    if (name.includes(searchInput) || email.includes(searchInput) || client.includes(searchInput)) {
        row.style.display = '';
    } else {
        row.style.display = 'none';
    }
    }
}