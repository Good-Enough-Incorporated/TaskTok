async function loadHomePage() {
  const token = localStorage.getItem('token');
  try {
      const response = await fetch('/home', {
          method: 'GET',
          headers: {
              'Authorization': `Bearer ${localStorage.getItem('AccessToken')}`
          }
      });

      if (response.ok) {
          console.log('good to go!')
          const htmlContent = await response.text();
          document.body.innerHTML = htmlContent;
      } else {
          console.error('Failed to load home page:', await response.text());
          // Handle error, for example, by redirecting to the login page
          window.location.href = '/login';
      }
  } catch (error) {
      console.error('Error fetching home page:', error);
      // Handle error, possibly by showing a message to the user
  }
}

// Call this function after successful login



document.addEventListener('DOMContentLoaded', function(){
//Use the DOMContentLoaded to make sure the DOM is fully loaded before trying to load our script.
  document.getElementById('loginForm').addEventListener('submit', async function (event) {
    event.preventDefault();
  
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username,
          password
        })
      });
  
      if (!response.ok) {
        console.log(response.status)
        if(response.status === 403){
          document.getElementById('error-message').textContent = "Invalid username or password."
        } else {
          document.getElementById('error-message').textContent = "Unknown error - Please contact your System Administrator."

        }
      }
  
      const data = await response.json();
      console.log("Credentials accepted... saving tokens");
      document.cookie = "AccessToken=" + data.tokens['AccessToken'] + "; path=/";
      window.location.href = '/home';

  
      // Now you can use the token to make authenticated requests to your API
    
  
    } catch (error) {
      console.error('Error during fetch operation:', error.message);
    }
  });
  

});
