import { showToast, clearModal, getCookie, format_backend_datetime, enableVerticalScroll } from './utilities.js';

document.addEventListener('DOMContentLoaded', function () {
    var timezoneInput = document.getElementById('timezoneInput');
    var timezoneOptions = document.querySelectorAll('.timezone-option');
    var dropdownMenu = document.querySelector('.dropdown-menu');
    var dropDownOpen = false;

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