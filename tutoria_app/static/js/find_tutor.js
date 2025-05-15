document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.querySelector(".search-input input");
    const subjectCheckboxes = document.querySelectorAll('input[name="subject"]');
    const tutorCards = document.querySelectorAll(".tutor-card");

    function filterTutors() {
        const searchQuery = searchInput.value.toLowerCase().trim();
        let selectedSubjects = Array.from(subjectCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value.toLowerCase());

        tutorCards.forEach(card => {
            const tutorSubjects = card.querySelector(`#subjects-full-${card.dataset.tutorId}`)?.innerText.toLowerCase() || "";
            const tutorName = card.querySelector(".tutor-details p:nth-of-type(2)")?.innerText.toLowerCase() || "";

            let matchesSearch = searchQuery === "" || tutorName.includes(searchQuery) || tutorSubjects.includes(searchQuery);
            let matchesSubject = selectedSubjects.length === 0 || selectedSubjects.some(subject => tutorSubjects.includes(subject));

            card.style.display = (matchesSearch && matchesSubject) ? "flex" : "none";
        });
    }

    searchInput.addEventListener("input", filterTutors);
    subjectCheckboxes.forEach(checkbox => checkbox.addEventListener("change", filterTutors));

    window.toggleFilter = function () {
        let filterBox = document.getElementById("subject-filter");
        filterBox.style.display = filterBox.style.display === "flex" ? "none" : "flex";
    };
});


    
    
    function toggleTopics(tutorId) {
        let short = document.getElementById("topics-short-" + tutorId);
        let full = document.getElementById("topics-full-" + tutorId);
        let button = document.getElementById("toggle-btn-" + tutorId);
        
        if (full.style.display === "none") {
          full.style.display = "inline";
          short.style.display = "none";
          button.innerText = "Less";
        } else {
          full.style.display = "none";
          short.style.display = "inline";
          button.innerText = " More";
        }
    }
    
    function toggleSubjects(tutorId) {
        let short = document.getElementById("subjects-short-" + tutorId);
        let full = document.getElementById("subjects-full-" + tutorId);
        let button = document.getElementById("toggle-subjects-btn-" + tutorId);
        
        if (full.style.display === "none") {
          full.style.display = "inline";
          short.style.display = "none";
          button.innerText = "Less";
        } else {
          full.style.display = "none";
          short.style.display = "inline";
          button.innerText = "+ More";
        }
    }