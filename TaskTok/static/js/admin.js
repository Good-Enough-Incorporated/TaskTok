import { getCookie } from './utilities.js';


async function updateServerUtilization(){
    const csrfAccessToken = getCookie('csrf_access_token');
    try{
        const response = await fetch('/api/serverUtilization', {
            method: 'GET',
            headers: {
                'X-CSRF-TOKEN': csrfAccessToken
            },
        });

        const data = await response.json();
        if (response.ok){
            console.log(data);
            var cpu_utilization = data.data.cpu;
            var ram_utilization = data.data.ram;
            var cpu_gage = new JustGage({
                id: "cpu_gage",
                value: cpu_utilization,
                min: 0,
                max: 100,
                title: "CPU Utilization (%)"
              });
              console.log(Math.ceil(cpu_utilization));
              console.log(Math.ceil(ram_utilization));
              var ram_gage = new JustGage({
                id: "ram_gage",
                value: Math.ceil(ram_utilization),
                min: 0,
                max: 100,
                title: "RAM Utilization (%)"
              });
        }
    } catch (exception) {
        console.log(exception)
    }
}


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
    console.log('updating server utilization');
    updateServerUtilization();

});