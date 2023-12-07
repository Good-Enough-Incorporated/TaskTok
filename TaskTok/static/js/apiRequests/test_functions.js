import { showToast, clearModal, getCookie, format_backend_datetime, enableVerticalScroll, isValidEmailList } from '../utilities.js';
// Global variable for the Bootstrap 5 modal instance.
let confirmationModal = null;
let currentTaskID = null;
let tableGrid = null;
let api;
document.addEventListener('DOMContentLoaded', function () {
    // Initialize the Bootstrap 5 modal.
    confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'), {});
    const filterInput = document.getElementById('filter-text-box');
    filterInput.addEventListener('input', onFilterTextBoxChanged)
  
    // Other initialization code.
    //listTask();
    //queryTasks();
    //initializeGrid();
    initializeAGGrid();
    enableVerticalScroll();
    
});




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

            $taskRow.addClass('fadeOutSlideRight');
            $taskRow.on('animationend', function () {
                $taskRow.remove(); // This will remove the row from the DOM after the animation
            });

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


async function listTask() {
    const csrfAccessToken = getCookie('csrf_access_token');
    //pretend long load time
    //await new Promise(r => setTimeout(r, 10000));
    try {
        const response = await fetch('/api/listTask', {
            method: "GET",
            headers: {
                'X-CSRF-TOKEN': csrfAccessToken,
            },
        });

        //Get our async api call
        const data = await response.json();

        console.log(typeof (data.TaskList));
        //legacy table if we need to revert
        
        //createTableHeader()
        
        data.TaskList.forEach(task => {
            console.log(task + ' being added to table')
            //addRowToTable(task);
        });
        
       console.log(data.TaskList)

       const columns = [
         
       
        {id: "task_description", name: "Description"},
        {id: "task_dueDate", name: "Due Date"},
        {id: "task_emailList", name: "E-Mail List"},
        {id: "task_message", name: "E-mail Message"},
        {id: "task_name", name: "Name"},
        {id: "task_reminderOffSetTime", name: "Early Reminder Time"},
        {id: "actions", name:"Actions"}]

        

        const formattedData = data.TaskList.map(item => [
            
            
            item.task_description,
            item.task_dueDate,
            item.task_emailList,
            item.task_message,
            item.task_name,
            item.task_reminderOffSetTime,
            gridjs.html(`
    <button data-id="${item.id}" class='task-edit-btn'>Edit</button>
    <button data-id="${item.id}" class='task-delete-btn'>Delete</button>
  `) 
          ]);
          
        var grid = new gridjs.Grid({
            columns: columns.map(col => col.name),
            style: { 
                table: { 
                  'white-space': 'nowrap'
                }
              },
            data: formattedData,
            search: true,
            sort: true,
            resizable: true,
            pagination: true}).render(document.getElementById('taskTableGrid'));

        



        const addTableButton = document.getElementById('task-add-btn');
        addTableButton.style.visibility = 'visible';

    } catch (error) {
        console.error("Error:", error)
    }
}

