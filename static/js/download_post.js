
function sendDownloadPostRequest(post_id) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/download_certain_post/' + post_id, true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            console.log("success");
            window.location.href = '/send_local_zip/' + post_id
        }
    };
    xhr.send();
}