 document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".info-btn").forEach((button) => {
        let popup = button.nextElementSibling; 

        button.addEventListener("click", function (event) {
            event.stopPropagation(); 
            let isVisible = popup.style.display === "flex";
            
        
            document.querySelectorAll(".credentials-popup").forEach(p => p.style.display = "none");

           
            popup.style.display = isVisible ? "none" : "flex";
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
    let selectedAction = null;

    function showConfirmation(tutorId, action) {
        selectedTutorId = tutorId;
        selectedAction = action;

        confirmText.textContent = action === "approve"
            ? "Are you sure you want to APPROVE this tutor?"
            : "Are you sure you want to DECLINE this tutor?";

        confirmationModal.style.display = "flex";
        document.body.classList.add("modal-open");
    }

    function closeModal() {
        confirmationModal.style.display = "none";
        document.body.classList.remove("modal-open"); 
    }

    function sendApprovalRequest() {
        if (!selectedTutorId || !selectedAction) return;

        const url = selectedAction === "approve"
            ? `/approve/${selectedTutorId}/`
            : `/decline/${selectedTutorId}/`;

        fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": getCSRFToken() }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === selectedAction + "d") { 
                document.querySelector(`.approve-btn[data-id="${selectedTutorId}"]`)
                    ?.closest(".tutor-item")?.remove();

                document.getElementById("successMessage").textContent =
                    selectedAction === "approve" ? "Tutor Approved!" : "Tutor Declined!";
                successModal.style.display = "flex";
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

    document.querySelectorAll(".approve-btn").forEach(button => {
        button.addEventListener("click", function () {
            let tutorId = this.getAttribute("data-id");
            showConfirmation(tutorId, "approve");
        });
    });

    document.querySelectorAll(".decline-btn").forEach(button => {
        button.addEventListener("click", function () {
            let tutorId = this.getAttribute("data-id");
            showConfirmation(tutorId, "decline");
        });
    });

    cancelAction.addEventListener("click", closeModal);
    confirmAction.addEventListener("click", sendApprovalRequest);

    function getCSRFToken() {
        return document.cookie.split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
    }
});
