// Show Register Form
function showRegister() {
    document.getElementById('authForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
  }
  
  // Show Login Form
  function showLogin() {
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('authForm').style.display = 'block';
  }
  
  // Handle Register Form Submission
  document.getElementById('registerUserForm').addEventListener('submit', function(event) {
    event.preventDefault();
  
    let name = document.getElementById('newName').value;
    let email = document.getElementById('newEmail').value;
    let qualification = document.getElementById('newQualification').value;
    let exam = document.getElementById('newExam').value;
    let password = document.getElementById('newPassword').value;
  
    // Send this data to the backend API for registration (using fetch)
    fetch('http://localhost:5000/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, qualification, exam, password })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('Registration successful! Please log in.');
        showLogin();
      } else {
        alert('Registration failed!');
      }
    });
  });
  
  // Handle Login Form Submission
  document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
  
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
  
    // Send this data to the backend API for login
    fetch('http://localhost:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('Login successful!');
        startInterview();
      } else {
        alert('Login failed!');
      }
    });
  });
  
  // Start Interview Simulation
  function startInterview() {
    document.getElementById('authForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('interviewPage').style.display = 'block';
  
    // Access the webcam
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(function(stream) {
        document.getElementById('webcamVideo').srcObject = stream;
      })
      .catch(function(err) {
        console.log("Webcam error: " + err);
      });
  
    // Fetch an AI-generated interview question (replace with your API)
    fetch('http://localhost:5000/getInterviewQuestion')
      .then(response => response.json())
      .then(data => {
        document.getElementById('question').textContent = data.question;
      });
  }
  
// Submit Answer and Get Feedback
function submitAnswer() {
    let answer = document.getElementById('answer').value;

    // Send the answer to the backend API for processing
    fetch('http://localhost:5000/submitAnswer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answer })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Assuming you get feedback from the server
            document.getElementById('feedback').textContent = data.feedback;
            document.getElementById('feedbackContainer').style.display = 'block';
        } else {
            alert('There was an issue processing your answer.');
        }
    })
    .catch(error => {
        console.log("Error submitting answer:", error);
        alert("An error occurred while submitting your answer.");
    });
}
