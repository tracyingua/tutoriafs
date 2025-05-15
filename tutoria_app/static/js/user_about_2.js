let uploadInterval;
let selectedFiles = [];

document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("fileUpload");
    if (fileInput) {
        fileInput.addEventListener("change", handleFileSelection);
    }

    const profileInput = document.getElementById("profileUpload");
    if (profileInput) {
        profileInput.addEventListener("change", displayImage);
    }
});


function handleFileSelection(event) {
    const fileList = Array.from(event.target.files);
    const filePreviewContainer = document.getElementById("filePreviewContainer");


    fileList.forEach((file) => {
        if (!selectedFiles.some(f => f.name === file.name)) {
            selectedFiles.push(file);
        }
    });

    updateFileListDisplay();
    updateFileInput(); 
}


function removeFile(fileName) {
    selectedFiles = selectedFiles.filter(file => file.name !== fileName);
    updateFileListDisplay();
    updateFileInput(); 
}


function updateFileInput() {
    const fileInput = document.getElementById("fileUpload");

    const dataTransfer = new DataTransfer(); 
    selectedFiles.forEach(file => dataTransfer.items.add(file));

    fileInput.files = dataTransfer.files; 
}

function updateFileListDisplay() {
    const filePreviewContainer = document.getElementById("filePreviewContainer");
    filePreviewContainer.innerHTML = "";

    selectedFiles.forEach((file) => {
        const fileItem = document.createElement("div");
        fileItem.className = "file-preview-item";
        fileItem.innerHTML = `
            <span class="file-name">${file.name}</span>
            <button class="remove-file" onclick="removeFile('${file.name}')">✖</button>
        `;
        filePreviewContainer.appendChild(fileItem);
    });

    if (selectedFiles.length === 0) {
        document.getElementById("fileUpload").value = "";
    }
}

function displayImage(event) {
    const uploadBox = document.querySelector(".upload-placeholder");
    const file = event.target.files[0];

    if (file) {
        const validExtensions = ["image/jpeg", "image/jpg", "image/png"];
        const fileExtension = file.name.split(".").pop().toLowerCase();

        if (!validExtensions.includes(file.type) || !["jpg", "jpeg", "png"].includes(fileExtension)) {
            alert("Invalid file type. Please upload a JPEG or PNG image.");
            event.target.value = "";
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            alert("File size exceeds 5MB limit.");
            event.target.value = ""; 
            return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            uploadBox.innerHTML = `<img src="${e.target.result}" style="width: 100%; height: 100%; border-radius: 8px; background-color: #fff;">`;
        };
        reader.readAsDataURL(file);
    }
}


function handleBrowseClick(event) {
    event.preventDefault();
    document.getElementById("fileUpload").click();
}
