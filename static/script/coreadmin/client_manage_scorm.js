document.getElementById('table-search').addEventListener('input', searchSCORMs);

function searchSCORMs() {
    const searchInput = document.getElementById('table-search').value.toLowerCase();
    const tableRows = document.getElementsByTagName('tr');

    for (let i = 1; i < tableRows.length; i++) {
    const row = tableRows[i];
    const title = row.getElementsByTagName('td')[0].textContent.toLowerCase();
    const category = row.getElementsByTagName('td')[1].textContent.toLowerCase();

    if (title.includes(searchInput) || category.includes(searchInput)) {
        row.style.display = '';
    } else {
        row.style.display = 'none';
    }
    }
}