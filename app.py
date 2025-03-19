from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from typing import List
import smtplib
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize the list of receiver emails
receiver_emails = [
    "harichselvamc@gmail.com",
    "harichselvam.ds.ai@gmail.com"
]

# Email configuration from environment variables
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")


def send_email(subject: str, message: str):
    """Function to send email to all receiver emails"""
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Start TLS for security
            server.login(sender_email, sender_password)
            full_message = f"Subject: {subject}\n\n{message}"

            # Send email to all receiver emails
            for receiver_email in receiver_emails:
                server.sendmail(sender_email, receiver_email, full_message)

        return "Email sent successfully!"
    except Exception as e:
        return f"An error occurred: {e}"


# Pydantic model for receiver email
class Receiver(BaseModel):
    email: str


# Pydantic model for CancerSponsorRequest
class CancerSponsorRequest(BaseModel):
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


@app.post("/submit_form/")
async def submit_form(request: CancerSponsorRequest):
    """Endpoint to handle form submission and send email"""

    # Check for missing fields
    missingFields = []
    if not request.name:
        missingFields.append("Name")
    if not request.gender:
        missingFields.append("Gender")
    if not request.cancerType:
        missingFields.append("Cancer Type")
    if not request.age:
        missingFields.append("Age")
    if not request.occupation:
        missingFields.append("Occupation")
    if not request.income:
        missingFields.append("Income")
    if not request.panCardNumber:
        missingFields.append("PAN Card Number")
    if not request.currentTreatment:
        missingFields.append("Current Cancer Treatment")
    if not request.costNeeded:
        missingFields.append("Cost Needed")
    if not request.aadhaarNumber:
        missingFields.append("Aadhaar Number")
    if not request.address:
        missingFields.append("Address")
    if not request.dob:
        missingFields.append("Date of Birth")

    # If there are missing fields, show an alert message
    if missingFields:
        return JSONResponse(
            status_code=400,
            content={"message": f"Please fill in the following fields: {', '.join(missingFields)}"}
        )

    # Create the message for the email
    message = (
        f"Name: {request.name}\n"
        f"Gender: {request.gender}\n"
        f"Cancer Type: {request.cancerType}\n"
        f"Age: {request.age}\n"
        f"Occupation: {request.occupation}\n"
        f"Income: {request.income}\n"
        f"PAN Card Number: {request.panCardNumber}\n"
        f"Current Treatment: {request.currentTreatment}\n"
        f"Cost Needed: {request.costNeeded}\n"
        f"Aadhaar Number: {request.aadhaarNumber}\n"
        f"Address: {request.address}\n"
        f"Date of Birth: {request.dob}\n"
    )

    # Send email with subject "Cancer Sponsor Request"
    result = send_email("Cancer Sponsor Request", message)
    if "successfully" in result:
        return {"status": "success", "message": "Application submitted successfully and email sent."}
    else:
        raise HTTPException(status_code=500, detail=f"Error sending email: {result}")


@app.post("/addmin/")
async def add_or_edit_receiver(receiver: Receiver, operation: str = Form(...)):
    """Endpoint to add or edit receiver email addresses"""
    global receiver_emails
    if operation == "add":
        if receiver.email not in receiver_emails:
            receiver_emails.append(receiver.email)
            return {"status": "success", "message": f"Email {receiver.email} added to the receiver list."}
        else:
            raise HTTPException(status_code=400, detail="Email is already in the list.")
    elif operation == "edit":
        old_email = receiver.email
        new_email = Form(..., alias="new_email")
        if old_email in receiver_emails:
            receiver_emails.remove(old_email)
            receiver_emails.append(new_email)
            return {"status": "success", "message": f"Email {old_email} edited to {new_email}."}
        else:
            raise HTTPException(status_code=404, detail="Email not found in the list.")
    else:
        raise HTTPException(status_code=400, detail="Invalid operation. Use 'add' or 'edit'.")


@app.get("/get_receivers/")
async def get_receivers():
    """Endpoint to get the list of receiver emails"""
    return {"receiver_emails": receiver_emails}

