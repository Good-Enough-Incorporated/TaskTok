// Global variable for the Bootstrap 5 modal instance
let confirmationModal = null;
let currentTaskID = null;

document.addEventListener('DOMContentLoaded', function(){
    // Initialize the Bootstrap 5 modal
    confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'), {});

    // Other initialization code
    listTask();
    enableVerticalScroll();
    addButtonEventHandlers();
});

function clearModal() {
    var editModal = document.getElementById('editModal');
    editModal.style.display = 'none';
    var modalBody = document.getElementById('modal-body');
    var modalFooter = document.getElementById('modal-footer');
    modalBody.innerHTML = "";
    modalFooter.innerHTML = "";
}

function getCookie(name) {
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

// Rest of your addTask, editTask, deleteTask, listTask, etc. functions
// ...

async function addTask() {
    const csrfAccessToken = getCookie('csrf_access_token');
    const taskInput1 = document.getElementById('taskInput1').value;
    const taskInput2 = document.getElementById('taskInput2').value;
    const taskInput3 = document.getElementById('taskInput3').value;
    const taskInput4 = document.getElementById('taskInput4').value;
    const taskInput5 = document.getElementById('taskInput5').value;
    const taskInput6 = document.getElementById('taskInput6').value;

    //terrible way to check, but it'll do for now.
    if(taskInput1.length === 0 || taskInput2.length === 0 || taskInput3.length === 0 || taskInput4.length === 0 || taskInput5.length === 0 || taskInput6.length === 0){
        console.log("NULL");
        showToast("Please fill out all iput boxes before submitting", 5000)
        return;
    }


    try {
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

            //Get our async api call
            clearModal();
            const data = await response.json();
            console.log(data)
            if(data.Message === "add_success") {
                console.log('whats data.TaskList');
                data.TaskList.forEach(task => {
                    addRowToTable(task);
                });
                addButtonEventHandlers();

                showToast(`Task successfully created!`, 5000)
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

        // Populate the edit modal fields
        document.getElementById('editTaskName').value = taskData.task_name;
        document.getElementById('editTaskDescription').value = taskData.task_description;
        document.getElementById('editTaskDueDate').value = taskData.task_dueDate;
        document.getElementById('editTaskReminderOffset').value = taskData.task_reminderOffSetTime;
        document.getElementById('editTaskEmailList').value = taskData.task_emailList;

        // Show the modal
        let editModal = new bootstrap.Modal(document.getElementById('editModal'));
        editModal.show();

        // Attach event handler to the "Save" button in the edit modal
        document.getElementById('saveEdit').addEventListener('click', function() {
            editTask(taskID); // Call editTask with the specific task ID
        });
    } catch (error) {
        console.error('Error fetching task data:', error);
        // Handle errors, e.g., display an error message
    }
}





async function editTask(taskID) {
    // Fetch values from the modal's input fields
    const taskName = document.getElementById('editTaskName').value; // Ensure this ID matches your modal's input field
    const taskDescription = document.getElementById('editTaskDescription').value; // Same as above
    const taskDueDate = document.getElementById('editTaskDueDate').value; // Add more fields as per your modal form
    const taskReminderOffset = document.getElementById('editTaskReminderOffset').value;
    const taskEmailList = document.getElementById('editTaskEmailList').value;

    const csrfAccessToken = getCookie('csrf_access_token');

    try {
        const response = await fetch(`/api/editTask/${taskID}`, {
                method: "PUT",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrfAccessToken
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
    try{
        console.log("[removeTask]: calling /api/removeTask/ call")
        const response =  await fetch(`api/removeTask/${taskID}`, {
            method: "GET",
            headers: {
                'X-CSRF-TOKEN': csrfAccessToken
            },
        });
        console.log("[removeTask]: waiting for response")
        const data = await response.json();
        console.log("[removeTask]: response received!")
        if (data.Message === 'remove_success'){
            showToast("Task was successfully removed.", 5000);
            console.log('Task was deleted from the database')
            const taskRow = document.querySelector(`tr[data-id="${taskID}"]`);
            const $taskRow = $(taskRow)

            $taskRow.addClass('fadeOutSlideRight');
            $taskRow.on('animationend', function() {
                $taskRow.remove(); // This will remove the row from the DOM after the animation
              });

            //removeRowFromTable(taskID);



        } else {
            showToast("Task failed to be removed :(", 5);
            console.log('Something went wrong when deleting the task')
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

            console.log(typeof(data));

            createTableHeader()
            data.TaskList.forEach(task => {
                addRowToTable(task);
            });
            addButtonEventHandlers();

        //add event handlers for edit/delete buttons
        //addButtonEventHandlers();
        const addTableButton = document.getElementById('task-add-btn');
        addTableButton.style.visibility = 'visible';

        } catch (error) {
            console.error("Error:", error)
        }
}
    function createTableHeader(){
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

document.getElementById('confirmDelete').addEventListener('click', function() {
    if (currentTaskID !== null) {
        deleteTask(currentTaskID);
    }
    confirmationModal.hide();
});

function addButtonEventHandlers() {
    document.querySelectorAll('.task-edit-btn, .task-delete-btn').forEach(button => {
        if (!button.getAttribute('data-click-handler')) {
            button.addEventListener('click', function(event) {
                const dataID = this.closest('tr').getAttribute('data-id');
                if (this.classList.contains('task-edit-btn')) {
                    console.log('attempting to edit taskID=', dataID);
                    showEditModal(dataID); // Call the new function here
                } else if (this.classList.contains('task-delete-btn')) {
                    console.log('attempting to remove taskID=', dataID);
                    removeTask(dataID);
                }
            });
            button.setAttribute('data-click-handler', true);
        }
    });
}



// Additional functions
// ...
//TODO: will not need if using jQuery
  function removeRowFromTable(taskID){
    const row = document.querySelector(`tr[data-id="${taskID}"]`);
    if(row){
        row.remove();
    }
  }
  function addRowToTable(task){

    var table = document.getElementById('taskTable').getElementsByTagName('tbody')[0];
    var newRow = table.insertRow(-1); //last row
    newRow.setAttribute('data-id', task.id)
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
    cell4.innerHTML = task.task_dueDate;
    cell5.innerHTML = task.task_reminderOffSetTime;
    cell6.innerHTML = task.task_emailList
    //cell7.innerHTML = '<td><input type="submit" value="Edit"></td><td><input type="submit" value="Delete"></td>'
    cell7.innerHTML = '<button class="task-edit-btn">Edit</button><button class="task-delete-btn">Delete</button>'

  }

  function getTableInformation(taskId){
    var table = document.getElementById('taskTable');
    var modal = document.getElementById('modal-body');
    var modalFooter = document.getElementById('modal-footer');
    var headerValues = table.getElementsByTagName('th');
    //need to query the row by using the data-id
    //otherwise we'll get a list of all values which isn't very helpful.
    var row   = table.querySelector(`tr[data-id="${taskId}"]`)
    var cellValues = row.getElementsByTagName('td');
    //do not include this in our list
    const skipHeaders = ['actions', 'owner'];
    for(var i=0; i < headerValues.length; i++){
        //create the label
        if (skipHeaders.includes(headerValues[i].innerHTML.toLowerCase())){
            continue; //do not create these elements
        }
        label = document.createElement('label');
        label.innerHTML = headerValues[i].innerHTML;
        label.htmlFor = `taskLabel${i}`;
        inputBox = document.createElement('input');

        inputBox.type = 'text';

        inputBox.type = 'text';
        inputBox.value = cellValues[i].innerHTML;
        inputBox.id = `taskInput${i}`;
        inputBox.name =  headerValues[i].innerHTML;
        inputBox.className = 'modal-fields';
        modal.appendChild(label);
        modal.appendChild(inputBox);
        if(inputBox.id === 'taskInput3'){
            dateTimeInput = document.getElementById('taskInput3')
            dateTimeInput.type = 'datetime-local'
            unparsedDate = cellValues[i].innerHTML.toString()
            console.log(unparsedDate.indexOf('.'));
            if(unparsedDate.indexOf('.') === -1){
                //already in the format we want.
                formattedDate = unparsedDate

            } else {
                //parse to allow the datetime-local to load the correct date.
                formattedDate = unparsedDate.substring(0, unparsedDate.indexOf('.'))
            }
            dateTimeInput.value = formattedDate
        }

    }
        updateButton = document.createElement('button');
        updateButton.textContent = "Update Task";
        updateButton.className = 'task-update-btn';
        modalFooter.appendChild(updateButton);
        updateButton.onclick = function(){
            console.log("Updating task")
            editTask(taskId);

        }
  }

  function addTaskModal(){
    var modal = document.getElementById('modal-body');
    var modalFooter = document.getElementById('modal-footer');
    const fields = ['Task Name', 'Task Description', 'Task Due Date', 'Task Due (Offset)', 'E-Mail List', 'E-mail Message'];
    var elementNumber = 1;
    fields.forEach(field => {
        //Create the element
        label = document.createElement('label');
        console.log(field)
        label.id = `taskLabel${elementNumber}`;
        label.innerHTML = field;
        label.name = `taskLabel${elementNumber}`;

        input = document.createElement('input');
        input.id = `taskInput${elementNumber}`;
        input.name = `taskInput${elementNumber}`;
        input.type = 'text'
        input.className = 'modal-fields';
        modal.appendChild(label);
        modal.appendChild(input);

        elementNumber++;


    });

        console.log('setting to datetime-local')
        dateTimeInput = document.getElementById('taskInput3')
        dateTimeInput.type = 'datetime-local'
        dateTimeInput.setAttribute('step', 1)
        dateTimeInput = document.getElementById('taskInput4')
        dateTimeInput.type = 'datetime-local'
        dateTimeInput.setAttribute('step', 1)


    addButton = document.createElement('button');
    addButton.textContent = "Add Task";
    addButton.className = 'task-update-btn';
    modalFooter.appendChild(addButton);
    addButton.onclick = function(){
        console.log("Clicked add button");
        addTask();
    }


    var editModal = document.getElementById('editModal');
    var close = document.getElementsByClassName("close")[0];
    editModal.style.display = 'block';

    close.onclick = function() {
        editModal.style.display = "none";
        clearModal();
      }
  }
  function showToast(message, duration = 3000) {
    const toast = document.getElementById("toast-container");
    const toastContent = document.getElementById("toast-user-content");
    toastContent.textContent = message;
    toast.classList.add("show");

    // Hide the toast after 'duration' milliseconds
    setTimeout(() => {
        toast.classList.remove("show");
    }, duration);
}

  document.addEventListener('DOMContentLoaded', function(){
  //Use the DOMContentLoaded to make sure the DOM is fully loaded before trying to load our script.

  //Add button event handlers for edit/delete actions.
  //Uses the data-id field to determine which task was selected

  console.log("testing api calls from js");
  listTask();
  console.log('hello')
  enableVerticalScroll();

  });


function enableVerticalScroll() {
    const scrollContainer = document.querySelector('.archived-tasks-container');
    if (scrollContainer) {
        scrollContainer.addEventListener('wheel', (event) => {
            event.preventDefault();
            scrollContainer.scrollLeft += event.deltaY;
        });
    }
}

// Ensure all other functionalities are correctly updated for Bootstrap 5 if needed
