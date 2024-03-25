let viewMediaModalS = document.getElementById("view-media__modal-stories");
let mainContainerS = document.getElementById("main-container");
let closeViewMediaBtnS = document.getElementById("close-view-media__modal-btn-stories");

function viewMediaP(mediaLink) {
    let imageElement = document.getElementById('view-media__media-img');
    imageElement.src = mediaLink;
    viewMediaModalS.style.display = "block";
    mainContainerS.style.opacity = 0.3;

}


closeViewMediaBtnS.onclick = function() {
    viewMediaModalS.style.display = "none";
    mainContainerS.style.opacity = 1;

}
