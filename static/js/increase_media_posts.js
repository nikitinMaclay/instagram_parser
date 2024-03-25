let viewMediaModal = document.getElementById("view-media__modal-posts");
let mainContainer = document.getElementById("main-container");
let closeViewMediaBtn = document.getElementById("close-view-media__modal-btn-posts");

function viewMediaP(mediaLink) {
    let imageElement = document.getElementById('view-media__media-img');
    imageElement.src = mediaLink;
    viewMediaModal.style.display = "block";
    mainContainer.style.opacity = 0.3;

}


closeViewMediaBtn.onclick = function() {
    viewMediaModal.style.display = "none";
    mainContainer.style.opacity = 1;

}
