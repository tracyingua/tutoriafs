$(document).ready(function () {
    console.log("JavaScript Loaded!");

    // Initialize Select2 with "Select All" option
    $(".multi-select").select2({
        width: "100%",
        closeOnSelect: false
    });

    // Add "Select All" option to topics and subtopics
    function addSelectAllOption(selector) {
        $(selector).on('select2:open', function() {
            let select = $(this);
            if (select.find('option[value="all"]').length === 0) {
                select.prepend('<option value="all">Select All</option>');
                select.trigger('change');
            }
        });

        $(selector).on('change', function() {
            if ($(this).val() && $(this).val().includes("all")) {
                // Select all options except "Select All"
                let allOptions = $(this).find('option').not('[value="all"]').map(function() {
                    return $(this).val();
                }).get();
                $(this).val(allOptions).trigger('change');
            }
        });
    }

    addSelectAllOption("#topics");
    addSelectAllOption("#subtopics");

    $("#edit-profile-modal, #successfully-modal").hide();

    let removedCredentials = [];
    let selectedFiles = [];
    let isSubmitting = false;

    function openModal() {
        console.log("Opening modal...");
        $("#edit-profile-modal").show();

        setSelectedValues("#subjects");
        setSelectedValues("#topics");
        setSelectedValues("#subtopics");
        setSelectedValues("#grade_levels");

        updateTopicsAndSubtopics($("#subjects").val());
    }

    function closeModal() {
        console.log("Closing modal...");
        $("#edit-profile-modal").hide();
    }

    function showSuccessModal() {
        console.log("Showing success modal...");
        $("#successfully-modal").show();
    }

    function closelyModal() {
        console.log("Closing success modal...");
        $("#successfully-modal").hide();
        location.reload();
    }

    window.openModal = openModal;
    window.closeModal = closeModal;
    window.closelyModal = closelyModal;

    $(document).on("click", "#editButton", openModal);
    $(".close").on("click", closeModal);
    $(".mew-close-modal").on("click", closelyModal);

    $(window).on("click", function (event) {
        if ($(event.target).hasClass("modal")) {
            closeModal();
        }
    });

    function setSelectedValues(selectElement) {
        let selectedValues = $(selectElement).attr("data-selected");
        try {
            selectedValues = JSON.parse(selectedValues);
            if (Array.isArray(selectedValues)) {
                console.log(`Setting selected values for ${selectElement}:`, selectedValues);
                $(selectElement).val(selectedValues).trigger("change");
            }
        } catch (error) {
            console.error(`Error parsing selected values for ${selectElement}:`, error);
        }
    }

    $("#subjects").on("change", function () {
        let selected = $(this).val();
        updateTopicsAndSubtopics(selected);
    });

    function updateTopicsAndSubtopics(selectedSubjects) {
        if (!selectedSubjects || selectedSubjects.length === 0) {
            console.log("No subjects selected.");
            updateDropdown("#topics", []);
            updateDropdown("#subtopics", []);
            updateDropdown("#grade_levels", []); 
            return;
        }
    
        $.ajax({
            url: getTopicsUrl,
            type: "GET",
            data: { subjects: selectedSubjects },
            success: function (response) {
                console.log("Received response:", response);
                updateDropdown("#topics", response.topics);
                updateDropdown("#subtopics", response.subtopics);
                updateDropdown("#grade_levels", response.grade_levels); 
    
                setSelectedValues("#topics");
                setSelectedValues("#subtopics");
                setSelectedValues("#grade_levels");
            },
            error: function (xhr, status, error) {
                console.error("Error fetching topics:", error);
            }
        });
    }

    function updateDropdown(selector, items) {
        let dropdown = $(selector);
        dropdown.empty();

        if (items.length === 0) {
            dropdown.append(new Option("No options available", "", false, false));
        } else {
            // Add "Select All" option for topics and subtopics
            if (selector === "#topics" || selector === "#subtopics") {
                dropdown.append(new Option("Select All", "all", false, false));
            }
            
            items.forEach(item => {
                dropdown.append(new Option(item.name, item.id, false, false));
            });
        }

        dropdown.trigger("change");
    }

    $("#edit-profile-form").on("submit", function (event) {
        event.preventDefault();

        if (isSubmitting) {
            console.log("Form submission already in progress");
            return;
        }

        isSubmitting = true;
        const submitButton = $("#submit-button");
        submitButton.prop("disabled", true);
        submitButton.find(".button-text").text("Saving...");
        submitButton.find(".loading-spinner").show();

        $("#removed-credentials").val(JSON.stringify(removedCredentials)); 

        let formData = new FormData(this);

        // Remove "all" value if present in topics or subtopics
        let topics = $("#topics").val();
        if (topics && topics.includes("all")) {
            topics = topics.filter(val => val !== "all");
            formData.set("topics[]", topics);
        }

        let subtopics = $("#subtopics").val();
        if (subtopics && subtopics.includes("all")) {
            subtopics = subtopics.filter(val => val !== "all");
            formData.set("subtopics[]", subtopics);
        }

        let fileInput = document.getElementById("file-input");
        if (fileInput.files.length > 0) {
            for (let i = 0; i < fileInput.files.length; i++) {
                formData.append("credentials", fileInput.files[i]);
            }
        }

        console.log("Submitting form with data:", formData);

        $.ajax({
            url: editProfileUrl,
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                "X-CSRFToken": getCSRFToken()
            },
            success: function (response) {
                console.log("Profile updated successfully!", response);
                closeModal();
                showSuccessModal();
            },
            error: function (xhr, status, error) {
                console.error("Error updating profile:", error);
                isSubmitting = false;
                submitButton.prop("disabled", false);
                submitButton.find(".button-text").text("Save Changes");
                submitButton.find(".loading-spinner").hide();
                alert("An error occurred. Please try again.");
            }
        });
    });

    function getCSRFToken() {
        let cookieValue = null,
            name = "csrftoken";
        if (document.cookie && document.cookie !== "") {
            let cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    $(".remove-credential").click(function () {
        let credentialId = $(this).data("id");
        if (!removedCredentials.includes(credentialId)) {
            removedCredentials.push(credentialId);
        }
        $(this).closest("li").hide();
        console.log("Marked for removal:", removedCredentials);
        $("#removed-credentials").val(JSON.stringify(removedCredentials));
    });

    let fileInput = document.getElementById("file-input");
    let filePreview = document.getElementById("file-preview");

    document.getElementById("add-files").addEventListener("click", function () {
        fileInput.click();
    });

    fileInput.addEventListener("change", function (event) {
        let newFiles = Array.from(event.target.files);
        newFiles.forEach(file => {
            if (!selectedFiles.some(f => f.name === file.name)) {
                selectedFiles.push(file);
            }
        });
        updatePreview();
    });

    function updatePreview() {
        filePreview.innerHTML = "";
        selectedFiles.forEach((file, index) => {
            let fileItem = document.createElement("div");
            fileItem.classList.add("file-item");
            fileItem.innerHTML = `
                <span>${file.name}</span>
                <button type="button" class="remove-file" data-index="${index}">✖</button>
            `;
            filePreview.appendChild(fileItem);
        });

        document.querySelectorAll(".remove-file").forEach(button => {
            button.addEventListener("click", function () {
                let index = parseInt(this.getAttribute("data-index"));
                selectedFiles.splice(index, 1);
                updatePreview();
            });
        });

        let newFileList = new DataTransfer();
        selectedFiles.forEach(file => newFileList.items.add(file));
        fileInput.files = newFileList.files;
    }
});

function toggleCredentials() {
    let hiddenItems = document.querySelectorAll(".credential-item.hidden");
    let allItems = document.querySelectorAll(".credential-item");
    let button = document.getElementById("show-more-btn");

    if (button.innerText === "Show More") {
        hiddenItems.forEach(item => item.classList.remove("hidden"));
        button.innerText = "Show Less";
    } else {
        allItems.forEach((item, index) => {
            if (index >= 3) item.classList.add("hidden");
        });
        button.innerText = "Show More";
    }
}