import { getCookie } from './utilities.js';



async function updateMessageBrokerStatus(){
    const csrfAccessToken = getCookie('csrf_access_token');
    
    try {
        const response = await fetch('/api/messageBroker', {
            method: "GET",
            headers: {
                'X-CSRF-TOKEN': csrfAccessToken,
            },
        });

        //Get our async api call
        const data = await response.json();
        if (response.ok){
            console.log(data)
            var brokerStatus = document.getElementById('messageBrokerStatus')
            if (data.Message == true){
                brokerStatus.classList.add('status-ok')
            } else {

                brokerStatus.classList.add('status-error')
            }
        }
    } catch (error) {
        console.log(error);
    }
}

async function updateCeleryStatus(){
    const csrfAccessToken = getCookie('csrf_access_token');
    
    try {
        const response = await fetch('/api/celeryStatus', {
            method: "GET",
            headers: {
                'X-CSRF-TOKEN': csrfAccessToken,
            },
        });

        //Get our async api call
        const data = await response.json();
        if (response.ok){
            console.log(data)
            var brokerStatus = document.getElementById('celeryWorkerStatus')
            if (data.Message == true){
                brokerStatus.classList.add('status-ok')
            } else {

                brokerStatus.classList.add('status-error')
            }
        }
    } catch (error) {
        console.log(error);
    }
}


document.addEventListener('DOMContentLoaded', function () {
    console.log('checking Redis-Server');
    updateMessageBrokerStatus();
    console.log('checking Celery worker');
    updateCeleryStatus();

});