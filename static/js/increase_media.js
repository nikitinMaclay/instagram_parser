let viewMediaModal = document.getElementById("view-media__modal");
let mainContainer = document.getElementById("main-container");
let closeViewMediaBtn = document.getElementById("close-view-media__modal-btn");

function viewMedia(mediaLink, mediaPrevLink) {
    let videoElement = document.getElementById('view-media__media-vid');
    let sourceElement = videoElement.querySelector('source');
    sourceElement.src = mediaLink
    videoElement.poster = mediaPrevLink
    videoElement.load();
    viewMediaModal.style.display = "block";
    mainContainer.style.opacity = 0.3;

}


closeViewMediaBtn.onclick = function() {
    let videoElement = document.getElementById('view-media__media-vid');
    videoElement.pause();
    viewMediaModal.style.display = "none";
    mainContainer.style.opacity = 1;

}
