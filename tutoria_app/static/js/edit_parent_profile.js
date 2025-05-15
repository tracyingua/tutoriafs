document.addEventListener("DOMContentLoaded", function () {
  
    function previewImage(event) {
      var reader = new FileReader();
      reader.onload = function () {
        var output = document.getElementById("profile-preview");
        if (output) {
          output.src = reader.result;
        }
      };
      if (event.target.files.length > 0) {
        reader.readAsDataURL(event.target.files[0]);
      }
    }
  
    function goBack() {
      window.location.href = goBackUrl;
    }
  

    window.previewImage = previewImage;
    window.goBack = goBack;
  });
  
  document.addEventListener("DOMContentLoaded", function () {
 
    const successModal = document.getElementById("success-modal");
  
    if (successModal && successModal.dataset.show === "true") {
      successModal.style.display = "flex"; 
    }
  });
  

  function closeModal() {
    document.getElementById("success-modal").style.display = "none";
  }
  


  function closelyModal() {
    document.getElementById("successfully-modal").style.display = "none";

    let scheduleForm = document.getElementById("scheduleForm");
    if (scheduleForm) {
        scheduleForm.reset();  
    }

    document.querySelectorAll(".subject-btn, .topic-btn, .repeat-day-btn").forEach(btn => {
        btn.classList.remove("selected");
    });

   
    document.querySelector(".topic-container").style.display = "none";
    document.getElementById("timeSelection").style.display = "none";

    document.getElementById("selectedDaysContainer").innerHTML = "";


    document.getElementById("selectedSubject").value = "";
    document.getElementById("selectedTopic").value = "";
    document.getElementById("selectedDays").value = "{}";

    selectedDays = {};
}
