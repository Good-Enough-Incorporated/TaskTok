import { showToast, clearModal, getCookie, format_backend_datetime, enableVerticalScroll, isValidEmailList } from '../utilities.js';
// Global variable for the Bootstrap 5 modal instance.
let confirmationModal = null;
let currentTaskID = null;

document.addEventListener('DOMContentLoaded', function () {
    // Initialize the Bootstrap 5 modal.
    confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'), {});

    // Other initialization code.
    listTask();
    enableVerticalScroll();
    
});




// Add Event Listener to the Add Task Form.
document.getElementById('addTaskForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const form = event.currentTarget;



    // Fetch form data
    const taskName = document.getElementById('taskName').value;
    const taskDescription = document.getElementById('taskDescription').value;
    let taskDueDate = document.getElementById('taskDueDate').value;
    let taskReminderOffset = document.getElementById('taskReminderOffset').value;
    const taskEmailList = document.getElementById('taskEmailList').value;
    const taskEmailMessage = document.getElementById('taskEmailMessage').value;

    // Basic validation for now...
    if (!taskName || !taskDescription || !taskDueDate || !taskReminderOffset || !taskEmailList || !taskEmailMessage) {
        showToast("Please fill out all input boxes before submitting", 5000);
        return;
    }

    // If the user enters an invalid email address return error message.
    if (!form.checkValidity() || !isValidEmailList(taskEmailList)) {
        event.stopPropagation();
        form.classList.add('was-validated');
        showToast("Please enter valid email addresses.", 5000);
        return;
    }

    // Convert dates to JavaScript Date objects for comparison.
    taskDueDate = new Date(taskDueDate);
    taskReminderOffset = new Date(taskReminderOffset);

    // Check if reminder offset is before the due date.
    if (taskReminderOffset > taskDueDate) {
        showToast("Reminder Offset must be before the due date.", 5000);
        return;
    }


    console.log(taskDueDate);
    console.log(taskReminderOffset);
    console.log(format_backend_datetime(taskDueDate));
    console.log(format_backend_datetime(taskReminderOffset));

    const csrfAccessToken = getCookie('csrf_access_token');
    console.log('token is:')
    console.log(csrfAccessToken)

    try {
     
    
        const flask_wtf_csrf = document.getElementById('flask_wtf_csrf_token')

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
        console.log('request made to /addTask');
        const data = await response.json();

        if (response.ok && data.Message === "add_success") {
            showToast(`Task successfully created!`, 5000);

            // format_backend_datetime' here to format the date for display
            console.log(data.TaskList[0].task_dueDate)
            console.log(data.TaskList[0].task_reminderOffSetTime)
            console.log(format_backend_datetime(data.TaskList[0].task_dueDate))
            console.log(format_backend_datetime(data.TaskList[0].task_reminderOffSetTime))
            
            data.TaskList[0].task_dueDate = format_backend_datetime(data.TaskList[0].task_dueDate);
            data.TaskList[0].task_reminderOffSetTime = format_backend_datetime(data.TaskList[0].task_reminderOffSetTime);
            addRowToTable(data.TaskList[0]); // Add the new task to the table
        } else {
            showToast(data.Error, 5000);
        }

    } catch (error) {
        console.error("Error:", error);
        showToast('An error occurred while adding the task', 5000);
    }

    // Reset form fields and close bootstrap modal.
    document.getElementById('taskName').value = '';
    document.getElementById('taskDescription').value = '';
    document.getElementById('taskDueDate').value = '';
    document.getElementById('taskReminderOffset').value = '';
    document.getElementById('taskEmailList').value = '';
    document.getElementById('taskEmailMessage').value = '';
    bootstrap.Modal.getInstance(document.getElementById('taskAddModal')).hide();
});




async function addTask() {
    const csrfAccessToken = getCookie('csrf_access_token');
    const taskInput1 = document.getElementById('taskInput1').value;
    const taskInput2 = document.getElementById('taskInput2').value;
    const taskInput3 = document.getElementById('taskInput3').value;
    const taskInput4 = document.getElementById('taskInput4').value;
    const taskInput5 = document.getElementById('taskInput5').value;
    const taskInput6 = document.getElementById('taskInput6').value;

    //terrible way to check, but it'll do for now.
    if (taskInput1.length === 0 || taskInput2.length === 0 || taskInput3.length === 0 || taskInput4.length === 0
        || taskInput5.length === 0 || taskInput6.length === 0) {
        console.log("NULL");
        showToast("Please fill out all iput boxes before submitting", 5000)
        return;
    }


    try {
        console.log('attempting to make api request');
        const response = await fetch('/api/addTask', {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrfAccessToken
            },
            body: JSON.stringify({

                task_name: taskInput1,
                task_description: taskInput2,
                task_dueDate: taskInput3,
                task_reminderOffSetTime: taskInput4,
                task_emailList: taskInput5,
                task_email_message: taskInput6


            })
        });
        console.log('made request');
        // Get our async api call.
        clearModal();
        const data = await response.json();
        console.log(data)
        if (data.Message === "add_success") {
            console.log('whats data.TaskList');
            data.TaskList.forEach(task => {
                addRowToTable(task);
            });
 
            showToast(`Task successfully created!`, 5000)
            console.log('adding button event handlers')
        
        } else {
            showToast(data.Error, 5000)
        }
    } catch (error) {
        console.error("Error:", error)
    }
}


