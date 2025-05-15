document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.querySelector(".search-bar input");
    const subjectCards = document.querySelectorAll(".subject-card");
    const noResultsMessage = document.getElementById("no-results");
    const subjectsGrid = document.querySelector(".subjects-grid");

    searchInput.addEventListener("input", function() {
        const searchText = searchInput.value.toLowerCase();
        let hasResults = false;

        subjectCards.forEach(card => {
            const subjectName = card.textContent.toLowerCase();
            if (subjectName.includes(searchText)) {
                card.style.display = "block";
                hasResults = true;
            } else {
                card.style.display = "none";
            }
        });


        noResultsMessage.style.display = hasResults ? "none" : "flex";

     
    });
});