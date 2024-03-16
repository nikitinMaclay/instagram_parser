let confirmModal = document.getElementById("confirm-download-modal");

let confirmInput = document.getElementById("confirm-download-filename__input");

let confirmBtn = document.getElementById("modal-confirm__confirm-btn");

confirmBtn.onclick = function() {
    confirmModal.style.display = "none";
}

function sendDownloadPostRequest(post_id) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/download_certain_post/' + post_id, true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            var downloadUrl = xhr.responseText;
            console.log(downloadUrl);
            confirmModal.style.display = "block";
            confirmInput.value = downloadUrl;
//            window.location.href = "/download_local_file_page/";
        }
    };
    xhr.send();
}