import openai
import smtplib
import ssl
import cv2
import speech_recognition as sr
import mysql.connector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from textblob import TextBlob

# Initialize OpenAI API key
openai.api_key = 'YOUR_API_KEY'

# Initialize the recognizer for microphone
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Database Connection Class
class Candidate:
    def __init__(self, name, password, qualification, email, exam, assessment=0):
        self.name = name
        self.password = password
        self.qualification = qualification
        self.email = email
        self.exam = exam
        self.assessment = assessment

class Simulation:
    def __init__(self):
        # Establish database connection
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="root",         # Default username for XAMPP
            password="",         # Default password for XAMPP (empty)
            database="interview_simulation"
        )
        self.db_cursor = self.db_connection.cursor()

    def register(self):
        print("Registration")
        name = input("Enter your name: ")
        qualification = input("Enter your qualification: ")
        email = input("Enter your email address: ")
        exam = input("Enter the interview exam you want to prepare for: ")
        password = input("Enter your password: ")

        # Create a candidate object (for DB interaction)
        candidate = Candidate(name, password, qualification, email, exam)

        # Store candidate information in the database
        sql = """
        INSERT INTO candidates (name, password, qualification, email, exam, assessment)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        val = (candidate.name, candidate.password, candidate.qualification, candidate.email, candidate.exam, candidate.assessment)
        
        self.db_cursor.execute(sql, val)
        self.db_connection.commit()
        
        print("Registration successful!")

    def login(self):
        print("Login")
        name = input("Enter your name: ")
        password = input("Enter your password: ")

        # Fetch candidate info from the database based on name and password
        sql = "SELECT * FROM candidates WHERE name = %s AND password = %s"
        self.db_cursor.execute(sql, (name, password))

        result = self.db_cursor.fetchone()
        if result:
            print("Login successful!")
            print(f"Welcome, {result[1]} ({result[4]})")  # Print name and email from result
            return result  # Return the result containing email for sending assessment
        else:
            print("Incorrect name or password.")
            return None

# Function to send email
def send_email(candidate_email, subject, body):
    sender_email = "your_email@gmail.com"
    password = "your_email_password"  # Use App Password if using Gmail with 2FA enabled

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = candidate_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Set up the secure SSL context
    context = ssl.create_default_context()

    # Send the email via Gmail's SMTP server
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, candidate_email, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

# Function to generate AI interview question using GPT-3
def ask_interview_question():
    prompt = "Generate an interview question for a software developer role"
    
    response = openai.Completion.create(
        engine="text-davinci-003",  # You can use the latest model available
        prompt=prompt,
        max_tokens=100
    )
    
    question = response.choices[0].text.strip()
    return question

# Function to listen to the candidate's answer using the microphone
def listen_to_answer():
    with mic as source:
        print("Please answer the question: ")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        answer = recognizer.recognize_google(audio)
        print(f"Candidate's Answer: {answer}")
        return answer
    except sr.UnknownValueError:
        print("Sorry, I could not understand the answer.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ""

# Function to analyze the answer and provide strengths and weaknesses
def analyze_answer(answer):
    blob = TextBlob(answer)
    sentiment = blob.sentiment.polarity
    
    if sentiment > 0.1:
        strength = "Strong communication skills."
        weakness = "None identified."
    elif sentiment < -0.1:
        strength = "Needs improvement in communication."
        weakness = "Weak communication skills."
    else:
        strength = "Neutral response."
        weakness = "Could improve clarity."
    
    return strength, weakness

# Start the interview simulation
def start_interview():
    print("Starting the interview...\n")
    
    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    
    # Ask interview question using GPT-3
    question = ask_interview_question()
    print(f"AI: {question}")
    
    # Listen to candidate's answer via microphone
    answer = listen_to_answer()
    
    # Analyze the answer to determine strengths and weaknesses
    strength, weakness = analyze_answer(answer)

    # Send the email with the assessment results
    subject = "Your Interview Assessment Results"
    body = f"""
    Dear Candidate,

    Thank you for your participation in the interview simulation.

    Assessment Summary:
    Strength: {strength}
    Weakness: {weakness}

    We hope this helps in your preparation.

    Best regards,
    The Interview Simulation Team
    """
    
    # After login, candidate email is available
    candidate_email = result[4]  # Assuming result[4] contains the email address
    
    send_email(candidate_email, subject, body)

    # Show the video feed (camera)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Interview Camera", frame)
        
        # Press 'q' to end the interview
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Main flow
simulation = Simulation()

while True:
    print("\n1. Register")
    print("2. Login")
    print("3. Exit")
    choice = input("Choose an option: ")

    if choice == "1":
        simulation.register()
    elif choice == "2":
        result = simulation.login()
        if result:
            start_interview()
    elif choice == "3":
        break
    else:
        print("Invalid choice, please try again.")