async function showEditModal(taskID) {
    // Fetching task data from API.
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
        document.getElementById('editTaskReminderOffset').value = task.task_reminderOffSetTime ? format_backend_datetime(task.task_reminderOffSetTime) : "";
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

        // Attach event handler to the "Save" button in the edit modal
        document.getElementById('saveEdit').addEventListener('click', function () {
            // Validate the offset date
            var offsetDate = document.getElementById("editTaskReminderOffset").value;
            if (!offsetDate) {
                // Show the toast for offset date required
                showToast("Please provide the offset date for the task.");
                return; // Prevent further execution of editTask
            }

            // Continue with editTask() call if offset date is provided,
            editTask(taskID); // Call editTask with the specific task ID
        });
    } catch (error) {
        console.error('Error fetching task data:', error);
        // Handle errors, e.g., display an error message
    }
}



async function editTask(taskID) {
    // Fetch values from the modal's input fields.
    const taskName = document.getElementById('editTaskName').value;
    const taskDescription = document.getElementById('editTaskDescription').value;
    let taskDueDate = document.getElementById('editTaskDueDate').value;
    let taskReminderOffset = document.getElementById('editTaskReminderOffset').value;
    const taskEmailList = document.getElementById('editTaskEmailList').value;


    // Debugging: Log the formatted dates.
    console.log("Formatted Due Date:", taskDueDate);
    console.log("Formatted Reminder Offset:", taskReminderOffset);

    const csrfAccessToken = getCookie('csrf_access_token');

    // Check if reminder offset is after the due date.
    if (taskReminderOffset > taskDueDate) {
        showToast("Reminder Offset must be before the due date.", 5000);
        return; // Stop the function execution here
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
            const taskRow = document.querySelector(`tr[data-id="${taskID}"]`);
            if (taskRow) {
                const nameCell = taskRow.querySelector("td:nth-child(2)")
                const descriptionCell = taskRow.querySelector("td:nth-child(3)")
                const dueDateCell = taskRow.querySelector("td:nth-child(4)")
                const offSetCell = taskRow.querySelector("td:nth-child(5)")
                const emailListCell = taskRow.querySelector("td:nth-child(6)")
                if (nameCell) {
                    nameCell.textContent = taskName;
                }
                if (descriptionCell) {
                    descriptionCell.textContent = taskDescription;
                }
                if (dueDateCell) {
                    dueDateCell.textContent = taskDueDate;
                }
                if (offSetCell) {
                    offSetCell.textContent = taskReminderOffset;
                }
                if (emailListCell) {
                    emailListCell.textContent = taskEmailList;
                }
            }
            // Close the modal
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

        console.log(typeof (data));

        createTableHeader()
        data.TaskList.forEach(task => {
            console.log(task + ' being added to table')
            addRowToTable(task);
        });
        


        const addTableButton = document.getElementById('task-add-btn');
        addTableButton.style.visibility = 'visible';

    } catch (error) {
        console.error("Error:", error)
    }
}

function createTableHeader() {
    var table = document.getElementById('taskTable');
    var thead = table.getElementsByTagName('thead')[0];

    // Check if header already exists
    if (thead.rows.length === 0) {
        var newRow = thead.insertRow(-1); // Add to the bottom

        function createHeaderCell(text) {
            var cell = document.createElement('th');
            cell.innerHTML = text;
            newRow.appendChild(cell);
        }

        createHeaderCell("Owner");
        createHeaderCell("Task Name");
        createHeaderCell("Task Description");
        createHeaderCell("Task Due Date");
        createHeaderCell("Task Due (Offset)");
        createHeaderCell("E-mail List");
        createHeaderCell("Actions");
    }
}

function removeTask(taskID) {
    currentTaskID = taskID;
    confirmationModal.show();
}

document.getElementById('confirmDelete').addEventListener('click', function () {
    if (currentTaskID !== null) {
        deleteTask(currentTaskID);
    }
    confirmationModal.hide();
});


//TODO: will not need if using jQuery
function removeRowFromTable(taskID) {
    const row = document.querySelector(`tr[data-id="${taskID}"]`);
    if (row) {
        row.remove();
    }
}

// Function to add a new row to the task table
function addRowToTable(task) {
    var table = document.getElementById('taskTable').getElementsByTagName('tbody')[0];
    var newRow = table.insertRow(-1); // insert into last row.
    newRow.setAttribute('data-id', task.id);

    var cell1 = newRow.insertCell(0);
    var cell2 = newRow.insertCell(1);
    var cell3 = newRow.insertCell(2);
    var cell4 = newRow.insertCell(3);
    var cell5 = newRow.insertCell(4);
    var cell6 = newRow.insertCell(5);
    var cell7 = newRow.insertCell(6);

    cell1.innerHTML = task.owner_username;
    cell2.innerHTML = task.task_name;
    cell3.innerHTML = task.task_description;
    cell4.innerHTML = format_backend_datetime(task.task_dueDate);
    cell5.innerHTML = task.task_reminderOffSetTime ? format_backend_datetime(task.task_reminderOffSetTime) : '';
    cell6.innerHTML = task.task_emailList;
    cell7.innerHTML = '<button class="task-edit-btn">Edit</button><button class="task-delete-btn">Delete</button>';
}








document.getElementById('taskTable').addEventListener('click', function(event) {
    if (event.target.matches('button.task-edit-btn')) { //event handler for Edit button
        const dataID = event.target.closest('tr').getAttribute('data-id');
        console.log('Opening showEditModal on taskID=', dataID);
        showEditModal(dataID); // Call the new function here
    }
    if (event.target.matches('button.task-delete-btn')){
        const dataID = event.target.closest('tr').getAttribute('data-id');
        console.log('attempting to remove taskID=', dataID);
        removeTask(dataID);
    }
});

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

