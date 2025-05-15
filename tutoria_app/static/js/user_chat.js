document.addEventListener("DOMContentLoaded", function () {
  const messageInput = document.getElementById("messageInput");
  const sendBtn = document.getElementById("sendBtn");
  const chatMessages = document.querySelector(".chat-messages");
  const photoBtn = document.getElementById("photoBtn");
  const popupModal = document.getElementById("popupModal");
  const cameraOption = document.getElementById("cameraOption");
  const galleryOption = document.getElementById("galleryOption");
  const fileInput = document.getElementById("fileInput");
  const uploadInput = document.getElementById("uploadInput");
  const imageModal = document.getElementById("imageModal");
  const modalImage = document.getElementById("modalImage");
  const closeModal = document.querySelector(".close-modal");

  let currentUser = chatMessages?.dataset.currentUser || null; 
  let lastMessageId = 0; 

 
  if (!currentUser) {
      console.error(" currentUser is NULL! Check your template.");
  }

  // Modal functionality
  function openImageModal(imageSrc) {
    modalImage.src = imageSrc;
    imageModal.style.display = "block";
    document.body.style.overflow = "hidden";
  }

  function closeImageModal() {
    imageModal.style.display = "none";
    document.body.style.overflow = "auto";
  }

  closeModal.addEventListener("click", closeImageModal);
  imageModal.addEventListener("click", function (e) {
    if (e.target === imageModal) {
      closeImageModal();
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && imageModal.style.display === "block") {
      closeImageModal();
    }
  });


  const galleryImages = document.querySelectorAll(".gallery-image");
  galleryImages.forEach(image => {
    image.addEventListener("click", function () {
      openImageModal(this.src);
    });
  });


  function sendMessage(message, messageType = "text") {
      if (!message.trim()) return;

      const conversationId = chatMessages?.dataset.conversationId;
      if (!conversationId) {
          console.error(" No conversation ID found!");
          alert("Invalid conversation ID. Please refresh the page.");
          return;
      }

      if (typeof sendMessageUrl === "undefined") {
          console.error(" sendMessageUrl is not defined!");
          return;
      }

      let formData = new FormData();
      formData.append("message", message);
      formData.append("message_type", messageType);
      formData.append("conversation_id", conversationId);

      fetch(sendMessageUrl, {
          method: "POST",
          body: formData,
          headers: {
              "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
          }
      })
      .then(response => response.json())
      .then(data => {
          if (data.error) {
              alert(data.error);
          } else {
            
              messageInput.value = "";
          }
      })
      .catch(error => console.error(" Error sending message:", error));
  }

  function fetchNewMessages() {
    const conversationId = chatMessages?.dataset.conversationId;
    if (!conversationId) {
        console.error(" No conversation ID found!");
        return;
    }

    fetch(`/get-new-messages/?conversation_id=${conversationId}&last_message_id=${lastMessageId}`)
        .then(response => response.json())
        .then(data => {
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    const messageType = message.sender_id == currentUser ? "sent" : "received";

                  
                    if (!document.getElementById(`message-${message.id}`)) {
                        if (message.type === "text") {
                            appendTextMessageToChat(message.content, messageType, message.sender_avatar, message.id, message.timestamp);
                        } else if (message.type === "image") {
                            appendImageToChat(message.image_url, messageType, message.sender_avatar, message.id, message.timestamp);
                            appendImageToMediaGallery(message.image_url);
                        }
                    }
                });

           
     

 
            }
        })
        .catch(error => console.error(" Error fetching new messages:", error));
}



