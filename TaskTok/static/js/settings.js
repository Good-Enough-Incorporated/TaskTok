import { showToast, clearModal, getCookie, format_backend_datetime, enableVerticalScroll } from './utilities.js';

document.addEventListener('DOMContentLoaded', function () {
    var confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'), {});
    var form = document.querySelector('form');
    var credentialForm = document.getElementById('form_credential')
    var updateCredentialButton = document.getElementById('update_userpassword_btn')
    var updatePersonalInfoButton = document.getElementById('update_userpassword_btn');
    var timezoneInput = document.getElementById('timezoneInput');
    var timezoneOptions = document.querySelectorAll('.timezone-option');
    var dropdownMenu = document.querySelector('.dropdown-menu');
    var dropDownOpen = false;
    var isConfirmPressed = false;
    
    credentialForm.addEventListener('submit', function(event) {
        var scrollPosition = window.scrollY || document.documentElement.scrollTop;
        sessionStorage.setItem('scrollPosition', scrollPosition);
    });


    //event handler for updating user info
    form.addEventListener('submit', function(event){

        if(!isConfirmPressed){
            
            //prevent the form submission
            event.preventDefault();

            //add the fields to show the user
            addInputFieldsToModal();

            //show the confirm modal
            confirmationModal.show();
            
            document.getElementById('confirmUpdate').addEventListener('click', function(event){
                isConfirmPressed = true
                //manually force the form submit
                form.submit();
            });

        }


    });

    // Event handler for document click
    document.addEventListener('click', function (event) {
        // Check if the click is outside the input and dropdown menu
        var isClickInside = timezoneInput.contains(event.target) || dropdownMenu.contains(event.target);

        if (!isClickInside) {
            hideDropdown();
        }
    });

    // Show dropdown menu
    function showDropdown() {
        dropdownMenu.classList.add('show');
    }

    // Hide dropdown menu
    function hideDropdown() {
        dropdownMenu.classList.remove('show');
    }
    // Toggle dropdown on input focus
    timezoneInput.addEventListener('focus', function(){
        dropdownMenu.classList.add('show');
        dropDownOpen = true;
    });

    dropdownMenu.addEventListener('mousedown', function(e){
        e.preventDefault();
    })

    // Hide dropdown on input blur
    timezoneInput.addEventListener('blur', function() {
        if (!dropDownOpen){ 
            dropdownMenu.classList.remove('show');
        }

    });

    dropdownMenu.addEventListener('click', function(e) {
        console.log(e.target);
        
        if (e.target.matches('.timezone-option')) {
            e.preventDefault();
            timezoneInput.value = e.target.textContent;
            hideDropdown();
            dropDownOpen = false;
            timezoneInput.blur()
            
        }
    });

// Function to add input fields to the modal
function addInputFieldsToModal() {
    // Get the element where inputs will be appended
    var modalInputs = document.querySelector('.modal-body');

    // Clear previous inputs if any
    modalInputs.innerHTML = '';

    var confirm_message = document.createElement('label');
    confirm_message.textContent = "You're about to update the following information:"
    confirm_message.className = 'confirm-label';

    var confirm_message2 = document.createElement('label');
    confirm_message2.className = 'confirm-label';
    confirm_message2.textContent = "Are you sure?"
   

    // Create new input elements
    var confirm_un_input = document.createElement('input');
    var confirm_em_input = document.createElement('input');
    var confirm_fn_input = document.createElement('input');
    var confirm_ln_input = document.createElement('input');

    var confirm_un_label = document.createElement('label');
    var confirm_em_label = document.createElement('label');
    var confirm_fn_label = document.createElement('label');
    var confirm_ln_label = document.createElement('label');

    

    confirm_un_input.type = 'text';
    confirm_un_input.className = 'form-control mb-2';
    confirm_un_input.value = document.getElementById('username').value
    confirm_un_input.readOnly = true;
    confirm_un_label.textContent = "Username"

    confirm_em_input.type = 'text';
    confirm_em_input.className = 'form-control mb-2';
    confirm_em_input.value = document.getElementById('email').value
    confirm_em_input.readOnly = true;
    confirm_em_label.textContent = "E-Mail"

    confirm_fn_input.type = 'text';
    confirm_fn_input.className = 'form-control mb-2';
    confirm_fn_input.value = document.getElementById('first_name').value ? document.getElementById('first_name').value : "";
    confirm_fn_input.readOnly = true;
    confirm_fn_label.textContent = "First Name"

    confirm_ln_input.type = 'text';
    confirm_ln_input.className = 'form-control mb-2';
    confirm_ln_input.value = document.getElementById('last_name').value ? document.getElementById('last_name').value : "";
    confirm_ln_input.readOnly = true;
    confirm_ln_label.textContent = "Last Name"



    // Append inputs to the modal
    modalInputs.appendChild(confirm_message);

    modalInputs.appendChild(confirm_un_label);
    modalInputs.appendChild(confirm_un_input);

    modalInputs.appendChild(confirm_em_label);
    modalInputs.appendChild(confirm_em_input);
  

  
    modalInputs.appendChild(confirm_fn_label);
    modalInputs.appendChild(confirm_fn_input);

    modalInputs.appendChild(confirm_ln_label);
    modalInputs.appendChild(confirm_ln_input);



    modalInputs.appendChild(confirm_message2);
}




    function filterTimeZone(searchText){
        timezoneOptions.forEach(function (option) {
            if (option.textContent.toLowerCase().indexOf(searchText.toLowerCase()) > -1){
                option.style.display = '';
            } else {
                option.style.display = 'none';
            }
        });
    }
    timezoneInput.addEventListener('input', function(){
        filterTimeZone(this.value)
    });
    //event handler for when user selects a specific timezone-option
  

});

window.onbeforeunload = function(){
    var scrollPosition = window.scrollY || document.documentElement.scrollTop;
    sessionStorage.setItem('scrollPosition', scrollPosition);
};



window.onload = function() {
    //removed query params after an error
    //const baseUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
    //window.history.replaceState(null, null, baseUrl);

    //this will prevent a reload sending the same bad data
    var scrollPosition = sessionStorage.getItem('scrollPosition');
    if (scrollPosition) {
        window.scrollTo(0, scrollPosition);
        sessionStorage.removeItem('scrollPosition');  // Clear the saved position
    }
};