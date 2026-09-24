import logging
import time
from sqlalchemy.orm import Session
from database.models import Business, CustomerInquiry, OrganismActivity, Review, Appointment
from cognitive_kernel.gemini_client import GeminiClient

gemini = GeminiClient(model_name="gemini-2.5-flash")

logger = logging.getLogger(__name__)


def _subagent_log(db: Session, business: Business, action: str, detail: str):
    """Lightweight activity logger for sub-agents (avoids circular import from worker)."""
    entry = OrganismActivity(
        timestamp=time.time(),
        cycle="SUB_AGENT",
        business_id=business.id,
        action=action,
        detail=detail,
        impact="Instant customer service provided",
        status="DONE",
        autonomous=True,
    )
    db.add(entry)
    db.commit()

logger = logging.getLogger(__name__)

async def process_inquiry_with_subagent(db: Session, inquiry: CustomerInquiry, business: Business):
    """
    Spawns an AI Sub-Agent to answer a customer inquiry on behalf of the business.
    """
    logger.info(f"[SUB-AGENT] Spawning sub-agent for '{business.name}' to answer {inquiry.customer_name}.")
    
    services = ", ".join(business.services) if business.services else "General services"
    custom_prompt = business.ai_agent_prompt or ""
    
    prompt = f"""
You are the official 24/7 AI Customer Success Agent for a business named "{business.name}".
Business Category: {business.category}
Location: {business.location}
Services Provided: {services}
Business Description: {business.description or 'No description provided.'}

Additional Instructions from the Owner:
{custom_prompt}

The following is a message from a customer named {inquiry.customer_name} ({inquiry.customer_email}):
---
"{inquiry.message}"
---

Reply to the customer professionally and warmly. 
IMPORTANT RULE: If they ask a specific question that you do not have the answer to (e.g. asking for a specific price when it's not listed above), you MUST explicitly say: 
"I am the AI assistant for {business.name}. Let me take your contact details and the owner will get back to you with an exact quote/answer."

Output valid JSON only:
{{
  "reply": "<your response back to the customer>"
}}
"""
    try:
        result = await gemini.generate_reasoning(prompt, thinking_level="TACTICAL")
        
        if "error" in result:
            reply = f"I am the AI assistant for {business.name}. I'm currently experiencing high volume. Let me take your contact details and the owner will get back to you shortly."
        else:
            reply = result.get("reply", "Thank you for reaching out. The owner will get back to you shortly.")

    except Exception as e:
        logger.error(f"[SUB-AGENT] Failed to generate reply: {e}")
        reply = f"I am the AI assistant for {business.name}. The owner will get back to you shortly."

    # Update DB
    inquiry.agent_reply = reply
    inquiry.status = "REPLIED"
    db.commit()

    # Log the Activity for the Organism
    _subagent_log(db, business,
         f"AI Agent replied to {inquiry.customer_name}",
         f"Customer asked: '{inquiry.message}'. Agent replied successfully.")
    
    logger.info(f"[SUB-AGENT] Reply sent successfully for '{business.name}'.")

async def process_review_with_subagent(db: Session, review: Review, business: Business):
    """
    Spawns an AI Sub-Agent to respond to a customer review on behalf of the business.
    """
    logger.info(f"[SUB-AGENT] Spawning sub-agent for '{business.name}' to respond to review by {review.user_name}.")
    
    custom_prompt = business.ai_agent_prompt or ""
    
    prompt = f"""
You are the official AI Customer Success Agent for "{business.name}".
Business Category: {business.category}

Additional Instructions: {custom_prompt}

A customer named {review.user_name} just left a {review.rating}-star review:
"{review.comment}"

Reply to this review on behalf of the business owner.
If it's a positive review, thank them warmly.
If it's a negative review, apologize politely and offer to make things right.
Output valid JSON only:
{{
  "reply": "<your response>"
}}
"""
    try:
        result = await gemini.generate_reasoning(prompt, thinking_level="TACTICAL")
        if "error" in result:
            reply = f"Thank you for your feedback, {review.user_name}."
        else:
            reply = result.get("reply", f"Thank you for your feedback, {review.user_name}.")
    except Exception as e:
        logger.error(f"[SUB-AGENT] Failed to generate review reply: {e}")
        reply = f"Thank you for your feedback, {review.user_name}."

    review.agent_reply = reply
    review.reply_status = "REPLIED"
    db.commit()

    _subagent_log(db, business,
         f"AI Agent replied to {review.rating}-star review",
         f"Agent generated a reply for {review.user_name}'s review.")

async def process_booking_with_subagent(db: Session, appointment: Appointment, business: Business):
    """
    Spawns an AI Sub-Agent to confirm an appointment request.
    """
    logger.info(f"[SUB-AGENT] Spawning sub-agent for '{business.name}' to confirm booking for {appointment.customer_name}.")
    
    custom_prompt = business.ai_agent_prompt or ""
    services = ", ".join(business.services) if business.services else "our services"
    
    prompt = f"""
You are the official AI Booking Agent for "{business.name}".
Services: {services}

Additional Instructions: {custom_prompt}

A customer named {appointment.customer_name} has requested an appointment:
Service: {appointment.service}
Time: {appointment.requested_time}

Confirm their appointment warmly and professionally.
Output valid JSON only:
{{
  "confirmation_message": "<your confirmation message>"
}}
"""
    try:
        result = await gemini.generate_reasoning(prompt, thinking_level="TACTICAL")
        if "error" in result:
            msg = f"Hello {appointment.customer_name}, your appointment for {appointment.service} at {appointment.requested_time} has been received. We will contact you shortly."
        else:
            msg = result.get("confirmation_message", f"Your appointment is confirmed for {appointment.requested_time}.")
    except Exception as e:
        logger.error(f"[SUB-AGENT] Failed to generate booking confirmation: {e}")
        msg = f"Your appointment is confirmed for {appointment.requested_time}."

    appointment.agent_confirmation_message = msg
    appointment.status = "CONFIRMED"
    db.commit()

    _subagent_log(db, business,
         f"AI Agent confirmed appointment",
         f"Agent confirmed {appointment.service} at {appointment.requested_time} for {appointment.customer_name}.")
