"""
BIZIT Sovereign Email Engine — powered by SendGrid
Sends real autonomous outreach emails to unclaimed business owners.
"""
import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent

logger = logging.getLogger("organism.mailer")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "organism@bizit.co")
FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "BIZIT Organism")

BASE_URL = os.getenv("BIZIT_BASE_URL", "http://localhost:3003")


def send_transactional_email(to_email: str, subject: str, html_body: str, from_name: str = None) -> bool:
    """
    Physically sends a transactional email via SendGrid. Returns True on success, False on failure.
    """
    if not SENDGRID_API_KEY:
        logger.warning("📧 [MAILER] No SendGrid API key found. Email not sent.")
        return False

    try:
        message = Mail(
            from_email=(FROM_EMAIL, from_name or FROM_NAME),
            to_emails=to_email,
            subject=subject,
            html_content=html_body
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code in (200, 202):
            logger.info(f"📧 [MAILER] ✅ Email sent to {to_email} (status {response.status_code})")
            return True
        else:
            logger.error(f"📧 [MAILER] ❌ SendGrid responded with {response.status_code}: {response.body}")
            return False

    except Exception as e:
        logger.error(f"📧 [MAILER] ❌ Failed to send email: {e}")
        return False


def send_claim_email(to_email: str, business_name: str, ghost_token: str, profile_views: int) -> bool:
    """
    Physically sends the 'claim your profile' outreach email to a business owner.
    Returns True on success, False on failure.
    """
    claim_url = f"{BASE_URL}/claim?token={ghost_token}"

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #09090B; color: #F4F4F5; margin: 0; padding: 0; }}
    .container {{ max-width: 560px; margin: 40px auto; background: #111115; border-radius: 20px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06); }}
    .header {{ background: linear-gradient(135deg, #6C3DE8, #10B981); padding: 40px; text-align: center; }}
    .header h1 {{ color: white; font-size: 28px; margin: 0; font-weight: 800; }}
    .header p {{ color: rgba(255,255,255,0.8); margin: 8px 0 0; font-size: 14px; }}
    .body {{ padding: 36px; }}
    .body p {{ color: rgba(244,244,245,0.8); font-size: 15px; line-height: 1.7; margin: 0 0 16px; }}
    .stat-box {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 20px; text-align: center; margin: 24px 0; }}
    .stat-box .number {{ font-size: 48px; font-weight: 800; color: #A78BFA; margin: 0; }}
    .stat-box .label {{ color: rgba(161,161,170,0.6); font-size: 13px; margin-top: 4px; }}
    .cta {{ display: block; background: linear-gradient(135deg, #6C3DE8, #4F46E5); color: white; text-decoration: none; text-align: center; padding: 18px 32px; border-radius: 14px; font-size: 16px; font-weight: 700; margin: 28px 0 0; }}
    .footer {{ padding: 20px 36px; border-top: 1px solid rgba(255,255,255,0.06); }}
    .footer p {{ color: rgba(161,161,170,0.4); font-size: 12px; margin: 0; text-align: center; line-height: 1.6; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🧬 BIZIT</h1>
      <p>Autonomous Business Intelligence Platform</p>
    </div>
    <div class="body">
      <p>Hi <strong>{business_name}</strong>,</p>
      <p>Our AI was scanning local business directories and noticed <strong>{business_name}</strong> isn't listed on BIZIT — so we went ahead and built a profile for you.</p>

      <div class="stat-box">
        <p class="number">{profile_views}</p>
        <p class="label">people have already viewed your profile this week</p>
      </div>

      <p>Your profile is already getting real traffic from potential customers searching in your area. Claiming it takes less than 60 seconds and is completely free.</p>
      <p>Once claimed, you'll get:</p>
      <p>✅ A verified business badge<br>📊 Real-time analytics dashboard<br>🔥 Demand alerts when customers are searching for you<br>💬 Direct leads from customers</p>

      <a href="{claim_url}" class="cta">Claim Your Free Profile →</a>
    </div>
    <div class="footer">
      <p>This profile was automatically discovered and created by the BIZIT Organism AI.<br>
      If this is not your business, you can safely ignore this email.<br>
      <a href="#" style="color: rgba(161,161,170,0.4);">Unsubscribe</a></p>
    </div>
  </div>
</body>
</html>
"""

    return send_transactional_email(
        to_email,
        subject=f"I built a free profile for {business_name} on BIZIT 🧬",
        html_body=html_body,
    )
