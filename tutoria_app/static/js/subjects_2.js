document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.querySelector(".search-input input");
    const subjectItems = document.querySelectorAll(".subject-item");

    searchInput.addEventListener("input", function () {
        const searchText = searchInput.value.toLowerCase();
        let hasResults = false;

        subjectItems.forEach(item => {
            const topicName = item.querySelector("h3").textContent.toLowerCase();
            if (topicName.includes(searchText)) {
                item.style.display = "flex"; 
                hasResults = true;
            } else {
                item.style.display = "none"; 
            }
        });


        const noResultsMessage = document.querySelector(".no-results");
        if (!hasResults) {
            if (!noResultsMessage) {
                const message = document.createElement("p");
                message.className = "no-results";
                message.textContent = "No topics available.";
                document.querySelector(".subject-list").appendChild(message);
            }
        } else {
            if (noResultsMessage) {
                noResultsMessage.remove();
            }
        }
    });
});
