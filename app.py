from fastapi import FastAPI, Form, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import smtplib
from fastapi.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI()

# SQLite Database Configuration
DATABASE_URL = "sqlite:///./test.db"  # SQLite database file
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # Needed for SQLite
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the ReceiverEmail model (table)
class ReceiverEmail(Base):
    __tablename__ = 'receiver_emails'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Email configuration
sender_email = "screamdetection@gmail.com"  # Replace with your sender email
sender_password = "aobh rdgp iday bpwg"  # Replace with your email password (consider using an App Password if using Gmail)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Email sending function
def send_email(subject: str, message: str, db: Session):
    """Function to send email to all receiver emails"""
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Start TLS for security
            server.login(sender_email, sender_password)
            full_message = f"Subject: {subject}\n\n{message}"
            
            # Fetch all receiver emails from the database
            receivers = db.query(ReceiverEmail).all()
            for receiver in receivers:
                server.sendmail(sender_email, receiver.email, full_message)
        
        return "Email sent successfully!"
    except Exception as e:
        return f"An error occurred: {e}"

# Pydantic models for validation
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

# Endpoint to submit form data and send email
@app.post("/submit_form/")
async def submit_form(form_data: FormData, db: Session = Depends(get_db)):
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
    
    result = send_email("New Form Submission", message, db)
    if "successfully" in result:
        return {"status": "success", "message": result}
    else:
        raise HTTPException(status_code=500, detail=result)

# Endpoint to add or edit receiver email addresses
@app.post("/addmin/")
async def add_or_edit_receiver(receiver: Receiver, new_email: str = Form(None), operation: str = Form(...), db: Session = Depends(get_db)):
    """Endpoint to add or edit receiver email addresses"""
    if operation == "add":
        existing_receiver = db.query(ReceiverEmail).filter(ReceiverEmail.email == receiver.email).first()
        if not existing_receiver:
            new_receiver = ReceiverEmail(email=receiver.email)
            db.add(new_receiver)
            db.commit()
            return {"status": "success", "message": f"Email {receiver.email} added to the receiver list."}
        else:
            raise HTTPException(status_code=400, detail="Email is already in the list.")
    elif operation == "edit":
        old_receiver = db.query(ReceiverEmail).filter(ReceiverEmail.email == receiver.email).first()
        if old_receiver:
            if new_email:
                old_receiver.email = new_email
                db.commit()
                return {"status": "success", "message": f"Email {receiver.email} edited to {new_email}."}
            else:
                raise HTTPException(status_code=400, detail="New email is required for editing.")
        else:
            raise HTTPException(status_code=404, detail="Email not found in the list.")
    elif operation == "remove":
        receiver_to_remove = db.query(ReceiverEmail).filter(ReceiverEmail.email == receiver.email).first()
        if receiver_to_remove:
            db.delete(receiver_to_remove)
            db.commit()
            return {"status": "success", "message": f"Email {receiver.email} removed from the receiver list."}
        else:
            raise HTTPException(status_code=404, detail="Email not found in the list.")
    else:
        raise HTTPException(status_code=400, detail="Invalid operation. Use 'add', 'edit', or 'remove'.")

# Endpoint to get the list of receiver emails
@app.get("/get_receivers/")
async def get_receivers(db: Session = Depends(get_db)):
    """Endpoint to get the list of receiver emails"""
    receivers = db.query(ReceiverEmail).all()
    return {"receiver_emails": [receiver.email for receiver in receivers]}
