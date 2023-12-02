


  
async function addTask() {
    const csrfAccessToken = getCookie('csrf_access_token');
    const taskInput1 = document.getElementById('taskInput1').value;
    const taskInput2 = document.getElementById('taskInput2').value;
    const taskInput3 = document.getElementById('taskInput3').value;
    const taskInput4 = document.getElementById('taskInput4').value;
    const taskInput5 = document.getElementById('taskInput5').value;
    const taskInput6 = document.getElementById('taskInput6').value;

    //terrible way to check, but it'll do for now.
    if(taskInput1.length == 0 || taskInput2.length == 0 || taskInput3.length == 0 || taskInput4.length == 0 || taskInput5.length == 0 || taskInput6.length == 0){
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
            if(data.Message == "add_success") {
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


async function editTask(taskID) {
    const csrfAccessToken = getCookie('csrf_access_token');
    //Grab the values from the text fields
    //ensure we're validating this as safe on our endpoint as it 
    //make no sense on the client side
    const taskInput1 = document.getElementById('taskInput1').value;
    const taskInput2 = document.getElementById('taskInput2').value;
    const taskInput3 = document.getElementById('taskInput3').value;
    const taskInput4 = document.getElementById('taskInput4').value;
    const taskInput5 = document.getElementById('taskInput5').value;
    console.log(taskInput1);
    console.log(taskInput2);
    console.log(taskInput3);
    console.log(taskInput4);
    console.log(taskInput5);

        
    try {
        const response = await fetch(`/api/editTask/${taskID}`, {
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

                
                })
            });
        
        const data = await response.json();
        console.log(data);
        
        if (data.Message == 'Task updated successfully') {
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
                        nameCell.textContent = taskInput1;
                    }
                    if (descriptionCell) {
                        descriptionCell.textContent = taskInput2;
                    }
                    if (dueDateCell) {
                        dueDateCell.textContent = taskInput3;
                    }
                    if (offSetCell) {
                        offSetCell.textContent = taskInput4;
                    }
                    if (emailListCell) {
                        emailListCell.textContent = taskInput5;
                    }
                }
            } else {
                showToast("Task failed to be updated.", 5000);
                console.log('Something went wrong when updating the task');
            }
        
        } catch (error) {
            showToast('Oops, an error occurred. Please try again.', 5000)
            console.error("Error:", error);
        }
    }

 // Global variable to store the current task ID.
let currentTaskID = null;

async function removeTask(taskID) {
    // Store the task ID globally
    currentTaskID = taskID;

    // Show the delete confirmation modal.
    $('#confirmationModal').modal('show');
}

// Fix: Bind the deleteTask function to the confirmation button in the modal
document.getElementById('confirmDelete').addEventListener('click', function() {
    // Call the function to delete the task
    if (currentTaskID !== null) {
        deleteTask(currentTaskID); // Change to deleteTask
    }
    // Hide the modal
    $('#confirmationModal').modal('hide');
});


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
        if (data.Message == 'remove_success'){
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
    var table = document.getElementById('taskTable').getElementsByTagName('thead')[0];
    var newRow = table.insertRow(-1)//add to the bottom
    
    function createHeaderCell(text){
        var cell = document.createElement('th');
        cell.innerHTML = text;
        newRow.appendChild(cell)
    }

    createHeaderCell("Owner");
    createHeaderCell("Task Name");
    createHeaderCell("Task Description");
    createHeaderCell("Task Due Date");
    createHeaderCell("Task Due (Offset)");
    createHeaderCell("E-mail List");
    createHeaderCell("Actions");


  }

  function addButtonEventHandlers(){
    document.querySelectorAll('.task-edit-btn, .task-delete-btn').forEach(button => {
        if (!button.getAttribute('data-click-handler')) {
            button.addEventListener('click', function(event) {
                const dataID = this.closest('tr').getAttribute('data-id');

                if (this.classList.contains('task-edit-btn')) {
                    console.log('attempting to edit taskID=', dataID);
                    getTableInformation(dataID);
                    var editModal = document.getElementById('editModal');
                    var close = document.getElementsByClassName("close")[0];
                    editModal.style.display = 'block';

                    close.onclick = function() {
                        editModal.style.display = "none";
                        clearModal();
                    }
                } else if (this.classList.contains('task-delete-btn')) {
                    console.log('attempting to remove taskID=', dataID);
                    removeTask(dataID); // Change made here to call removeTask
                }
            });
            button.setAttribute('data-click-handler', true);
        }
    });
}


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
        if(inputBox.id == 'taskInput3'){
            dateTimeInput = document.getElementById('taskInput3')
            dateTimeInput.type = 'datetime-local'
            unparsedDate = cellValues[i].innerHTML.toString()
            console.log(unparsedDate.indexOf('.'));
            if(unparsedDate.indexOf('.') == -1){
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

  
  document.addEventListener('DOMContentLoaded', function(){
  //Use the DOMContentLoaded to make sure the DOM is fully loaded before trying to load our script.

  //Add button event handlers for edit/delete actions.
  //Uses the data-id field to determine which task was selected

  console.log("testing api calls from js");
  listTask();
  console.log('hello')
  enableVerticalScroll();
  
  });
  
  function enableVerticalScroll(){
    const scrollContainer = document.querySelector('.archived-tasks-container');

    // Check if the container exists
    if (scrollContainer) {
        scrollContainer.addEventListener('wheel', (event) => {
            // Prevent the default vertical scroll
            event.preventDefault();

            // Scroll horizontally instead
            scrollContainer.scrollLeft += event.deltaY;
        });
    }
  }