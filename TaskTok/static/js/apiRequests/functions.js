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
  
    async function listTask() {
        const csrfAccessToken = getCookie('csrf_access_token');
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
 



            } catch (error) {
                console.error("Error:", error)
            }
        }
  // Call this function after successful login
  
  function createTableHeader(){
    var table = document.getElementById('taskTable').getElementsByTagName('thead')[0];
    var newRow = table.insertRow(-1)
    
    var cell1 = newRow.insertCell(0)
    var cell2 = newRow.insertCell(1)
    var cell3 = newRow.insertCell(2)
    var cell4 = newRow.insertCell(3)
    var cell5 = newRow.insertCell(4)
    var cell6 = newRow.insertCell(5)

    cell1.innerHTML = "Owner"
    cell2.innerHTML = "Task Name"
    cell3.innerHTML = "Task Description"
    cell4.innerHTML = "Task Due Date"
    cell5.innerHTML = "Task Due (Offset)"
    cell6.innerHTML = "E-mail List"


  }
  function addRowToTable(task){
    
    var table = document.getElementById('taskTable').getElementsByTagName('tbody')[0];
    var newRow = table.insertRow(-1); //last row

    var cell1 = newRow.insertCell(0);
    var cell2 = newRow.insertCell(1);
    var cell3 = newRow.insertCell(2);
    var cell4 = newRow.insertCell(3);
    var cell5 = newRow.insertCell(4);
    var cell6 = newRow.insertCell(5);

    cell1.innerHTML = task.owner_username;
    cell2.innerHTML = task.task_name;
    cell3.innerHTML = task.task_description;
    cell4.innerHTML = task.task_dueDate;
    cell5.innerHTML = task.task_reminderOffSetTime;
    cell6.innerHTML = task.task_emailList
  }
  
  document.addEventListener('DOMContentLoaded', function(){
  //Use the DOMContentLoaded to make sure the DOM is fully loaded before trying to load our script.
  console.log("testing api calls from js");
 listTask();
    
  
  });
  