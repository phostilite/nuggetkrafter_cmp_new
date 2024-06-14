document.getElementById('table-search-users').addEventListener('input', searchUsers);

function searchUsers() {
    const searchInput = document.getElementById('table-search-users').value.toLowerCase();
    const tableRows = document.getElementsByTagName('tr');

    for (let i = 1; i < tableRows.length; i++) {
    const row = tableRows[i];
    const name = row.getElementsByTagName('th')[0].getElementsByTagName('div')[0].textContent.toLowerCase();

    if (name.includes(searchInput)) {
        row.style.display = '';
    } else {
        row.style.display = 'none';
    }
    }
}