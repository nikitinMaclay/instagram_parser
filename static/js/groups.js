let openGroupModalBtn = document.getElementById("group-adding__modal__btn");
let groupModal = document.getElementById("new-group-adding__modal");

let closeGroupModalBtn = document.getElementById("close-group-adding-modal");

openGroupModalBtn.onclick = function() {
    groupModal.style.display = "block";
}

closeGroupModalBtn.onclick = function() {
    groupModal.style.display = "none";
}


let openAccountModalBtn = document.getElementById("new-acc-adding-btn");


function sendDeleteRequest(group_id) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/delete_group/' + group_id, true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            console.log(xhr.responseText);
        }
        window.location.href = '/1';

    };
    xhr.send();
}

let changeGroupModal = document.getElementById("change-account-group-modal-window");

let closeChangeGroupModalBtn = document.getElementById("close-change-account-group-modal");


function ChangeGroup(acc_id) {
    console.log(acc_id);
    hidden_account_id_field = document.getElementById("accountIdField");
    hidden_account_id_field.value = acc_id
    changeGroupModal.style.display = "block";

}

closeChangeGroupModalBtn.onclick = function() {
    changeGroupModal.style.display = "none";
}
