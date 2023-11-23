function clearModal(){
    var modalBody = document.getElementById('modal-body');
    var modalFooter = document.getElementById('modal-footer')
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
                console.log(cookieValue);
                break;
            }
        }
    }
    return cookieValue;
  }
  
  
async function addTask() {
    const csrfAccessToken = getCookie('csrf_access_token');
    try {
        const response = await fetch('/api/addTask', {
            method: "GET",
            headers: {
                'X-CSRF-TOKEN': csrfAccessToken,
            },
            });

            //Get our async api call
            const data = await response.json();
            console.log(data)
        } catch (error) {
            console.error("Error:", error)
        }
    }


async function editTask(taskID) {
    const csrfAccessToken = getCookie('csrf_access_token');
        
    const newDescription = prompt("Enter new description for the task:"); // Use bootstrap instead of this dusty dialog box form.
    if (!newDescription) return;
        
    try {
        const response = await fetch(`/api/editTask/${taskID}`, {
                method: "PUT",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrfAccessToken
                },
                body: JSON.stringify({ task_description: newDescription })
            });
        
        const data = await response.json();
        console.log(data);
        
        if (data.Message == 'Task updated successfully') {
            showToast("Task was successfully updated.", 5000);
            console.log('Task was updated in the database');
                
            // Update the corresponding task in the HTML table with the new description.
            const taskRow = document.querySelector(`tr[data-id="${taskID}"]`);
            if (taskRow) {
                // Task description is currently in column 3.
                const descriptionCell = taskRow.querySelector("td:nth-child(3)")
                    if (descriptionCell) {
                        descriptionCell.textContent = newDescription;
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
  

async function removeTask(taskID) {
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
            removeRowFromTable(taskID);
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
        
        //add event handlers for edit/delete buttons
        addButtonEventHandlers();

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
        button.addEventListener('click', function(event) {
            const dataID = this.closest('tr').getAttribute('data-id');
            if (this.classList.contains('task-edit-btn')) {
                console.log('attempting to edit taskID=', dataID);
                //editTask(dataID);
                getTableInformation(dataID);
                var editModal = document.getElementById('editModal');
                var close = document.getElementsByClassName("close")[0];
                editModal.style.display = 'block';

                close.onclick = function() {
                    editModal.style.display = "none";
                    clearModal();
                  }
                
                window.onclick = function(event) {
                    if(event.target == editModal) {
                        editModal.style.display = 'none';
                        clearModal();
                    }
                }
            } else if (this.classList.contains('task-delete-btn')) {
                console.log('attempting to remove taskID=', dataID);
                removeTask(dataID);
            }
        });
    });
}

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
        if(headerValues[i].innerHTML.trim() === 'Task Due Date'){
            console.log('setting input to datetime-local');
            inputBox.type = 'datetime-local';
        } else {
            inputBox.type = 'text';
        }
        inputBox.type = 'text';
        inputBox.value = cellValues[i].innerHTML;
        inputBox.id = `taskInput${i}`;
        inputBox.name =  headerValues[i].innerHTML;
        inputBox.className = 'modal-fields';
        modal.appendChild(label);
        modal.appendChild(inputBox);
    }
        updateButton = document.createElement('button');
        updateButton.textContent = "Update Task";
        updateButton.className = 'task-update-btn';
        modalFooter.appendChild(updateButton);
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
  
  });
  