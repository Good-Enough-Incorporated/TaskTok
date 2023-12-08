export function showToast(message, duration = 3000) {
    const toast = document.getElementById("toast-container");
    const toastContent = document.getElementById("toast-user-content");
    toastContent.textContent = message;
    toast.classList.add("show");

    // Hide the toast after 'duration' milliseconds
    setTimeout(() => {
        toast.classList.remove("show");
    }, duration);
}

export function clearModal(){
    var editModal = document.getElementById('editModal');
    editModal.style.display = 'none';
    var modalBody = document.getElementById('modal-body');
    var modalFooter = document.getElementById('modal-footer')
    modalBody.innerHTML = "";
    modalFooter.innerHTML = "";
}

export function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  
  export function format_backend_datetime(dateString){
    const date = new Date(dateString);

    let day = date.getDate().toString().padStart(2, '0');
    let month = (date.getMonth() + 1).toString().padStart(2, '0'); // getMonth() returns 0-11
    let year = date.getFullYear();
    let hours = date.getHours().toString().padStart(2, '0');
    let minutes = date.getMinutes().toString().padStart(2, '0');

    return `${month}/${day}/${year} ${hours}:${minutes}`;
}

export function enableVerticalScroll() {
    const scrollContainer = document.querySelector('.archived-tasks-container');
    if (scrollContainer) {
        scrollContainer.addEventListener('wheel', (event) => {
            event.preventDefault();
            scrollContainer.scrollLeft += event.deltaY;
        });
    }
}


// TODO: use a better method of validating more than 1 email addresses?
export function isValidEmailList(emailList) {
    // Check if the email list is empty
    if (!emailList.trim()) {
        return false;
    }

    // Trim whitespace from each email.
    const emails = emailList.split(',').map(email => email.trim());
    // Regular expression for email validation. It's good enough...
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    // Check each email in the list.
    for (const email of emails) {
        // If any email in the list is invalid, return false.
        if (!emailRegex.test(email)) {
            return false;
        }
    }

    // If all emails are valid, return true.
    return true;
}

// Used to update the top right of the nav bar with the current time.
export function updateTime(timezone = null) {
    const options = { timeZone: timezone, hour: '2-digit', minute: '2-digit', second: '2-digit' };
    const now = new Date();
    const timeString = timezone ? now.toLocaleTimeString('en-US', options) : now.toLocaleTimeString();
    document.getElementById('currentTime').textContent = timeString;
}





