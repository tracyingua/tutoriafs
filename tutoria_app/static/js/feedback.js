document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("feedback-modal");
    const openModalBtn = document.querySelector(".feedback-btn");
    const closeModalBtn = document.getElementById("cancel-feedback");
    const submitBtn = document.querySelector(".feedback-buttons[type='submit']");
    const stars = document.querySelectorAll(".star");
    const ratingInput = document.getElementById("rating-value");
    const commentBox = document.getElementById("feedback-comment");

    let selectedRating = 0;


    openModalBtn?.addEventListener("click", () => {
        modal.style.display = "flex";
    });


    closeModalBtn?.addEventListener("click", () => {
        modal.style.display = "none";
    });

 
    stars.forEach((star, index) => {
        star.addEventListener("mouseover", () => {
            stars.forEach((s, i) => {
                s.style.color = i <= index ? "gold" : "#ddd";
            });
        });

        star.addEventListener("mouseout", () => {
            stars.forEach((s, i) => {
                s.style.color = i < selectedRating ? "gold" : "#ddd";
            });
        });

        star.addEventListener("click", () => {
            selectedRating = index + 1;
            ratingInput.value = selectedRating; 
            stars.forEach((s, i) => {
                s.classList.toggle("selected", i < selectedRating);
            });
        });
    });


    submitBtn.addEventListener("click", (event) => {
        if (selectedRating === 0) {
            event.preventDefault();
          
        }
    });


    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});
