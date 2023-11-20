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
    var newRow = table.insertRow(-1)
    
    var cell1 = newRow.insertCell(0)
    var cell2 = newRow.insertCell(1)
    var cell3 = newRow.insertCell(2)
    var cell4 = newRow.insertCell(3)
    var cell5 = newRow.insertCell(4)
    var cell6 = newRow.insertCell(5)
    var cell7 = newRow.insertCell(6)
    cell1.innerHTML = "Owner"
    cell2.innerHTML = "Task Name"
    cell3.innerHTML = "Task Description"
    cell4.innerHTML = "Task Due Date"
    cell5.innerHTML = "Task Due (Offset)"
    cell6.innerHTML = "E-mail List"
    cell7.innerHTML = "Actions"


  }

  function addButtonEventHandlers(){
    document.querySelectorAll('.task-edit-btn, .task-delete-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            const dataID = this.closest('tr').getAttribute('data-id');
            if (this.classList.contains('task-edit-btn')) {
                console.log('attempting to edit taskID=', dataID);
                editTask(dataID);
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
  