async function queryTasks() {

    console.log("QUERYING TASKS")
    const response = await fetch('/api/listTask');
    if (!response.ok) {
        throw new Error('[queryTasks()]: Failed to query tasks');
    }
    const data = await response.json();
    return data.TaskList;
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
    <button data-id="${params.data.id}" class="delete-btn">
        <span class="icon">🗑️</span></button>
    <button data-id="${params.data.id}" class="edit-btn">
        <span class="icon">✏️</span></button>
    `
}
async function initializeAGGrid(){

    const data = await queryTasks();
    console.log(data);
    const gridOptions = {

        rowData: [],
    
        columnDefs:[
           
            {field: "id"},
            {field: "task_name", headerName: "Name"},
            {field: "task_description", headerName: "Description"},
            {field: "task_dueDate",  headerName: "Reminder Time", valueFormatter: dateFormatter},
            {field: "task_reminderOffSetTime", headerName: "Early Reminder Time", valueFormatter: dateFormatter},
            {field: "task_emailList", headerName: "E-Mail Recipient List"},
            {field: "task_message", headerName: "E-Mail Message"},
            {field: "actions", headerName: "Actions", cellRenderer: renderButtonCells, cellRenderParams: {api: api}, width: 150, suppressSizeToFit: true },
  
        ]

    };
    const myGridElement = document.querySelector("#taskTableGrid2");
    api = agGrid.createGrid(myGridElement, gridOptions);
    api.setGridOption('rowData',  data);
    api.sizeColumnsToFit();
    
    
    
    
}

async function initializeGrid(){
    console.log("INITIALIZE GRID")
    tableGrid = new gridjs.Grid({
        columns: [
            "Name",
            "Description",
            "Reminder Time",
            "Early Reminder Time",
            "Email List",
            "EMail Message",
            "Actions"
        ],
        style: { 
            table: { 
              'white-space': 'nowrap'
            }
          },
        search: true,
        sort: true,
        resizable: true,
        pagination: {
            limit: 5,
            server: {
                url: (prev, page, limit) => `${prev}?page=${page+1}&limit=${limit}`
            }
        },
        server: {
            url: "/api/listTaskPagination",
            total: data => data.totalTasks,
            then: data => data.TaskList.map(item =>[
                item.task_name,
                item.task_description,
                item.task_dueDate ? format_backend_datetime(item.task_dueDate) : "",
                item.task_reminderOffSetTime ? format_backend_datetime(item.task_reminderOffSetTime) : "",
                item.task_emailList,
                item.task_email_message,
                gridjs.html(`
    <button data-id="${item.id}" class='edit-btn'></button>
    <button data-id="${item.id}" class='delete-btn'></button>
`) 
            ])
        }
  

    }).render(document.getElementById('taskTableGrid'));

    var buttondiv = document.createElement('div')
    buttondiv.classList.add('gridjs-button');
    var button = document.createElement('button');

    button.textContent = 'New Task'
    button.classList.add('task-add-btn')
    buttondiv.appendChild(button)
    button.style.visibility = 'visible'
    var gridHead = document.querySelector('.gridjs-head')
    //gridHead.appendChild(buttondiv)
    
}

async function refreshAGGrid(){
    const data = await queryTasks();
    console.log("Refreshing grid!");
    api.setGridOption('rowData', data);
}

async function refreshGridData(){
   
        queryTasks().then(data => {
            const mappedData = data.map(item => [
                item.task_name,
                item.task_description,
                item.task_dueDate,
                item.task_reminderOffSetTime,
                item.task_emailList,
                item.task_email_message,
                gridjs.html(`
    <button data-id="${item.id}" class='task-edit-btn'>Edit</button>
    <button data-id="${item.id}" class='task-delete-btn'>Delete</button>
    `) 
    
            ]);

            tableGrid.updateConfig({
                data: mappedData
            }).forceRender();

        })


        // Update the grid with the new data

}


function removeTask(taskID) {
    currentTaskID = taskID;
    confirmationModal.show();
}

document.getElementById('confirmDelete').addEventListener('click', function () {
    if (currentTaskID !== null) {
         deleteTask(currentTaskID)
         refreshAGGrid();
         //refreshGridData();
        
    }
    confirmationModal.hide();
});




document.getElementById('taskTableGrid2').addEventListener('click', function(event) {
    console.log(event.target)
    console.log(event.target.matches('button.delete-btn'))
    if (event.target.matches('.edit-btn')) { //event handler for Edit button
        const dataID = event.target.getAttribute('data-id');
        //document.getElementById('editModal').setAttribute('data-current-editing-task-id', taskID);
        console.log('Opening showEditModal on taskID=', dataID);
        showEditModal(dataID); // Call the new function here
    }
    if (event.target.matches('.delete-btn')){
        const dataID = event.target.getAttribute('data-id');
        console.log('attempting to remove taskID=', dataID);
        removeTask(dataID);
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

