document.addEventListener("DOMContentLoaded", function () {
   
    const modal = document.getElementById("scheduleModal");
    const openModal = document.querySelector(".schedule-btn");
    const closeModal = document.getElementById("closeModal");
    const totalHoursDisplay = document.getElementById("totalHoursDisplay");
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const selectedSubjectInput = document.getElementById("selectedSubject");
    const selectedTopicInput = document.getElementById("selectedTopic");
    const selectedDaysInput = document.getElementById("selectedDays");
    const saveButton = document.querySelector("#scheduleForm button[type='submit']");
    const topicContainer = document.querySelector(".topic-container");
    const tutoringDaysContainer = document.getElementById("selectedDaysContainer");
    const dayOrder = ['Monday','Tuesday','Wednesday','Thursday','Friday'];
    const container = document.getElementById('availableDaysContainer');

    const buttons = Array.from(container.querySelectorAll('.repeat-day-btn'));

    buttons.sort((a, b) => {
 
      let i = dayOrder.indexOf(a.dataset.day);
      let j = dayOrder.indexOf(b.dataset.day);
 
      if (i === -1) i = Infinity;
      if (j === -1) j = Infinity;
      return i - j;
    });


    async function checkForExistingSchedules() {
        const studentId = document.getElementById("studentId").value;
        const tutorId = document.getElementById("tutorId").value;
        const subjectIds = Array.from(selectedSubjects);
        
        if (!studentId || !tutorId || subjectIds.length === 0) {
            return { hasConflict: false };
        }
    
        try {
            const response = await fetch('/check-schedule-conflicts/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({
                    student_id: studentId,
                    tutor_id: tutorId,
                    subject_ids: subjectIds
                })
            });
    
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
    
            return await response.json();
        } catch (error) {
            console.error('Error checking schedule conflicts:', error);
            return { hasConflict: false, error: error.message };
        }
    }
  
    buttons.forEach(btn => container.appendChild(btn));


    let selectedDays = {};
    let tutorAvailability = {};
    let selectedSubjects = new Set();
    

    const warningDiv = document.createElement("div");
    warningDiv.id = "scheduleConflictWarning";
    warningDiv.style.display = "none";
    warningDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> <span id="warningText"></span>';
    document.getElementById("scheduleForm").insertBefore(warningDiv, saveButton);


    function initializeDateInputs() {
        const today = new Date().toISOString().split("T")[0];
        startDateInput.setAttribute("min", today);
        endDateInput.setAttribute("min", today);
        endDateInput.disabled = true;
    }

    function loadTutorAvailability() {
        const tutorIdElement = document.getElementById("tutorId");
        if (!tutorIdElement) return;

        const tutorId = tutorIdElement.value;

        fetch(`/get-tutor-availability/${tutorId}/`)
            .then((response) => response.json())
            .then((data) => {
                tutorAvailability = data.availability || {};
                console.log("Tutor Availability:", tutorAvailability);
            })
            .catch((error) => {
                console.error("Error loading availability:", error);
            });
    }

  
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find((row) => row.startsWith("csrftoken="))
            ?.split("=")[1];
        return cookieValue;
    }


    function calculateEndDate() {
        if (!startDateInput.value || Object.keys(selectedDays).length === 0) {
            endDateInput.value = '';
            totalHoursDisplay.textContent = '';
            return;
        }

        const startDate = new Date(startDateInput.value);
        let weeklyHours = 0;

        Object.values(selectedDays).forEach(day => {
            if (day.subjects && day.subjects.size > 0) {
                weeklyHours += (day.selectedHours || 1) * day.subjects.size;
            }
        });

        if (weeklyHours === 0) {
            endDateInput.value = '';
            return;
        }

        const weeksNeeded = Math.ceil(100 / weeklyHours);
        const endDate = new Date(startDate);
        endDate.setDate(endDate.getDate() + (weeksNeeded * 7));
        endDateInput.value = endDate.toISOString().split('T')[0];
        
        updateTotalHoursDisplay();
    }

    function updateTotalHoursDisplay() {
        if (!startDateInput.value || !endDateInput.value || Object.keys(selectedDays).length === 0) {
            totalHoursDisplay.textContent = '';
            return;
        }

        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        let totalHours = 0;
        const dayInMs = 24 * 60 * 60 * 1000;

        Object.keys(selectedDays).forEach(dayName => {
            const dayData = selectedDays[dayName];
            let dayCount = 0;

            for (let date = new Date(startDate); date <= endDate; date.setTime(date.getTime() + dayInMs)) {
                if (date.toLocaleDateString("en-US", { weekday: "long" }) === dayName) {
                    dayCount++;
                }
            }

            if (dayData.subjects && dayData.subjects.size > 0) {
                totalHours += (dayData.selectedHours || 1) * dayData.subjects.size * dayCount;
            }
        });

        totalHoursDisplay.textContent = `Total Scheduled Hours: ${totalHours}`;
        totalHoursDisplay.dataset.totalHours = totalHours;
    }


    function updateHiddenInput() {
        const formattedDays = {};
        Object.keys(selectedDays).forEach((day) => {
            formattedDays[day] = {
                selectedHours: selectedDays[day].selectedHours || 1,
                subjects: Array.from(selectedDays[day].subjects || []),
            };
        });
        selectedDaysInput.value = JSON.stringify(formattedDays);
        calculateEndDate();
    }

    function addDaySelectionRow(day) {
        const existingRow = document.querySelector(`.day-container[data-day="${day}"]`);
        if (existingRow) existingRow.remove();
    
        const dayContainer = document.createElement("div");
        dayContainer.classList.add("day-container");
        dayContainer.dataset.day = day;
    
        const dayLabel = document.createElement("label");
        dayLabel.classList.add("label-day");
        dayLabel.textContent = day;
        dayContainer.appendChild(dayLabel);
    
        const subjectSelectDiv = document.createElement("div");
        subjectSelectDiv.classList.add("day-subject-selection");
    
        const subjectSelectLabel = document.createElement("label");
        subjectSelectLabel.textContent = "Select Subjects:";
        subjectSelectDiv.appendChild(subjectSelectLabel);
    
        const subjectCheckboxesDiv = document.createElement("div");
        subjectCheckboxesDiv.classList.add("subject-checkboxes-grid");
    
        selectedSubjects.forEach((subjectId) => {
            const subjectBtn = document.querySelector(`.subject-btn[data-subject-id="${subjectId}"]`);
            if (subjectBtn) {
                const subjectName = subjectBtn.textContent.replace(/\([^)]*\)/g, "").trim();
    
                const checkboxContainer = document.createElement("div");
                checkboxContainer.classList.add("subject-checkbox-container");
    
                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.id = `subject-${subjectId}-${day}`;
                checkbox.value = subjectId;
                checkbox.checked = true;
                checkbox.classList.add("subject-checkbox");
    
                selectedDays[day].subjects.add(subjectId);
    
                checkbox.addEventListener("change", function () {
                    if (this.checked) {
                        selectedDays[day].subjects.add(subjectId);
                    } else {
                        selectedDays[day].subjects.delete(subjectId);
                    }
                    updateHiddenInput();
                });
    
                const label = document.createElement("label");
                label.htmlFor = `subject-${subjectId}-${day}`;
                label.textContent = subjectName;
                label.classList.add("subject-label");
    
                checkboxContainer.appendChild(checkbox);
                checkboxContainer.appendChild(label);
                subjectCheckboxesDiv.appendChild(checkboxContainer);
            }
        });
    
        subjectSelectDiv.appendChild(subjectCheckboxesDiv);
        dayContainer.appendChild(subjectSelectDiv);
    
        const durationDiv = document.createElement("div");
        durationDiv.classList.add("duration-selection");
    
        const durationLabel = document.createElement("label");
        durationLabel.textContent = "Select Duration:";
        durationDiv.appendChild(durationLabel);
    
        const durationContainer = document.createElement("div");
        durationContainer.classList.add("duration-options");
        durationDiv.appendChild(durationContainer);
    
        const availableHours = tutorAvailability[day]?.total_hours || 0;
        const maxAvailableHours = Math.min(3, Math.floor(availableHours));
    
        for (let hours = 1; hours <= maxAvailableHours; hours++) {
            const button = document.createElement("button");
            button.type = "button";
            button.classList.add("duration-btn");
            if (hours === selectedDays[day].selectedHours) {
                button.classList.add("active");
            }
            button.dataset.hours = hours;
            button.textContent = `${hours} Hour${hours > 1 ? "s" : ""}`;
    
            button.addEventListener("click", function () {
                durationContainer.querySelectorAll(".duration-btn").forEach((btn) => {
                    btn.classList.remove("active");
                });
    
                this.classList.add("active");
                selectedDays[day].selectedHours = hours;
                updateHiddenInput();
            });
    
            durationContainer.appendChild(button);
        }
    
        if (maxAvailableHours === 0) {
            const noAvailability = document.createElement("p");
            noAvailability.textContent = "No available hours for this day";
            noAvailability.classList.add("no-availability");
            durationContainer.appendChild(noAvailability);
        }
    
        dayContainer.appendChild(durationDiv);
        tutoringDaysContainer.appendChild(dayContainer);
    
        updateHiddenInput();
    }

    function removeDaySelectionRow(day) {
        const dayContainer = document.querySelector(`.day-container[data-day="${day}"]`);
        if (dayContainer) dayContainer.remove();
        delete selectedDays[day];
        updateHiddenInput();
    }

    function updateDaySubjectSelections() {
        document.querySelectorAll(".day-container").forEach((dayContainer) => {
            const day = dayContainer.dataset.day;
            const subjectCheckboxesDiv = dayContainer.querySelector(".subject-checkboxes-grid");

            if (subjectCheckboxesDiv) {
                subjectCheckboxesDiv.innerHTML = "";

                selectedSubjects.forEach((subjectId) => {
                    const subjectBtn = document.querySelector(`.subject-btn[data-subject-id="${subjectId}"]`);
                    if (subjectBtn) {
                        const subjectName = subjectBtn.textContent.replace(/\([^)]*\)/g, "").trim();

                        const checkboxContainer = document.createElement("div");
                        checkboxContainer.classList.add("subject-checkbox-container");

                        const checkbox = document.createElement("input");
                        checkbox.type = "checkbox";
                        checkbox.id = `subject-${subjectId}-${day}`;
                        checkbox.value = subjectId;
                        checkbox.checked = selectedDays[day]?.subjects.has(subjectId) || false;
                        checkbox.classList.add("subject-checkbox");

                        checkbox.addEventListener("change", function () {
                            if (this.checked) {
                                selectedDays[day].subjects.add(subjectId);
                            } else {
                                selectedDays[day].subjects.delete(subjectId);
                            }
                            updateHiddenInput();
                        });

                        const label = document.createElement("label");
                        label.htmlFor = `subject-${subjectId}-${day}`;
                        label.textContent = subjectName;
                        label.classList.add("subject-label");

                        checkboxContainer.appendChild(checkbox);
                        checkboxContainer.appendChild(label);
                        subjectCheckboxesDiv.appendChild(checkboxContainer);
                    }
                });
            }
        });
    }

    function updateTopicButtons() {
        document.querySelectorAll(".topic-btn").forEach((topicBtn) => {
            const subjectId = topicBtn.dataset.subjectId;
            topicBtn.style.display = selectedSubjects.has(subjectId) ? "none" : "none";
            if (!selectedSubjects.has(subjectId)) {
                topicBtn.classList.remove("selected");
            }
        });
        topicContainer.style.display = selectedSubjects.size > 0 ? "none" : "none";
    }


    function handleSubjectClick(event) {
        if (event.target.classList.contains("subject-btn")) {
            if (event.target.classList.contains('has-conflict')) {
                return;
            }
    
            const subjectId = event.target.dataset.subjectId;
            const subjectName = event.target.textContent.replace(/\([^)]*\)/g, "").trim();
    
            if (selectedSubjects.has(subjectId)) {
                event.target.classList.remove("selected");
                selectedSubjects.delete(subjectId);
            } else {
                event.target.classList.add("selected");
                selectedSubjects.add(subjectId);
            }
    
            selectedSubjectInput.value = Array.from(selectedSubjects).join(",");
            updateTopicButtons();
            updateDaySubjectSelections();
            updateHiddenInput();
        }
    }

    function handleTopicClick(event) {
        if (event.target.classList.contains("topic-btn")) {
            event.target.classList.toggle("selected");
            const selectedTopics = Array.from(document.querySelectorAll(".topic-btn.selected"))
                .map((btn) => btn.dataset.topicId)
                .filter((id) => id);
            selectedTopicInput.value = selectedTopics.join(",");
        }
    }

    function handleDayButtonClick(event) {
        if (event.target.classList.contains("repeat-day-btn")) {
            const day = event.target.dataset.day;

            if (!selectedDays[day]) {
                selectedDays[day] = {
                    selectedHours: 1,
                    subjects: new Set(),
                };
                event.target.classList.add("selected");
                addDaySelectionRow(day);
            } else {
                delete selectedDays[day];
                event.target.classList.remove("selected");
                removeDaySelectionRow(day);
            }
            updateHiddenInput();
        }
    }

    async function handleFormSubmit(event) {
        event.preventDefault();
    
        // Existing validation checks
        const subjectId = document.getElementById("selectedSubject").value.split(",")[0];
        if (!subjectId) {
            alert("Please select a subject");
            return;
        }
        
        if (!startDateInput.value) {
            alert("Please select a start date");
            return;
        }
    
        if (!endDateInput.value) {
            alert("Please ensure an end date is calculated");
            return;
        }
    
        const repeatDays = JSON.parse(selectedDaysInput.value || "{}");
        if (Object.keys(repeatDays).length === 0) {
            alert("Please select at least one day");
            return;
        }
        
        for (const day in repeatDays) {
            if (!repeatDays[day].subjects || repeatDays[day].subjects.length === 0) {
                alert(`Please select at least one subject for ${day}`);
                return;
            }
            if (!repeatDays[day].selectedHours || repeatDays[day].selectedHours < 1) {
                alert(`Please select duration for ${day}`);
                return;
            }
        }
    
        // New conflict check
        const conflictCheck = await checkForExistingSchedules();
        if (conflictCheck.hasConflict) {
            const warningDiv = document.getElementById("scheduleConflictWarning");
            const warningText = document.getElementById("warningText");
            
            warningDiv.style.display = "flex";
            warningText.textContent = conflictCheck.message || 
                "This student already has sessions with this tutor for the selected subject(s).";
            
            // Highlight conflicting subjects
            if (conflictCheck.conflicting_subjects) {
                conflictCheck.conflicting_subjects.forEach(subjectId => {
                    const subjectBtn = document.querySelector(`.subject-btn[data-subject-id="${subjectId}"]`);
                    if (subjectBtn) {
                        subjectBtn.classList.add('has-conflict');
                        subjectBtn.title = "Conflict - student already has this subject with this tutor";
                    }
                });
            }
            
            return; // Don't proceed with submission
        }
    
        // Rest of your existing submission code...
        const formData = new FormData(event.target);
        const requestData = {
            tutor_id: formData.get("tutor_id"),
            parent_id: formData.get("parent_id"),
            student_id: formData.get("student_id"),
            start_date: startDateInput.value,
            end_date: endDateInput.value,    
            repeat_days: repeatDays,
            create_sessions: true,
        };
    
        console.log("Submitting schedule data:", requestData);
    
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = "Creating Schedule...";
    
        try {
            const response = await fetch("/create_schedule/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify(requestData),
            });
            
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error || "Failed to create schedule and sessions");
            }
            
            console.log("Schedule created successfully:", data);
            document.getElementById("scheduleModal").style.display = "none";
            document.getElementById("successfully-modal").style.display = "flex";
            document.body.classList.remove("modal-open");
        } catch (error) {
            console.error("Error:", error);
            alert("Error: " + error.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalBtnText;
        }
    }

    initializeDateInputs();
    loadTutorAvailability();


    startDateInput.addEventListener("change", function() {
        endDateInput.setAttribute("min", startDateInput.value);
        calculateEndDate();
    });

    if (openModal) {
        openModal.addEventListener("click", function () {
            modal.style.display = "flex";
            document.body.classList.add("modal-open");
        });
    }

    if (closeModal) {
        closeModal.addEventListener("click", function () {
            modal.style.display = "none";
            document.body.classList.remove("modal-open");
        });
    }

    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
            document.body.classList.remove("modal-open");
        }
    });

    document.addEventListener("click", handleSubjectClick);
    document.addEventListener("click", handleTopicClick);
    document.addEventListener("click", handleDayButtonClick);
    document.getElementById("scheduleForm").addEventListener("submit", handleFormSubmit);
});


document.addEventListener("DOMContentLoaded", function () {
    const progressBars = document.querySelectorAll(".fill");
    progressBars.forEach((bar) => {
        const progress = bar.getAttribute("data-progress");
        if (progress) bar.style.width = progress + "%";
    });
});

function toggleAvailability() {
    const extraAvailability = document.getElementById("extra-availability");
    const btn = document.querySelector(".view-more-btn");

    if (extraAvailability.style.display === "none") {
        extraAvailability.style.display = "block";
        btn.textContent = "Less";
    } else {
        extraAvailability.style.display = "none";
        btn.textContent = " More";
    }
}