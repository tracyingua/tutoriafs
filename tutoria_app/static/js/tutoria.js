function toggleNotificationDropdown() {
    const notificationDropdown = document.getElementById('notificationDropdown');
    const profileDropdown = document.getElementById('dropdownMenu'); 
    const notificationDropdown1 = document.getElementById('notificationDropdown1'); 
    const dropdownNav = document.getElementById('dropdownMenuNav'); 

  
    if (profileDropdown) profileDropdown.style.display = 'none';
    if (notificationDropdown1) notificationDropdown1.style.display = 'none';
    if (dropdownNav) dropdownNav.style.display = 'none';

   
    notificationDropdown.style.display = notificationDropdown.style.display === 'block' ? 'none' : 'block';
}

function toggleNotificationDrop() {
    const notificationDropdown1 = document.getElementById('notificationDropdown1');
    const profileDropdown = document.getElementById('dropdownMenu');
    const notificationDropdown = document.getElementById('notificationDropdown'); 
    const dropdownNav = document.getElementById('dropdownMenuNav');

    if (profileDropdown) profileDropdown.style.display = 'none';
    if (notificationDropdown) notificationDropdown.style.display = 'none';
    if (dropdownNav) dropdownNav.style.display = 'none';

   
    notificationDropdown1.style.display = notificationDropdown1.style.display === 'block' ? 'none' : 'block';
}

function toggleDropdownNav() {
    const dropdownNav = document.getElementById('dropdownMenuNav');
    const profileDropdown = document.getElementById('dropdownMenu'); 
    const notificationDropdown = document.getElementById('notificationDropdown'); 
    const notificationDropdown1 = document.getElementById('notificationDropdown1'); 

  
    if (profileDropdown) profileDropdown.style.display = 'none';
    if (notificationDropdown) notificationDropdown.style.display = 'none';
    if (notificationDropdown1) notificationDropdown1.style.display = 'none';

    dropdownNav.style.display = dropdownNav.style.display === 'block' ? 'none' : 'block';
}

function toggleDropdown() {
    const profileDropdown = document.getElementById('dropdownMenu');
    const notificationDropdown = document.getElementById('notificationDropdown'); 
    const notificationDropdown1 = document.getElementById('notificationDropdown1'); 
    const dropdownNav = document.getElementById('dropdownMenuNav'); 

 
    if (notificationDropdown) notificationDropdown.style.display = 'none';
    if (notificationDropdown1) notificationDropdown1.style.display = 'none';
    if (dropdownNav) dropdownNav.style.display = 'none';

   
    profileDropdown.style.display = profileDropdown.style.display === 'block' ? 'none' : 'block';
}


document.addEventListener('click', function (event) {
    const notificationDropdown = document.getElementById('notificationDropdown');
    const notificationIcon = document.querySelector('.notification-container');
    const profileDropdownNav = document.getElementById('dropdownMenuNav');
    const profileIconNav = document.querySelector('.profile-icon-container');
    const profileDropdown = document.getElementById('dropdownMenu');
    const profileIcon = document.querySelector('.profile-dropdown');

    if (notificationDropdown && !notificationIcon.contains(event.target)) {
        notificationDropdown.classList.remove('show');
    }

    if (profileDropdown && !profileIcon.contains(event.target)) {
        profileDropdown.classList.remove('show');
    }

    if (profileDropdownNav && !profileIconNav.contains(event.target)) {
        profileDropdownNav.classList.remove('show');
    }
});






window.addEventListener('resize', function () {
    const notificationDropdown = document.getElementById('notificationDropdown');
    const profileDropdownNav = document.getElementById('dropdownMenuNav');
    const profileDropdown = document.getElementById('dropdownMenu');

    if (window.innerWidth > 768) {
        notificationDropdown.style.display = 'none';
        profileDropdownNav.style.display = 'none';
        profileDropdown.style.display = 'none';
    }
});

