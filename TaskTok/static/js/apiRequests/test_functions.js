import { showToast, clearModal, getCookie, format_backend_datetime, enableVerticalScroll, isValidEmailList, updateTime } from '../utilities.js';
// Global variable for the Bootstrap 5 modal instance.
let confirmationModal = null;
let currentTaskID = null;
let currentTaskAction = null;
let tableGrid = null;
let api;

document.addEventListener('DOMContentLoaded', async function() {
    // Initialize the Bootstrap 5 modal.
    confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'), {});
    const filterInput = document.getElementById('filter-text-box');

    // Check if reminder counts are in localStorage and update if they are.
    // If not, fetch tasks and update count for upcoming reminders card.
    if (localStorage.getItem('dueTodayCount')) {
        document.getElementById('dueTodayCount').textContent = localStorage.getItem('dueTodayCount');
        document.getElementById('dueThisWeekCount').textContent = localStorage.getItem('dueThisWeekCount');
        document.getElementById('dueThisMonthCount').textContent = localStorage.getItem('dueThisMonthCount');
    } else {
        // Fetch and update counts if not in localStorage.
        const tasks = await queryAllTasks();
        updateReminderCounts(tasks);
    }

    filterInput.addEventListener('input', onFilterTextBoxChanged);

    initializeAGGrid();
    enableVerticalScroll();
    updateCompletedTasksCarousel();

    // Initialize timezone-based clock update.
    let selectedTimezone = localStorage.getItem('userTimezone') || 'Default_Timezone'; // Use stored timezone.
    setInterval(() => updateTime(selectedTimezone), 1000);
});

    


async function queryNonCompletedTasks() {
    const response = await fetch('/api/listNonCompleteTask');
    if (!response.ok) {
        throw new Error('[queryNonCompletedTasks()]: Failed to query tasks');
    }
    const data = await response.json();
    return data.TaskList;
}



async function queryCompletedTasks() {

    console.log("QUERYING COMPLETED TASKS")
    const response = await fetch('/api/listCompletedTask');
    if (!response.ok) {
        throw new Error('[queryCompletedTasks()]: Failed to query tasks');
    }
    const data = await response.json();
    return data.TaskList;
}

async function queryAllTasks() {

    console.log("QUERYING ALL TASKS")
    const response = await fetch('/api/listAllTask');
    if (!response.ok) {
        throw new Error('[queryAllTasks()]: Failed to query tasks');
    }
    const data = await response.json();
    return data.TaskList;
}


// This function fetches nonCompletedTasks() and updates reminder counts.
async function fetchNonCompletedTasksAndUpdateReminders() {
    try {
        const nonCompletedTasks = await queryNonCompletedTasks();
        updateReminderCounts(nonCompletedTasks);
    } catch (error) {
        console.error("Error fetching non-completed tasks:", error);
    }
}

// This function calculates and updates the counts for dueToday, dueThisWeek, and dueThisMonth
// for the upcoming reminders card.
function updateReminderCounts(taskList) {
    let dueToday = 0, dueThisWeek = 0, dueThisMonth = 0;

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const startOfNextWeek = new Date(today);
    startOfNextWeek.setDate(today.getDate() - today.getDay() + 7);
    const startOfNextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1);

    taskList.forEach(task => {
        const dueDate = new Date(task.task_dueDate);
        dueDate.setHours(0, 0, 0, 0);

        if (dueDate >= today && dueDate < tomorrow) {
            dueToday++;
        }
        if (dueDate >= today && dueDate < startOfNextWeek) {
            dueThisWeek++;
        }
        if (dueDate >= today && dueDate < startOfNextMonth) {
            dueThisMonth++;
        }
    });

    // Save the counts to localStorage.
    localStorage.setItem('dueTodayCount', dueToday);
    localStorage.setItem('dueThisWeekCount', dueThisWeek);
    localStorage.setItem('dueThisMonthCount', dueThisMonth);

    // Update the DOM elements.
    document.getElementById('dueTodayCount').textContent = dueToday;
    document.getElementById('dueThisWeekCount').textContent = dueThisWeek;
    document.getElementById('dueThisMonthCount').textContent = dueThisMonth;
}



// Defining when up-coming Task Reminders is updated.
setInterval(fetchNonCompletedTasksAndUpdateReminders, 60000); // Update every 60 seconds.