function appendImageToMediaGallery(imageUrl) {
    const mediaContent = document.getElementById("media-content");
    
 
    let gallery = mediaContent.querySelector(".media-gallery");
    if (!gallery) {
        gallery = document.createElement("div");
        gallery.className = "media-gallery";
        mediaContent.appendChild(gallery);
    }


    const existingImages = gallery.querySelectorAll("img");
    const imageExists = Array.from(existingImages).some(img => img.src.includes(imageUrl));
    
    if (!imageExists) {
        const imgElement = document.createElement("img");
        imgElement.src = imageUrl;
        imgElement.className = "gallery-image";
        imgElement.style.width = "100px";
        imgElement.style.height = "100px";
        imgElement.style.margin = "5px";
        imgElement.style.cursor = "pointer";
        imgElement.style.objectFit = "cover";
        imgElement.style.borderRadius = "5px";
        
        imgElement.addEventListener("click", function() {
            openImageModal(imageUrl);
        });

        gallery.appendChild(imgElement);
    
    }
}

 
  setInterval(fetchNewMessages, 100);

  document.getElementById("chatForm").addEventListener("submit", function (event) {
      event.preventDefault();
  });

  messageInput.addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
          event.preventDefault();
          sendMessage(messageInput.value, "text");
      }
  });

  sendBtn.addEventListener("click", function (event) {
      event.preventDefault();
      sendMessage(messageInput.value, "text");
  });

  photoBtn.addEventListener("click", function () {
      popupModal.style.display = "flex";
  });

  cameraOption.addEventListener("click", function () {
      popupModal.style.display = "none";
      fileInput.click();
  });

  galleryOption.addEventListener("click", function () {
      popupModal.style.display = "none";
      uploadInput.click();
  });

  fileInput.addEventListener("change", handleImageUpload);
  uploadInput.addEventListener("change", handleImageUpload);


function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        let formData = new FormData();
        formData.append("image", file);
        formData.append("message_type", "image");
        formData.append("conversation_id", chatMessages.dataset.conversationId);

      
        fetch(sendMessageUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
               
                event.target.value = ''; 
            }
        })
        .catch(error => console.error(" Error uploading image:", error));
    }
}



  function formatTimestamp(timestamp) {
    if (!timestamp) return "";
    
 
    if (typeof timestamp === 'string') {
        return timestamp;
    }
    
 
    const date = new Date(timestamp);
    
   
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}


  function appendTextMessageToChat(message, messageType, avatarUrl = "", messageId, timestamp = "") {
    const messageContainer = document.createElement("div");
    messageContainer.className = `message-container ${messageType}`;
    messageContainer.id = `message-${messageId}`;
  
    if (avatarUrl) {
      const avatar = document.createElement("img");
      avatar.src = avatarUrl;
      avatar.className = "avatar";
      messageContainer.appendChild(avatar);
    }
  
    const messageDiv = document.createElement("div");
    messageDiv.className = "message " + messageType;
    messageDiv.innerText = message;
  
    const timestampDiv = document.createElement("div");
    timestampDiv.className = "message-timestamp";
    timestampDiv.textContent = formatTimestamp(timestamp);  
  
    messageContainer.appendChild(messageDiv);
    messageContainer.appendChild(timestampDiv);
    chatMessages.appendChild(messageContainer);

chatMessages.scrollTop = chatMessages.scrollHeight;

  }
  

  function appendImageToChat(imageSrc, messageType, avatarUrl = "", messageId, timestamp = "") {
    const messageContainer = document.createElement("div");
    messageContainer.className = `message-container ${messageType}`;
    messageContainer.id = `message-${messageId}`;
  
    if (avatarUrl) {
      const avatar = document.createElement("img");
      avatar.src = avatarUrl;
      avatar.className = "avatar";
      messageContainer.appendChild(avatar);
    }
  
    const imageElement = document.createElement("img");
    imageElement.src = imageSrc;
    imageElement.className = "Image123";
    imageElement.alt = "Uploaded Image";
    imageElement.style.maxWidth = "250px";
    imageElement.style.maxHeight = "250px";
    imageElement.style.width = "auto";
    imageElement.style.height = "auto";
    imageElement.style.borderRadius = "10px";
    imageElement.style.objectFit = "cover";
    imageElement.style.cursor = "pointer";
  
    imageElement.addEventListener("click", () => openImageModal(imageSrc));
  
    const timestampDiv = document.createElement("div");
    timestampDiv.className = "message-timestamp";
    timestampDiv.textContent = formatTimestamp(timestamp);  
  
    messageContainer.appendChild(imageElement);
    messageContainer.appendChild(timestampDiv);
    chatMessages.appendChild(messageContainer);

chatMessages.scrollTop = chatMessages.scrollHeight;

  }
  

});
