let openAccModalBtn = document.getElementById("new-acc-adding-btn");
let accModal = document.getElementById("acc-modal-window");

let closeAccModalBtn = document.getElementById("close-acc-modal");

openAccModalBtn.onclick = function() {
    accModal.style.display = "block";
}

closeAccModalBtn.onclick = function() {
    accModal.style.display = "none";
}


let openSevAccsModalBtn = document.getElementById("new-several-accs-adding-btn");
let sevAccModal = document.getElementById("sev-accs-modal-window");

let closeSevAccModalBtn = document.getElementById("close-sev-accs-modal");

openSevAccsModalBtn.onclick = function() {
    sevAccModal.style.display = "block";
}

closeSevAccModalBtn.onclick = function() {
    sevAccModal.style.display = "none";
}