// Add Event Listener to the Add Task Form.
document.getElementById('addTaskForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const form = event.currentTarget;

    // Basic form validation.
    if (!form.checkValidity()) {
        event.stopPropagation();
        form.classList.add('was-validated');
        showToast("Please fill out all input boxes before submitting", 5000);
        return;
    }

    // Fetch form data.
    const taskName = document.getElementById('taskName').value;
    const taskDescription = document.getElementById('taskDescription').value;
    let taskDueDate = document.getElementById('taskDueDate').value;
    let taskReminderOffset = document.getElementById('taskReminderOffset').value;
    const taskEmailList = document.getElementById('taskEmailList').value;
    const taskEmailMessage = document.getElementById('taskEmailMessage').value;

    // Additional email list validation.
    if (!isValidEmailList(taskEmailList)) {
        showToast("Please enter valid email addresses.", 5000);
        return;
    }

    // Check if reminder offset is before the due date.
    taskDueDate = new Date(taskDueDate);
    taskReminderOffset = new Date(taskReminderOffset);
    if (taskReminderOffset > taskDueDate) {
        showToast("Reminder Offset must be before the due date.", 5000);
        return;
    }

    // Proceed with form submission...
    try {
        const csrfAccessToken = getCookie('csrf_access_token');
        const flask_wtf_csrf = document.getElementById('flask_wtf_csrf_token');

        const response = await fetch('/api/addTask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrfAccessToken,
                'FLASK-WTF-CSRF': flask_wtf_csrf.value
            },
            body: JSON.stringify({
                task_name: taskName,
                task_description: taskDescription,
                task_dueDate: format_backend_datetime(taskDueDate),
                task_reminderOffSetTime: format_backend_datetime(taskReminderOffset),
                task_emailList: taskEmailList,
                task_email_message: taskEmailMessage
            })
        });

        const data = await response.json();
        if (response.ok && data.Message === "add_success") {
            // Handle successful response
            showToast(`Task successfully created!`, 5000);
            data.TaskList[0].task_dueDate = format_backend_datetime(data.TaskList[0].task_dueDate);
            data.TaskList[0].task_reminderOffSetTime = format_backend_datetime(data.TaskList[0].task_reminderOffSetTime);
            //addRowToTable(data.TaskList[0]); // Add the new task to the table
            //refreshGridData();
            refreshAGGrid();
        } else {
            showToast(data.Error, 5000);
        }
    } catch (error) {
        console.error("Error:", error);
        showToast('An error occurred while adding the task', 5000);
    }

    // Reset form fields and close the modal
    document.getElementById('taskName').value = '';
    document.getElementById('taskDescription').value = '';
    document.getElementById('taskDueDate').value = '';
    document.getElementById('taskReminderOffset').value = '';
    document.getElementById('taskEmailList').value = '';
    document.getElementById('taskEmailMessage').value = '';
    bootstrap.Modal.getInstance(document.getElementById('taskAddModal')).hide();
});






