from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
import time
from datetime import datetime

from database.database import get_db, SessionLocal
from database.models import Business, Appointment
from organism.sub_agent import process_booking_with_subagent

router = APIRouter(prefix="/business", tags=["Appointments"])

class AppointmentCreate(BaseModel):
    customer_name: str
    customer_email: str
    requested_time: str
    service: str

def _serialize_appointment(a: Appointment) -> dict:
    return {
        "id": a.id,
        "business_id": a.business_id,
        "customer_name": a.customer_name,
        "customer_email": a.customer_email,
        "requested_time": a.requested_time,
        "service": a.service,
        "agent_confirmation_message": a.agent_confirmation_message,
        "status": a.status or "PENDING",
        "timestamp": a.timestamp,
        "timestamp_formatted": datetime.fromtimestamp(a.timestamp).strftime("%b %d, %Y · %I:%M %p") if a.timestamp else None,
    }

def _run_booking_subagent_bg(appointment_id: int, business_id: str):
    import asyncio
    db = SessionLocal()
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        business = db.query(Business).filter(Business.id == business_id).first()
        if appointment and business:
            asyncio.run(process_booking_with_subagent(db, appointment, business))
    except Exception as e:
        db.rollback()
    finally:
        db.close()

@router.get("/{business_id}/appointments")
def get_appointments(business_id: str, db: Session = Depends(get_db)):
    appointments = (
        db.query(Appointment)
        .filter(Appointment.business_id == business_id)
        .order_by(Appointment.timestamp.desc())
        .all()
    )
    return {
        "status": "success",
        "count": len(appointments),
        "appointments": [_serialize_appointment(a) for a in appointments]
    }

@router.post("/{business_id}/book")
def book_appointment(
    business_id: str,
    appointment_data: AppointmentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    appointment = Appointment(
        business_id=business_id,
        customer_name=appointment_data.customer_name,
        customer_email=appointment_data.customer_email,
        requested_time=appointment_data.requested_time,
        service=appointment_data.service,
        timestamp=time.time()
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    if business.ai_agent_enabled:
        background_tasks.add_task(_run_booking_subagent_bg, appointment.id, business.id)
        return {
            "status": "success",
            "message": "Booking received. AI Agent is confirming your appointment.",
            "appointment_id": appointment.id,
            "agent_active": True
        }

    return {
        "status": "success",
        "message": "Booking request submitted to the business.",
        "appointment_id": appointment.id,
        "agent_active": False
    }

@router.patch("/{business_id}/appointments/{appointment_id}")
def update_appointment_status(
    business_id: str,
    appointment_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Allow business owner to confirm, cancel or reschedule an appointment."""
    appt = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.business_id == business_id
    ).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    new_status = data.get("status")
    if new_status and new_status in ("CONFIRMED", "CANCELLED", "PENDING"):
        appt.status = new_status
    if "agent_confirmation_message" in data:
        appt.agent_confirmation_message = data["agent_confirmation_message"]

    db.commit()
    db.refresh(appt)
    return {"status": "success", "appointment": _serialize_appointment(appt)}
