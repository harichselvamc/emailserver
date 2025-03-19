from fastapi import FastAPI, Form, HTTPException 
from pydantic import BaseModel
from typing import List
import smtplib
from fastapi.responses import JSONResponse

app = FastAPI()

# Initialize the list of receiver emails
receiver_emails = [
    "harichselvamc@gmail.com",
    "harichselvam.ds.ai@gmail.com",
 "divyasri346.bme@gmail.com",
"priyanka.668.bme@gmail.com"
"rizwanabegum.1523bme@gmail.com"
]

# Email configuration
sender_email = "screamdetection@gmail.com"  # Replace with your sender email
sender_password = "aobh rdgp iday bpwg"  # Replace with your email password (consider using an App Password if using Gmail)


class Receiver(BaseModel):
    email: str


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
            
            # Send email to all receiver emails
            for receiver_email in receiver_emails:
                server.sendmail(sender_email, receiver_email, full_message)
        
        return "Email sent successfully!"
    except Exception as e:
        return f"An error occurred: {e}"


@app.post("/submit_form/")
async def submit_form(form_data: FormData):
    """Endpoint to handle form submission and send email"""
    # You can format the message however you want, here's a sample.
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
    global receiver_emails
    if operation == "add":
        if receiver.email not in receiver_emails:
            receiver_emails.append(receiver.email)
            return {"status": "success", "message": f"Email {receiver.email} added to the receiver list."}
        else:
            raise HTTPException(status_code=400, detail="Email is already in the list.")
    elif operation == "edit":
        old_email = receiver.email
        if old_email in receiver_emails:
            if new_email:
                receiver_emails.remove(old_email)
                receiver_emails.append(new_email)
                return {"status": "success", "message": f"Email {old_email} edited to {new_email}."}
            else:
                raise HTTPException(status_code=400, detail="New email is required for editing.")
        else:
            raise HTTPException(status_code=404, detail="Email not found in the list.")
    elif operation == "remove":
        if receiver.email in receiver_emails:
            receiver_emails.remove(receiver.email)
            return {"status": "success", "message": f"Email {receiver.email} removed from the receiver list."}
        else:
            raise HTTPException(status_code=404, detail="Email not found in the list.")
    else:
        raise HTTPException(status_code=400, detail="Invalid operation. Use 'add', 'edit', or 'remove'.")


@app.get("/get_receivers/")
async def get_receivers():
    """Endpoint to get the list of receiver emails"""
    return {"receiver_emails": receiver_emails}


# # Running the app
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
