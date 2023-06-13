function sendPostRequest(url, content) {
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(content)
    };
  
    return fetch(url, options)
      .then(response => response.json())
      .then(data => {
        // Handle the response data
        console.log(data);
        return data; // Optional: Return the response data
      })
      .catch(error => {
        // Handle any errors
        console.error('Error:', error);
        throw error; // Optional: Throw the error to be caught by the caller
      });
  }
  