async function showEditModal(taskID) {
    // Fetching task data from API.
    clearModal();
    try {
        
        const csrfAccessToken = getCookie('csrf_access_token');
        const response = await fetch(`/api/getTask/${taskID}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrfAccessToken
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const taskData = await response.json();
        const task = taskData.Task;
        console.log(task.task_dueDate)
        console.log(task.task_reminderOffSetTime)

        // Populate the edit modal fields with the task details
        document.getElementById('editTaskName').value = task.task_name;
        document.getElementById('editTaskDescription').value = task.task_description;
        document.getElementById('editTaskDueDate').value = format_backend_datetime(task.task_dueDate);
        document.getElementById('editTaskReminderOffset').value = task.task_reminderOffSetTime ?
        format_backend_datetime(task.task_reminderOffSetTime) : "";
        document.getElementById('editTaskEmailList').value = task.task_emailList;

        // Set current editing taskID as a data attribute on the edit modal.
        document.getElementById('editModal').setAttribute('data-current-editing-task-id', taskID);

        // Show the modal
        let editModal = new bootstrap.Modal(document.getElementById('editModal'));
        editModal.show();

        flatpickr("#editTaskReminderOffset", {
            enableTime: true,
            allowInput: true,
            dateFormat: "m/d/Y H:i"
        });

        flatpickr("#editTaskDueDate", {
            enableTime: true,
            allowInput: true,
            dateFormat: "m/d/Y H:i"
        });

        // Attach event handler to the "Save" button in the edit modal.
        const saveButton = document.getElementById('saveEdit')
        if (!saveButton.getAttribute('data-click-handler')) {
        
            saveButton.addEventListener('click', function () {

            // Validate the offset date
            var offsetDate = document.getElementById("editTaskReminderOffset").value;
            if (!offsetDate) {
                // Show the toast for offset date required.
                showToast("Please provide the offset date for the task.");
                return; // Prevent further execution of editTask
            }

        const currentEditingTaskId = document.getElementById('editModal').getAttribute('data-current-editing-task-id');

        if (currentEditingTaskId) {
            
            editTask(currentEditingTaskId);
        }
      
        });
        saveButton.setAttribute('data-click-handler', true);
        }


    } catch (error) {
        console.error('Error fetching task data:', error);
        // Handle errors, e.g., display an error message.
    }
}

async function setCompleteTask(taskID){
    try{

    
    const csrfAccessToken = getCookie('csrf_access_token');
    const response = await fetch(`/api/completeTask/${taskID}`, {
        method: "GET",
        headers: {
            'X-CSRF-TOKEN': csrfAccessToken,
        }
    })
    const data = await response.json()
    if (response.ok && data.Message == "successfully marked complete."){
        showToast("Task was marked complete!",5000);
        confirmationModal.hide();

        // Refresh the carousel with the updated list of completed tasks.
        await updateCompletedTasksCarousel();
        
    } else {
        showToast("Failed to mark task as complete :(", 5000);
        confirmationModal.hide();
    }
    } catch {
        showToast("An error occurred while trying to mark the task as complete.", 5000);
        console.error(error);
        confirmationModal.hide();
    }
}

async function updateCompletedTasksCarousel() {
    try {
        
        console.log('checking for completed tasks')
        const completedTasks = await queryCompletedTasks();

        const carouselInner = document.querySelector('#completedTasksCarousel .carousel-inner');
        carouselInner.innerHTML = ''; // Clear existing content.

        if (completedTasks.length === 0) {
            console.log('no completed tasks found for user');
            carouselInner.innerHTML = '<div class="carousel-item active"><p>No completed tasks.</p></div>';
        } else {
            console.log('adding completed tasks');
            completedTasks.forEach((task, index) => {
                const div = document.createElement('div');
                div.className = 'carousel-item' + (index === 0 ? ' active' : '');
                div.innerHTML = `<h5>${task.task_name}</h5><p>${task.task_description}</p>`;
                carouselInner.appendChild(div);
            });
        }
    } catch (error) {
        console.error(error);
    }
}



async function editTask(taskID) {
    // Fetch values from the modal's input fields.
    const taskName = document.getElementById('editTaskName').value;
    const taskDescription = document.getElementById('editTaskDescription').value;
    let taskDueDate = document.getElementById('editTaskDueDate').value;
    let taskReminderOffset = document.getElementById('editTaskReminderOffset').value;
    const taskEmailList = document.getElementById('editTaskEmailList').value;

    // Validate the email list first.
    if (!isValidEmailList(taskEmailList)) {
        showToast("Please enter valid email addresses.", 5000);
        return;
    }

    const csrfAccessToken = getCookie('csrf_access_token');

    // Check if reminder offset is after the due date.
    if (taskReminderOffset > taskDueDate) {
        showToast("Reminder Offset must be before the due date.", 5000);
        return;
    }


    try {
        const flask_wtf_csrf = document.getElementById('flask_wtf_csrf_token')
        const response = await fetch(`/api/editTask/${taskID}`, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrfAccessToken,
                'FLASK-WTF-CSRF': flask_wtf_csrf.value
            },
            body: JSON.stringify({

                task_name: taskName,
                task_description: taskDescription,
                task_dueDate: taskDueDate,
                task_reminderOffSetTime: taskReminderOffset,
                task_emailList: taskEmailList,


            })
        });

        const data = await response.json();
        console.log(data);

        if (data.Message === 'Task updated successfully') {
            showToast("Task was successfully updated.", 5000);
            console.log('Task was updated in the database');

            // Update the corresponding task in the HTML table with the new description.
            //refreshGridData();
            refreshAGGrid();
            // Close the modal.
            let editModal = bootstrap.Modal.getInstance(document.getElementById('editModal'));
            editModal.hide();
        } else {
            showToast("Task failed to be updated.", 5000);
            console.log('Something went wrong when updating the task');
        }

    } catch (error) {
        showToast('Oops, an error occurred. Please try again.', 5000)
        console.error("Error:", error);
    }
}





async function deleteTask(taskID) {

    console.log("Delete task called for task ID:", taskID);


    //we need a csrfAccessToken to make our API call
    console.log("[removeTask]: beginning client api request")
    const csrfAccessToken = getCookie('csrf_access_token');
    console.log("[removeTask]: obtained csrf token")
    try {
        console.log("[removeTask]: calling /api/removeTask/ call")
        const response = await fetch(`api/removeTask/${taskID}`, {
            method: "GET",
            headers: {
                'X-CSRF-TOKEN': csrfAccessToken
            },
        });
        console.log("[removeTask]: waiting for response")
        const data = await response.json();
        console.log("[removeTask]: response received!")
        if (data.Message === 'remove_success') {
            showToast("Task was successfully removed.", 5000);
            console.log(`Task was deleted from the database ${data.task_id}`)
            const taskRow = document.querySelector(`tr[data-id="${taskID}"]`);
            const $taskRow = $(taskRow)

            //refreshAGGrid();

            //removeRowFromTable(taskID);


        } else {
            showToast("Task failed to be removed :(", 5);
            console.log(`Something went wrong when deleting the task ${data.Error}`)
        }
        //console.log(data);


    } catch (error) {
        showToast('Oops, looks like your session expired :( Please refresh the page.', 10000)
        console.error("Error:", error);
    }

}



const dateFormatter = (params) => {
    const date =  new Date(params.value).toLocaleDateString('en-us', {
      weekday: 'long',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
    const time = new Date(params.value).toLocaleTimeString('en-us');
    return `${date} ${time}`;
  };

function onFilterTextBoxChanged() {
    api.setGridOption(
        'quickFilterText',
        document.getElementById('filter-text-box').value
    );
    }

function renderButtonCells(params){
    return `
    <div class='grid-button-wrapper'>
    <button data-id="${params.data.id}" class="complete-btn">
    <span class="icon">✅</span></button>
    <button data-id="${params.data.id}" class="delete-btn">
        <span class="icon">🗑️</span></button>
    <button data-id="${params.data.id}" class="edit-btn">
        <span class="icon">✏️</span></button>
    `
}

function onBtShowNoRows() {
    api.showNoRowsOverlay();
  }
  
  function onBtHide() {
    api.hideOverlay();
  }

async function initializeAGGrid(){
    const gridDataLoadFailedError = "Brad here... yikes I couldn't find any tasks."

    console.log("initializting AG Grid")
    const gridOptions = {

overlayLoadingTemplate:
    '<div style="position:absolute;top:0;left:0;right:0; bottom:0; background: url(https://ag-grid.com/images/ag-grid-loading-spinner.svg) center no-repeat" aria-label="loading"></div>',
  overlayNoRowsTemplate:
    `<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; margin-top: 100px; text-align: center;" aria-label="loading">
    <div style="background: url(/static/images/no_content_loaded.png) center no-repeat; background-size: contain; height: 60%;"></div>
    <div style="display: inline-flex; justify-content: center; align-items: center; border: 2px solid #ccc; color: white; background-color: rgb(15, 61, 77); margin-top: 10px; padding: 10px; border-radius: 10px;">
        <p style="margin: 0; line-height: normal;">${gridDataLoadFailedError}</p>
    </div>
</div>`,
        pagination: true,
        paginationPageSize: 10,
        rowData: [],
    
        columnDefs:[
           
            {field: "id"},
            {field: "task_name", headerName: "Name"},
            {field: "task_description", headerName: "Description"},
            {field: "task_dueDate",  headerName: "Reminder Time", valueFormatter: dateFormatter},
            {field: "task_reminderOffSetTime", headerName: "Early Reminder Time", valueFormatter: dateFormatter},
            {field: "task_emailList", headerName: "E-Mail Recipient List"},
            {field: "task_message", headerName: "E-Mail Message"},
            {field: "actions", headerName: "Actions", cellRenderer: renderButtonCells, cellRendererParams: {api: api}, width: 200, suppressSizeToFit: true },
  
        ]

    };
    //setting AG Grid to use the empty element TaskTableGrid2
    const myGridElement = document.querySelector("#taskTableGrid2");
    api = agGrid.createGrid(myGridElement, gridOptions)
    //shows our loading overlay
    api.showLoadingOverlay();
    //await new Promise(resolve => setTimeout(resolve, 5000)).then( data => console.log("done pretend waiting"));
    const data = await queryNonCompletedTasks();
    if (data.length == 0){
        api.showNoRowsOverlay();
    }else {
        api.hideOverlay();
    }
   
    api.setGridOption('rowData',  data);
    api.sizeColumnsToFit();
    
    
    
    
    
}

function csvJSON(csv){

    var lines=csv.split("\n");
  
    var result = [];
  
    // NOTE: If your columns contain commas in their values, you'll need
    // to deal with those before doing the next step 
    // (you might convert them to &&& or something, then covert them back later)
    // jsfiddle showing the issue https://jsfiddle.net/
    var headers=lines[0].split(",");
  
    for(var i=1;i<lines.length;i++){
  
        var obj = {};
        var currentline=lines[i].split(",");
  
        for(var j=0;j<headers.length;j++){
            obj[headers[j]] = currentline[j];
        }
  
        result.push(obj);
  
    }
  
    //return result; //JavaScript object
    return JSON.stringify(result); //JSON
  }

function exportTableToExcel(){
    queryAllTasks()
    .then(data =>
        {
            console.log(data);
            const worksheet = XLSX.utils.json_to_sheet(data)
            const workbook = XLSX.utils.book_new()
            XLSX.utils.book_append_sheet(workbook, worksheet, "sheet1")
            XLSX.writeFile(workbook,"TaskTokData.xlsx")
        }
    )
    .catch( exportError => console.log("Failed to export to excel, ", exportError));

}

async function refreshAGGrid(){
    const data = await queryNonCompletedTasks();
    console.log("Refreshing grid!");
    api.setGridOption('rowData', data);
}



function removeTask(taskID) {
    currentTaskID = taskID;
    currentTaskAction = "delete";
    confirmationModal.show();
}

document.getElementById('confirmAction').addEventListener('click', function () {
    if (currentTaskID !== null && currentTaskAction === "delete") {
        //make our API query to delete the task, then refresh the grid
         deleteTask(currentTaskID).then( () => refreshAGGrid() );
         confirmationModal.hide();
        
    } else if (currentTaskID !== null && currentTaskAction === "complete"){
        setCompleteTask(currentTaskID).then( () => refreshAGGrid());
    }
    
});

document.getElementById('exportToExcelButton').addEventListener('click', exportTableToExcel);


document.getElementById('taskTableGrid2').addEventListener('click', function(event) {
    console.log(event.target)
    console.log(event.target.matches('button.delete-btn'))
    if (event.target.matches('.edit-btn')) { //event handler for Edit button
        const dataID = event.target.getAttribute('data-id');
        //document.getElementById('editModal').setAttribute('data-current-editing-task-id', taskID);
        console.log('Opening showEditModal on taskID=', dataID);
        showEditModal(dataID); // Call the new function here
    }
    else if (event.target.matches('.delete-btn')){
        const dataID = event.target.getAttribute('data-id');
        currentTaskID = dataID;
        currentTaskAction = "delete";
        console.log('attempting to remove taskID=', dataID);
        const confirmationBody = document.getElementById('confirmTextContent')
        confirmationBody.innerHTML = ""
        confirmationBody.innerHTML = `<p> Are you sure you want to delete ${dataID}?</p> <p>Warning, this is a permanent action!</p> `;
        removeTask(dataID);
    }
    else if (event.target.matches(".complete-btn")){
        const dataID = event.target.getAttribute('data-id');
        currentTaskID = dataID;
        currentTaskAction = "complete";
        console.log(`Attempting to mark task complete (${dataID})`);
        const confirmationBody = document.getElementById('confirmTextContent')
        confirmationBody.innerHTML = ""
        confirmationBody.innerHTML = `<p> Are you sure you want to mark ${dataID} as complete?</p> <p>Warning, this is permanent action!</p>`;
        confirmationModal.show();
        //setCompleteTask(dataID);
    }
    
});

window.addEventListener('resize', event => {

    api.sizeColumnsToFit()

})
    


// DOMContentLoaded event listener
document.addEventListener('DOMContentLoaded', function () {
    // Initialization code...
    $('#taskAddModal').on('shown.bs.modal', function () {
        flatpickr("#taskDueDate", {
            enableTime: true,
            allowInput: true,
            dateFormat: "m/d/Y H:i"
        });

        flatpickr("#taskReminderOffset", {
            enableTime: true,
            allowInput: true,
            dateFormat: "m/d/Y H:i"
        });
    });
    // Attach event listener to the "Save" button in the edit modal
    document.getElementById('saveEdit').addEventListener('click', function () {
        const currentEditingTaskId = document.getElementById('editModal').getAttribute('data-current-editing-task-id');




        if (currentEditingTaskId) {
            //this is ran twice, we can probably delete this or the other event listener
            //editTask(currentEditingTaskId);
        }
    });

});

