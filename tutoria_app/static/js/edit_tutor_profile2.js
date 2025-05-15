document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("edit-tutor-profile-modal");
    const openBtn = document.querySelector(".edit-tutor-profile");
    const closeBtn = document.querySelector(".close-tutor-modal");
    const fileInput = document.getElementById("tutor-profile-pic");
    const imagePreview = document.getElementById("profile-preview");
    const form = document.getElementById("edit-tutor-profile-form");
    const successModal = document.getElementById("successfully-modal");
    const closeSuccessBtn = document.querySelector(".mew-close-modal");

    if (openBtn) {
        openBtn.addEventListener("click", function () {
            modal.style.display = "flex";
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", function () {
            modal.style.display = "none";
        });
    }

    window.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });

    fileInput.addEventListener("change", function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            let formData = new FormData(this);

            fetch(editProfileUrl2, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log("Received response:", data);
                if (data.success) {
                    modal.style.display = "none";
                    successModal.style.display = "flex"; 
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error("Error updating profile:", error));
        });
    }

    if (closeSuccessBtn) {
        closeSuccessBtn.addEventListener("click", function () {
            successModal.style.display = "none";
            location.reload(); 
        });
    }
});
