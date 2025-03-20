from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
import sqlite3
import smtplib

app = FastAPI()

# Email configuration
sender_email = "screamdetection@gmail.com"  # Replace with your sender email
sender_password = "aobh rdgp iday bpwg"  # Replace with your email password (consider using an App Password if using Gmail)

# Database setup
DB_NAME = "receiver_emails.db"

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS receivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL
    )''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

class Receiver(BaseModel):
    email: str

class EditReceiver(BaseModel):
    old: str
    new: str

class FormData(BaseModel):
    name: str
    gender: str
    cancerType: str
    age: int
    occupation: str
    income: float
    panCardNumber: str
    currentTreatment: str
    costNeeded: float
    aadhaarNumber: str
    address: str
    dob: str

def send_email(subject: str, message: str):
    """Function to send email to all receiver emails"""
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Start TLS for security
            server.login(sender_email, sender_password)
            full_message = f"Subject: {subject}\n\n{message}"
            
            # Fetch the receiver emails from the database
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM receivers")
            receiver_emails = cursor.fetchall()
            conn.close()
            
            # Send email to all receiver emails
            for email_tuple in receiver_emails:
                receiver_email = email_tuple[0]
                server.sendmail(sender_email, receiver_email, full_message)
        
        return "Email sent successfully!"
    except Exception as e:
        return f"An error occurred: {e}"

@app.post("/submit_form/")
async def submit_form(form_data: FormData):
    """Endpoint to handle form submission and send email"""
    message = f"""
    Name: {form_data.name}
    Gender: {form_data.gender}
    Cancer Type: {form_data.cancerType}
    Age: {form_data.age}
    Occupation: {form_data.occupation}
    Income: {form_data.income}
    PAN Card Number: {form_data.panCardNumber}
    Current Treatment: {form_data.currentTreatment}
    Cost Needed: {form_data.costNeeded}
    Aadhaar Number: {form_data.aadhaarNumber}
    Address: {form_data.address}
    Date of Birth: {form_data.dob}
    """
    
    result = send_email("New Form Submission for Cancer Support", message)
    if "successfully" in result:
        return {"status": "success", "message": result}
    else:
        raise HTTPException(status_code=500, detail=result)

@app.post("/manage_receiver/")
async def manage_receiver(receiver: Receiver = None, edit_receiver: EditReceiver = None, operation: str = Form(...)):
    """Endpoint to add, edit, or remove receiver email addresses"""
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if operation == "add" and receiver:
        try:
            cursor.execute("INSERT INTO receivers (email) VALUES (?)", (receiver.email,))
            conn.commit()
            conn.close()
            return {"status": "success", "message": f"Email {receiver.email} added to the receiver list."}
        except sqlite3.IntegrityError:
            conn.close()
            raise HTTPException(status_code=400, detail="Email is already in the list.")
    
    elif operation == "remove" and receiver:
        cursor.execute("DELETE FROM receivers WHERE email = ?", (receiver.email,))
        conn.commit()
        if cursor.rowcount > 0:
            conn.close()
            return {"status": "success", "message": f"Email {receiver.email} removed from the receiver list."}
        else:
            conn.close()
            raise HTTPException(status_code=404, detail="Email not found in the list.")
    
    elif operation == "edit" and edit_receiver:
        cursor.execute("UPDATE receivers SET email = ? WHERE email = ?", (edit_receiver.new, edit_receiver.old))
        conn.commit()
        if cursor.rowcount > 0:
            conn.close()
            return {"status": "success", "message": f"Email {edit_receiver.old} edited to {edit_receiver.new}."}
        else:
            conn.close()
            raise HTTPException(status_code=404, detail="Old email not found in the list.")
    
    else:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid operation. Use 'add', 'remove', or 'edit'.")

@app.get("/receive/")
async def receive_all_emails():
    """Endpoint to fetch all receiver email addresses"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM receivers")
    emails = cursor.fetchall()
    conn.close()

    email_list = [email[0] for email in emails]
    return {"receiver_emails": email_list}
