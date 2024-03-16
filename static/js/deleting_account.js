function sendAccDeleteRequest(acc_id) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/delete_acc/' + acc_id, true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            console.log(xhr.responseText);
        }
        window.location.reload();

    };
    xhr.send();
}
