document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".info-btn").forEach((button) => {
        let popup = button.nextElementSibling; 

        button.addEventListener("click", function (event) {
            event.stopPropagation(); 
            let isVisible = popup.style.display === "block";
            
        
            document.querySelectorAll(".credentials-popup").forEach(p => p.style.display = "none");

           
            popup.style.display = isVisible ? "none" : "block";
        });

        document.addEventListener("click", function () {
            popup.style.display = "none"; 
        });

        popup.addEventListener("click", function (event) {
            event.stopPropagation(); 
        });
    });
});



document.addEventListener("DOMContentLoaded", function () {
    const successModal = document.getElementById("successModal");
    const confirmationModal = document.getElementById("confirmationModal");
    const confirmText = document.getElementById("confirmText");
    const confirmAction = document.getElementById("confirmAction");
    const cancelAction = document.getElementById("cancelAction");
    const closeSuccessModal = document.getElementById("closeSuccessModal");

    let selectedTutorId = null;

    function showConfirmation(tutorId) {
        selectedTutorId = tutorId;
        confirmText.textContent = "Are you sure you want to RESTRICT this tutor?";
        confirmationModal.style.display = "block";
        document.body.classList.add("modal-open");
    }

    function closeModal() {
        confirmationModal.style.display = "none";
        document.body.classList.remove("modal-open"); 
    }

    function sendRestrictionRequest() {
        if (!selectedTutorId) return;  // ✅ No need for `selectedAction`

        const url = `/restrict/${selectedTutorId}/`;

        fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": getCSRFToken() }
        })
        .then(response => response.json())
        .then(data => {
            console.log("Response:", data);  // ✅ Debugging

            if (data.status === "restricted") {  // ✅ Correct status check
                document.querySelector(`.restrict-btn[data-id="${selectedTutorId}"]`)
                    ?.closest(".tutor-item")?.remove();

                document.getElementById("successMessage").textContent = "Tutor Restricted!";
                successModal.style.display = "block";  // ✅ Show success modal
                document.body.classList.add("message-modal-open"); 
            }
            closeModal();
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        });
    }

    closeSuccessModal.addEventListener("click", function () {
        successModal.style.display = "none";
        document.body.classList.remove("message-modal-open");
    });

    document.querySelectorAll(".restrict-btn").forEach(button => {
        button.addEventListener("click", function () {
            let tutorId = this.getAttribute("data-id");
            showConfirmation(tutorId);
        });
    });

    cancelAction.addEventListener("click", closeModal);
    confirmAction.addEventListener("click", sendRestrictionRequest);

    function getCSRFToken() {
        return document.cookie.split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
    }
});
