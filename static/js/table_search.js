document.getElementById('searchInput').addEventListener('input', function() {
  var searchText = this.value.toLowerCase();
  var rows = document.getElementById('data-table').rows;

  for (var i = 1; i < rows.length; i++) {
    var row = rows[i];
    var cells = row.getElementsByTagName('td');
    var matchFound = false;

    for (var j = 0; j < cells.length; j++) {
      var cellText = cells[j].textContent.toLowerCase();
      if (cellText.includes(searchText)) {
        matchFound = true;
        break;
      }
    }

    if (matchFound) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  }
});