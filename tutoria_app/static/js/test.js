document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("scheduleModal");
    const openModal = document.querySelector(".schedule-btn");
    const closeModal = document.getElementById("closeModal");

    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");

    const topicContainer = document.querySelector(".topic-container");
    const selectedSubjectInput = document.getElementById("selectedSubject");
    const selectedTopicInput = document.getElementById("selectedTopic");
    const selectedDaysInput = document.getElementById("selectedDays");

    const tutoringDaysContainer = document.getElementById("selectedDaysContainer");

    let selectedDays = {};
    let tutorAvailability = {};
    let selectedSubjects = new Set();

    let today = new Date().toISOString().split("T")[0];
    startDateInput.setAttribute("min", today);
    endDateInput.setAttribute("min", today);

    startDateInput.addEventListener("change", function () {
        endDateInput.setAttribute("min", startDateInput.value);
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

    // [Previous validation functions remain the same...]

    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
            document.body.classList.remove("modal-open");
        }
    });
    
    function loadTutorAvailability() {
        const tutorIdElement = document.getElementById("tutorId");
        if (!tutorIdElement) {
            console.error("Tutor ID is missing. Skipping tutor availability loading.");
            return;
        }
        const tutorId = tutorIdElement.value;

        fetch(`/get-tutor-availability/${tutorId}/`)
            .then(response => response.json())
            .then(data => {
                tutorAvailability = data.availability || {};
                console.log("Tutor Availability Data:", tutorAvailability);
            })
            .catch(error => console.error("Error fetching availability:", error));
    }

    loadTutorAvailability();

    document.addEventListener("click", function (event) {
        if (event.target.classList.contains("subject-btn")) {
            const subjectId = event.target.dataset.subjectId;

            if (event.target.classList.contains("selected")) {
                event.target.classList.remove("selected");
                selectedSubjects.delete(subjectId);
            } else {
                event.target.classList.add("selected");
                selectedSubjects.add(subjectId);
            }

            selectedSubjectInput.value = Array.from(selectedSubjects).join(",");
            console.log("Selected Subjects:", selectedSubjects);

            updateTopicButtons();
            updateDaySubjectDropdowns();
        }
    });

    function updateTopicButtons() {
        document.querySelectorAll(".topic-btn").forEach(topicBtn => {
            if (selectedSubjects.has(topicBtn.dataset.subjectId)) {
                topicBtn.style.display = "inline-block";
            } else {
                topicBtn.style.display = "none";
                topicBtn.classList.remove("selected");
            }
        });

        topicContainer.style.display = selectedSubjects.size ? "block" : "none";
    }

    document.addEventListener("click", function (event) {
        if (event.target.classList.contains("topic-btn")) {
            const topicId = event.target.dataset.topicId;

            event.target.classList.toggle("selected");

            let selectedTopics = Array.from(document.querySelectorAll(".topic-btn.selected"))
                .map(btn => parseInt(btn.dataset.topicId))
                .filter(id => !isNaN(id));

            selectedTopicInput.value = selectedTopics.join(",");
        }
    });

    document.addEventListener("click", function (event) {
        if (event.target.classList.contains("repeat-day-btn")) {
            const day = event.target.dataset.day;
            const hoursAvailable = parseInt(event.target.dataset.hoursAvailable) || 0;
    
            if (!selectedDays[day]) {
                selectedDays[day] = {
                    hoursAvailable: hoursAvailable,
                    subjects: {}
                };
                event.target.classList.add("selected");
                addDaySelectionRow(day, hoursAvailable);
                document.getElementById("timeSelection").style.display = "block";
            } else {
                delete selectedDays[day];
                event.target.classList.remove("selected");
                removeDaySelectionRow(day);
    
                if (Object.keys(selectedDays).length === 0) {
                    document.getElementById("timeSelection").style.display = "none";
                }
            }
    
            updateHiddenInput();
        }
    });

    function addDaySelectionRow(day, hoursAvailable) {
        console.log(`Adding row for day: ${day} with ${hoursAvailable} hours available`);
    
        const existingRow = document.querySelector(`.day-container[data-day="${day}"]`);
        if (existingRow) {
            existingRow.remove();
        }
    
        let dayContainer = document.createElement("div");
        dayContainer.classList.add("day-container");
        dayContainer.dataset.day = day;
    
        let dayLabel = document.createElement("label");
        dayLabel.classList.add("label-day");
        dayLabel.textContent = `${day} (${hoursAvailable} hour${hoursAvailable !== 1 ? 's' : ''} available)`;
        dayContainer.appendChild(dayLabel);
    
        const hasAvailability = tutorAvailability[day] && tutorAvailability[day].length > 0;
        const availableSlotsCount = hasAvailability ? tutorAvailability[day].length : 0;
        
        const shouldShowMultiSubject = hasAvailability && 
                                     (selectedSubjects.size > 1 || availableSlotsCount > 1);
    
        let subjectGroupsContainer = document.createElement("div");
        subjectGroupsContainer.classList.add("subject-groups-container");
        dayContainer.appendChild(subjectGroupsContainer);
    
        addSubjectTimeGroup(day, hoursAvailable, subjectGroupsContainer, shouldShowMultiSubject);
    
        if (shouldShowMultiSubject) {
            let addSubjectBtn = document.createElement("button");
            addSubjectBtn.type = "button";
            addSubjectBtn.classList.add("add-subject-btn");
            addSubjectBtn.textContent = "+ Add Another Subject";
            addSubjectBtn.addEventListener("click", () => {
                const currentGroups = subjectGroupsContainer.querySelectorAll('.subject-time-group');
                const maxGroups = Math.max(selectedSubjects.size, availableSlotsCount);
                if (currentGroups.length >= maxGroups) {
                    alert(`You can add up to ${maxGroups} subject groups for this day`);
                    return;
                }
                addSubjectTimeGroup(day, hoursAvailable, subjectGroupsContainer, shouldShowMultiSubject);
            });
            dayContainer.appendChild(addSubjectBtn);
        }
    
        tutoringDaysContainer.appendChild(dayContainer);
    }

    function addSubjectTimeGroup(day, hoursAvailable, container, showRemoveButton = true) {
        let groupDiv = document.createElement("div");
        groupDiv.classList.add("subject-time-group");
    
        // Create subject dropdown container
        let subjectSelectContainer = document.createElement("div");
        subjectSelectContainer.classList.add("subject-select-container");
    
        // Create subject dropdown
        let subjectSelect = document.createElement("select");
        subjectSelect.classList.add("day-subject-select");
        subjectSelect.dataset.day = day;
        
        // Initialize with default option
        let defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "Select Subject";
        subjectSelect.appendChild(defaultOption);
    
        // Add subject options
        Array.from(selectedSubjects).forEach(subjectId => {
            const subjectBtn = document.querySelector(`.subject-btn[data-subject-id="${subjectId}"]`);
            if (subjectBtn) {
                let option = document.createElement("option");
                option.value = subjectId;
                option.textContent = subjectBtn.textContent.replace(/\([^)]*\)/g, '').trim();
                subjectSelect.appendChild(option);
            }
        });
    
        subjectSelectContainer.appendChild(subjectSelect);
    
        // Add remove button if needed
        if (showRemoveButton) {
            let removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.classList.add("remove-subject-btn");
            removeBtn.textContent = "×";
            removeBtn.addEventListener("click", () => {
                groupDiv.remove();
                updateHiddenInput();
            });
            subjectSelectContainer.appendChild(removeBtn);
        }
    
        groupDiv.appendChild(subjectSelectContainer);
    
        // Create hour selection container
        let hourSelectionContainer = document.createElement("div");
        hourSelectionContainer.classList.add("hour-selection-container");
        
        // Create hour selection label
        let hourLabel = document.createElement("label");
        hourLabel.textContent = "Select Duration:";
        hourSelectionContainer.appendChild(hourLabel);
        
        // Create hour buttons container
        let hourButtonsContainer = document.createElement("div");
        hourButtonsContainer.classList.add("hour-buttons-container");
        
        // Create hour buttons (1h, 2h, 3h) based on available hours
        const maxHours = Math.min(3, hoursAvailable);
        for (let i = 1; i <= maxHours; i++) {
            let hourButton = document.createElement("button");
            hourButton.type = "button";
            hourButton.classList.add("hour-btn");
            hourButton.textContent = `${i}h`;
            hourButton.dataset.hours = i;
            
            hourButton.addEventListener("click", function() {
                // Remove active class from all buttons in this container
                hourButtonsContainer.querySelectorAll('.hour-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Get the selected subject
                const subjectId = subjectSelect.value;
                if (!subjectId) {
                    alert("Please select a subject first");
                    this.classList.remove('active');
                    return;
                }
                
                // Update the selected hours for this subject
                if (!selectedDays[day].subjects[subjectId]) {
                    selectedDays[day].subjects[subjectId] = {
                        hours: 0
                    };
                }
                
                selectedDays[day].subjects[subjectId].hours = i;
                updateHiddenInput();
            });
            
            hourButtonsContainer.appendChild(hourButton);
        }
        
        hourSelectionContainer.appendChild(hourButtonsContainer);
        groupDiv.appendChild(hourSelectionContainer);
    
        // Handle subject selection change
        subjectSelect.addEventListener("change", function() {
            const subjectId = this.value;
            
            // Clear any selected hours for this subject group
            hourButtonsContainer.querySelectorAll('.hour-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            if (subjectId && selectedDays[day] && selectedDays[day].subjects[subjectId]) {
                delete selectedDays[day].subjects[subjectId];
                updateHiddenInput();
            }
        });
    
        container.appendChild(groupDiv);
    }

    function removeDaySelectionRow(day) {
        console.log(`Removing row for day: ${day}`);
        
        const dayContainer = document.querySelector(`.day-container[data-day="${day}"]`);
        if (dayContainer) {
            dayContainer.remove();
        }
        
        delete selectedDays[day];
        updateHiddenInput();
        
        if (Object.keys(selectedDays).length === 0) {
            document.getElementById("timeSelection").style.display = "none";
        }
    }
    
    function updateHiddenInput() {
        let formattedDays = {};
        
        Object.keys(selectedDays).forEach(day => {
            formattedDays[day] = [];
            
            if (selectedDays[day].subjects) {
                Object.keys(selectedDays[day].subjects).forEach(subjectId => {
                    const subjectData = selectedDays[day].subjects[subjectId];
                    if (subjectData && subjectData.hours > 0) {
                        formattedDays[day].push({
                            subject: subjectId,
                            hours: subjectData.hours
                        });
                    }
                });
            }
        });
        
        selectedDaysInput.value = JSON.stringify(formattedDays);
        console.log("Updated selection:", formattedDays);
    }

    // [Rest of the code remains the same...]
});