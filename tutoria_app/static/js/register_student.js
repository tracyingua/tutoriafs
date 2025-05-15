function previewImage(event) {
    var input = event.target;
    var reader = new FileReader();

    reader.onload = function () {
        var profileImg = document.querySelector(".profile-photo");
        if (profileImg) {
            profileImg.src = reader.result;
        }
    };

    if (input.files && input.files[0]) {
        reader.readAsDataURL(input.files[0]);
    }
}


function goBack() {
    window.location.href = goBackUrl;
}


document.addEventListener("DOMContentLoaded", function () {
    var fileInput = document.getElementById("id_profile_photo");
    if (fileInput) {
        fileInput.addEventListener("change", previewImage);
    }

    var backButton = document.querySelector(".back-button");
    if (backButton) {
        backButton.addEventListener("click", goBack);
    }
});
