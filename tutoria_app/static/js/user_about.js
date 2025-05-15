document.addEventListener("DOMContentLoaded", function () {
    $('#grade').select2();

    // Hide all initially
    document.querySelectorAll('#topics-container .checkbox-label').forEach(el => {
        el.style.display = 'none';
    });
    document.querySelectorAll('#subtopics-container .checkbox-label').forEach(el => {
        el.style.display = 'none';
    });

    // Subjects – allow multiple selection
    document.querySelectorAll('#subjects-container input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            filterTopics();
        });
    });

    // Prevent checkboxes from closing anything if in dropdowns etc.
    document.querySelectorAll('.checkbox-label').forEach(label => {
        label.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    });

    // Handle Select All for Topics
    const selectAllTopics = document.getElementById('select-all-topics');
    if (selectAllTopics) {
        selectAllTopics.addEventListener('change', function () {
            document.querySelectorAll('#topics-container .checkbox-label').forEach(label => {
                if (label.style.display !== 'none') {
                    label.querySelector('input[type="checkbox"]').checked = this.checked;
                }
            });
            filterSubTopics();
        });
    }

    // Handle Select All for Subtopics
    const selectAllSubtopics = document.getElementById('select-all-subtopics');
    if (selectAllSubtopics) {
        selectAllSubtopics.addEventListener('change', function () {
            document.querySelectorAll('#subtopics-container .checkbox-label').forEach(label => {
                if (label.style.display !== 'none') {
                    label.querySelector('input[type="checkbox"]').checked = this.checked;
                }
            });
        });
    }
});

function updateSelectAllStatus() {
    // Topics
    const topicLabels = document.querySelectorAll('#topics-container .checkbox-label');
    const visibleTopics = Array.from(topicLabels).filter(label => label.style.display !== 'none');
    const checkedTopics = visibleTopics.filter(label => label.querySelector('input[type="checkbox"]').checked);
    const selectAllTopics = document.getElementById('select-all-topics');
    if (selectAllTopics) {
        selectAllTopics.checked = visibleTopics.length > 0 && checkedTopics.length === visibleTopics.length;
    }

    // Subtopics
    const subtopicLabels = document.querySelectorAll('#subtopics-container .checkbox-label');
    const visibleSubtopics = Array.from(subtopicLabels).filter(label => label.style.display !== 'none');
    const checkedSubtopics = visibleSubtopics.filter(label => label.querySelector('input[type="checkbox"]').checked);
    const selectAllSubtopics = document.getElementById('select-all-subtopics');
    if (selectAllSubtopics) {
        selectAllSubtopics.checked = visibleSubtopics.length > 0 && checkedSubtopics.length === visibleSubtopics.length;
    }
}

function filterTopics() {
    const selectedSubjects = Array.from(
        document.querySelectorAll('#subjects-container input[type="checkbox"]:checked')
    ).map(cb => cb.value);

    const selectAllTopics = document.getElementById('select-all-topics');
    const autoSelectTopics = selectAllTopics && selectAllTopics.checked;

    const topicLabels = document.querySelectorAll('#topics-container .checkbox-label');

    topicLabels.forEach(label => {
        const subjectId = label.dataset.subject;
        const checkbox = label.querySelector('input[type="checkbox"]');

        if (selectedSubjects.includes(subjectId)) {
            label.style.display = 'flex';
            if (autoSelectTopics) checkbox.checked = true;
        } else {
            label.style.display = 'none';
            checkbox.checked = false;
        }
    });

    updateSelectAllStatus();
    filterSubTopics();
    updateSelectAllVisibility();
}

