"""
BIZIT SMS Engine.
No SMS/WhatsApp provider is connected yet. This module exists so callers have a
stable interface to send against — until AFRICASTALKING_API_KEY (or another
provider's credentials) are configured, send_sms() honestly reports that nothing
was sent rather than faking delivery.
"""
import os
import logging

logger = logging.getLogger("organism.sms")

AFRICASTALKING_API_KEY = os.getenv("AFRICASTALKING_API_KEY")
AFRICASTALKING_USERNAME = os.getenv("AFRICASTALKING_USERNAME")


def send_sms(to_phone: str, body: str) -> bool:
    """
    Sends an SMS via Africa's Talking. Returns True on success, False on failure
    (including "no provider configured" — that is not an error, it's the honest
    default until credentials are added).
    """
    if not AFRICASTALKING_API_KEY or not AFRICASTALKING_USERNAME:
        logger.warning("📱 [SMS] No SMS provider configured (AFRICASTALKING_API_KEY/AFRICASTALKING_USERNAME). SMS not sent.")
        return False

    try:
        import africastalking
        africastalking.initialize(AFRICASTALKING_USERNAME, AFRICASTALKING_API_KEY)
        sms = africastalking.SMS
        response = sms.send(body, [to_phone])
        recipients = response.get("SMSMessageData", {}).get("Recipients", [])
        ok = bool(recipients) and recipients[0].get("status") == "Success"
        if ok:
            logger.info(f"📱 [SMS] ✅ Sent to {to_phone}")
        else:
            logger.error(f"📱 [SMS] ❌ Provider rejected send to {to_phone}: {response}")
        return ok
    except Exception as e:
        logger.error(f"📱 [SMS] ❌ Failed to send SMS: {e}")
        return False
