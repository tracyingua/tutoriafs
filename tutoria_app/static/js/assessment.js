document.addEventListener("DOMContentLoaded", function () {
    const questionBlocks = document.querySelectorAll(".question-block");
    const progressBar = document.getElementById("progress");
    let currentQuestionIndex = 0;

    function updateProgressBar() {
        let progressPercentage = ((currentQuestionIndex + 1) / questionBlocks.length) * 100;
        progressBar.style.width = progressPercentage + "%";
    }

    function showQuestion(index) {
        questionBlocks.forEach((block, i) => {
            block.style.display = i === index ? "block" : "none";
        });

        document.getElementById("prev-btn").disabled = index === 0;
        document.getElementById("next-btn").style.display = index === questionBlocks.length - 1 ? "none" : "inline-block";
        document.getElementById("submit-btn").style.display = index === questionBlocks.length - 1 ? "inline-block" : "none";

        updateProgressBar();
    }

    function restorePreviousSelections() {
        questionBlocks.forEach(block => {
            const questionId = block.getAttribute("data-question-id");
            const selectedInput = document.getElementById(`selected-answer-${questionId}`);
            const selectedAnswerId = selectedInput.value;

            if (selectedAnswerId) {
                const selectedButton = block.querySelector(`[data-answer-id="${selectedAnswerId}"]`);
                if (selectedButton) {
                    selectedButton.classList.add("selected");
                }
            }
        });
    }

    document.getElementById("prev-btn").addEventListener("click", function () {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex--;
            showQuestion(currentQuestionIndex);
        }
    });

    document.getElementById("next-btn").addEventListener("click", function () {
        if (currentQuestionIndex < questionBlocks.length - 1) {
            currentQuestionIndex++;
            showQuestion(currentQuestionIndex);
        }
    });

    window.selectAnswer = function (button) {
        const questionId = button.getAttribute("data-question-id");
        const answerId = button.getAttribute("data-answer-id");

        document.querySelectorAll(`[data-question-id="${questionId}"]`).forEach(btn => btn.classList.remove("selected"));
        button.classList.add("selected");

        document.getElementById(`selected-answer-${questionId}`).value = answerId;

        console.log("Selected Question:", questionId, "Answer:", answerId);
    };

    showQuestion(currentQuestionIndex);
    restorePreviousSelections();
});
