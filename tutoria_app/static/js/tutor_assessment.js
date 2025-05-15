document.addEventListener("DOMContentLoaded", function () {
    const questionBlocks = document.querySelectorAll(".question-block");
    const progressBar = document.getElementById("progress");
    const warning = document.getElementById("warning-message");
    let currentQuestionIndex = 0;

    function showQuestion(index) {
        questionBlocks.forEach((block, i) => {
            block.style.display = i === index ? "block" : "none";
        });

        document.getElementById("prev-btn").disabled = index === 0;
        document.getElementById("next-btn").style.display = index === questionBlocks.length - 1 ? "none" : "inline-block";
        document.getElementById("submit-btn").style.display = index === questionBlocks.length - 1 ? "inline-block" : "none";

        updateProgress(index);
    }

    function updateProgress(index) {
        let progressPercentage = ((index + 1) / questionBlocks.length) * 100;
        progressBar.style.width = `${progressPercentage}%`;
    }

    window.toggleAnswer = function (button) {
        button.classList.toggle("selected");
        updateSelectedAnswers(button);
    };

    function updateSelectedAnswers(button) {
        const questionId = button.getAttribute("data-question-id");
        const answerId = button.getAttribute("data-answer-id");
        const hiddenInput = document.getElementById(`selected-answers-${questionId}`);
        
        let selectedAnswers = [];
        document.querySelectorAll(`.question-block[data-question-id="${questionId}"] .answer-btn.selected`).forEach(btn => {
            selectedAnswers.push(btn.getAttribute("data-answer-id"));
        });
        
        hiddenInput.value = selectedAnswers.join(",");
    }

    function hasAtLeastOneAnswer(questionId) {
        const selectedButtons = document.querySelectorAll(`.question-block[data-question-id="${questionId}"] .answer-btn.selected`);
        return selectedButtons.length > 0;
    }

    document.getElementById("prev-btn").addEventListener("click", function () {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex--;
            showQuestion(currentQuestionIndex);
        }
    });

    document.getElementById("next-btn").addEventListener("click", function () {
        const currentBlock = questionBlocks[currentQuestionIndex];
        const questionId = currentBlock.getAttribute("data-question-id");

        if (!hasAtLeastOneAnswer(questionId)) {
            showWarning("Please select at least one answer before proceeding.");
            return;
        }

        if (currentQuestionIndex < questionBlocks.length - 1) {
            currentQuestionIndex++;
            showQuestion(currentQuestionIndex);
        }
    });

    document.getElementById("assessment-form").addEventListener("submit", function (event) {
        let allAnswered = true;

        questionBlocks.forEach(block => {
            const questionId = block.getAttribute("data-question-id");
            if (!hasAtLeastOneAnswer(questionId)) {
                allAnswered = false;
                block.classList.add("unanswered");
            }
        });

        if (!allAnswered) {
            event.preventDefault();
            showWarning("Please answer all questions before submitting.");
        }
    });

    function showWarning(message) {
        warning.textContent = message;
        warning.style.display = "block";
        warning.style.opacity = 1;

        setTimeout(() => {
            warning.style.opacity = 0;
        }, 3000);

        setTimeout(() => {
            warning.style.display = "none";
        }, 3500);
    }

    showQuestion(currentQuestionIndex);
});