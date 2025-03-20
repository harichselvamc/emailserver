from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from typing import List
import smtplib
import sqlite3
from fastapi.responses import JSONResponse

app = FastAPI()

# Email configuration
sender_email = "screamdetection@gmail.com"  # Replace with your sender email
sender_password = "aobh rdgp iday bpwg"  # Replace with your email password (consider using an App Password if using Gmail)

# SQLite database connection setup
DATABASE = "app.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # To fetch results as dictionary-like objects
    return conn

# Create the tables if they don't exist
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create receivers table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS receivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL
    )
    ''')
    
    # Create form_data table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS form_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gender TEXT NOT NULL,
        cancerType TEXT NOT NULL,
        age INTEGER NOT NULL,
        occupation TEXT NOT NULL,
        income REAL NOT NULL,
        panCardNumber TEXT NOT NULL,
        currentTreatment TEXT NOT NULL,
        costNeeded REAL NOT NULL,
        aadhaarNumber TEXT NOT NULL,
        address TEXT NOT NULL,
        dob TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

# Run the function to create the tables
create_tables()

# Receiver model
class Receiver(BaseModel):
    email: str

# FormData model
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

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT email FROM receivers')
            receiver_emails = [row['email'] for row in cursor.fetchall()]
            conn.close()

            # Send email to all receiver emails
            for receiver_email in receiver_emails:
                server.sendmail(sender_email, receiver_email, full_message)

        return "Email sent successfully!"
    except Exception as e:
        return f"An error occurred: {e}"

@app.post("/submit_form/")
async def submit_form(form_data: FormData):
    """Endpoint to handle form submission and send email"""
    # Insert form data into the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO form_data (name, gender, cancerType, age, occupation, income, panCardNumber, currentTreatment, costNeeded, aadhaarNumber, address, dob)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (form_data.name, form_data.gender, form_data.cancerType, form_data.age, form_data.occupation, form_data.income, form_data.panCardNumber,
          form_data.currentTreatment, form_data.costNeeded, form_data.aadhaarNumber, form_data.address, form_data.dob))
    conn.commit()
    conn.close()

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
async def manage_receiver(receiver: Receiver, new_email: str = Form(None), operation: str = Form(...)):
    """Endpoint to add, edit, or remove receiver email addresses"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if operation == "add":
        cursor.execute('''
        INSERT INTO receivers (email) VALUES (?)
        ''', (receiver.email,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Email {receiver.email} added to the receiver list."}
    elif operation == "edit":
        if new_email:
            cursor.execute('''
            UPDATE receivers SET email = ? WHERE email = ?
            ''', (new_email, receiver.email))
            conn.commit()
            conn.close()
            return {"status": "success", "message": f"Email {receiver.email} edited to {new_email}."}
        else:
            conn.close()
            raise HTTPException(status_code=400, detail="New email is required for editing.")
    elif operation == "remove":
        cursor.execute('''
        DELETE FROM receivers WHERE email = ?
        ''', (receiver.email,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Email {receiver.email} removed from the receiver list."}
    else:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid operation. Use 'add', 'edit', or 'remove'.")

@app.get("/get_receivers/")
async def get_receivers():
    """Endpoint to get the list of receiver emails"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM receivers')
    receiver_emails = [row['email'] for row in cursor.fetchall()]
    conn.close()
    return {"receiver_emails": receiver_emails}


# # Running the app
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
