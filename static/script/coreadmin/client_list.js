document.getElementById('table-search-clients').addEventListener('input', searchClients);

function searchClients() {
    const searchInput = document.getElementById('table-search-clients').value.toLowerCase();
    const tableRows = document.getElementsByTagName('tr');

    for (let i = 1; i < tableRows.length; i++) {
    const row = tableRows[i];
    const name = row.getElementsByTagName('th')[0].getElementsByTagName('div')[0].textContent.toLowerCase();
    const company = row.getElementsByTagName('td')[0].textContent.toLowerCase();
    const contact_phone = row.getElementsByTagName('td')[1].textContent.toLowerCase();

    if (company.includes(searchInput) || contact_phone.includes(searchInput) || name.includes(searchInput)) {
        row.style.display = '';
    } else {
        row.style.display = 'none';
    }
    }
}