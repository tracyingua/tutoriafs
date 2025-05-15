document.addEventListener("DOMContentLoaded", function () {
  
    const expertiseForm = document.getElementById("expertise-form");
    if (expertiseForm) {
        expertiseForm.addEventListener("submit", function (e) {
            e.preventDefault(); 

            let formData = new FormData(this);

            fetch(updateSubjectPricesUrl, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": csrfToken,
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showSuccessModal(); 
                    closeExpertiseModal(); 
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error("Error:", error));
        });
    }

    function showSuccessModal() {
        const successModal = document.getElementById("successfully-modal");
        if (successModal) {
            successModal.style.display = "flex";
        }
    }

    window.closelyModal = function () {
        const successModal = document.getElementById("successfully-modal");
        if (successModal) {
            successModal.style.display = "none";
        }
    };


    const modal = document.getElementById("expertise-modal");
    const openBtn = document.querySelector(".edit-expertise-btn");
    const closeBtn = modal ? modal.querySelector(".close") : null;

    if (openBtn && modal) {
        openBtn.addEventListener("click", function () {
            modal.style.display = "flex";
        });
    }

    if (closeBtn && modal) {
        closeBtn.addEventListener("click", function () {
            closeExpertiseModal();
        });
    }

    function closeExpertiseModal() {
        if (modal) {
            modal.style.display = "none";
        }
    }

    window.addEventListener("click", function (e) {
        if (modal && e.target === modal) {
            closeExpertiseModal();
        }
    });

  
    const priceInputs = document.querySelectorAll(".currency-input input");

    priceInputs.forEach(input => {
        input.addEventListener("focus", function () {
            let value = this.value.trim();
            if (!value.includes(".")) {
                this.value = parseFloat(this.value || 0).toFixed(2);
            }

            setTimeout(() => {
                let decimalIndex = this.value.indexOf(".");
                if (decimalIndex !== -1) {
                    this.setSelectionRange(decimalIndex + 3, decimalIndex + 3);
                }
            }, 50);
        });

        input.addEventListener("blur", function () {
            if (this.value !== "") {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });

        input.addEventListener("input", function () {
            let decimalIndex = this.value.indexOf(".");
            if (decimalIndex !== -1) {
                setTimeout(() => {
                    this.setSelectionRange(decimalIndex + 3, decimalIndex + 3);
                }, 50);
            }
        });
    });
});
