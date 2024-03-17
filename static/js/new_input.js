document.getElementById("addInputBtn").addEventListener("click", function() {
    var container = document.getElementById("account-link-wrapper");
    var input = document.createElement("input");
    input.type = "text";
    input.className = "page-url-field";
    input.placeholder = "Instagram nickname";
    input.name = "account-link";
    input.required = true;
    container.appendChild(input);
});