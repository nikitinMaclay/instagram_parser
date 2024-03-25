function uncheckAllCheckboxes() {
    function uncheck() {
        var checkboxes = document.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(function(checkbox) {
            checkbox.checked = false;
        });
    }

    setTimeout(uncheck, 5000);
}