function filterSubTopics() {
    const selectedTopics = Array.from(
        document.querySelectorAll('#topics-container input[type="checkbox"]:checked')
    ).map(cb => cb.value);

    const selectAllSubtopics = document.getElementById('select-all-subtopics');
    const autoSelectSubtopics = selectAllSubtopics && selectAllSubtopics.checked;

    const subtopicLabels = document.querySelectorAll('#subtopics-container .checkbox-label');

    subtopicLabels.forEach(label => {
        const topicId = label.dataset.topic;
        const checkbox = label.querySelector('input[type="checkbox"]');

        if (selectedTopics.includes(topicId)) {
            label.style.display = 'flex';
            if (autoSelectSubtopics) checkbox.checked = true;
        } else {
            label.style.display = 'none';
            checkbox.checked = false;
        }
    });

    if (selectedTopics.length === 0) {
        subtopicLabels.forEach(label => {
            label.style.display = 'none';
            label.querySelector('input[type="checkbox"]').checked = false;
        });
    }

    updateSelectAllStatus();
    updateSelectAllVisibility();
}

// Time Validation
function validateTime(input) {
    let timeSlot = input.closest(".time-slot");
    let startTimeInput = timeSlot.querySelector(".start-time");
    let endTimeInput = timeSlot.querySelector(".end-time");
    let errorSpan = timeSlot.querySelector(".time-error");
    let saveButton = document.querySelector(".save-button");

    let startTime = startTimeInput.value;
    let endTime = endTimeInput.value;

    errorSpan.textContent = "";
    errorSpan.style.display = "none";
    startTimeInput.classList.remove("error");
    endTimeInput.classList.remove("error");
    if (saveButton) saveButton.disabled = false;

    if (startTime && endTime) {
        let startDate = new Date("1970-01-01T" + startTime + ":00");
        let endDate = new Date("1970-01-01T" + endTime + ":00");
        let diffInMinutes = (endDate - startDate) / (1000 * 60);

        if (diffInMinutes < 60) {
            errorSpan.textContent = "End time must be at least one hour later than start time.";
            errorSpan.style.display = "block";
            endTimeInput.classList.add("error");
            if (saveButton) saveButton.disabled = true;
            return;
        }

        const morningStart = "07:00";
        const morningEnd = "12:00";
        const afternoonStart = "13:00";
        const afternoonEnd = "16:00";

        const isInMorningRange = (startTime >= morningStart && endTime <= morningEnd);
        const isInAfternoonRange = (startTime >= afternoonStart && endTime <= afternoonEnd);

        if (!(isInMorningRange || isInAfternoonRange)) {
            errorSpan.textContent = "Allowed time slots are only from 7:00 AM to 12:00 PM or 1:00 PM to 4:00 PM.";
            errorSpan.style.display = "block";
            startTimeInput.classList.add("error");
            endTimeInput.classList.add("error");
            if (saveButton) saveButton.disabled = true;
        }
    }
}



function addTimeSlot() {
    let container = document.getElementById("availability-container");
    let newSlot = document.createElement("div");
    newSlot.classList.add("time-slot");

    newSlot.innerHTML = `
        <select name="days[]" required>
            <option value="" disabled selected>Select a day</option>
            <option value="Monday">Monday</option>
            <option value="Tuesday">Tuesday</option>
            <option value="Wednesday">Wednesday</option>
            <option value="Thursday">Thursday</option>
            <option value="Friday">Friday</option>
        </select>
        <label class="from">From</label>
        <input type="time" name="start_times[]" class="start-time" 
            required min="07:00" max="19:00" step="3600" 
            pattern="[0-9]{2}:[0-9]{2}" onchange="validateTime(this)">
        <label class="to">To</label>
        <input type="time" name="end_times[]" class="end-time" 
            required min="07:00" max="19:00" step="3600" 
            pattern="[0-9]{2}:[0-9]{2}" onchange="validateTime(this)">
        <span class="time-error"></span>
        <button type="button" class="remove-button" onclick="removeTimeSlot(this)">
  <div class="x-button" aria-label="Remove time slot">&times;</div>
</button>

    `;

    container.appendChild(newSlot);
}

function removeTimeSlot(button) {
    button.closest(".time-slot").remove();
}


const style = document.createElement("style");
style.textContent = `
  .save-button:disabled {
    background-color: white;
    color: black;
    border: 1px solid black;
    opacity: 1;
    cursor: not-allowed;
  }
`;
document.head.appendChild(style);
