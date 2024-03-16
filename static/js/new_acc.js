let openAccModalBtn = document.getElementById("new-acc-adding-btn");
let accModal = document.getElementById("acc-modal-window");

let closeAccModalBtn = document.getElementById("close-acc-modal");

openAccModalBtn.onclick = function() {
    accModal.style.display = "block";
}

closeAccModalBtn.onclick = function() {
    accModal.style.display = "none";
}