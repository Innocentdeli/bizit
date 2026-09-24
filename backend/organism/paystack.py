"""
BIZIT Payout Engine — powered by Paystack Transfers.
No payment processor was connected before this. Like mailer.py and sms.py,
every function here fails closed (returns None/False and logs a warning)
until PAYSTACK_SECRET_KEY is configured — it never fakes a successful payout.

NOTE: this has been written against Paystack's documented Transfer Recipient
and Transfer APIs but has not been exercised against a live account (no key
was available while building it). Verify against Paystack's test mode before
trusting it with real payouts.
"""
import os
import logging
from typing import Optional

import httpx

logger = logging.getLogger("organism.paystack")

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
BASE_URL = "https://api.paystack.co"


def _headers() -> dict:
    return {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}", "Content-Type": "application/json"}


async def create_transfer_recipient(name: str, account_number: str, bank_code: str) -> Optional[dict]:
    """
    Registers a contractor's bank account with Paystack ahead of paying them.
    Returns {"recipient_code": ..., "account_name": ...} on success, None if
    unconfigured or Paystack rejects the details (e.g. account number/bank
    mismatch — Paystack resolves and verifies the account name server-side).
    """
    if not PAYSTACK_SECRET_KEY:
        logger.warning("💳 [PAYSTACK] No PAYSTACK_SECRET_KEY configured. Cannot register payout account.")
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{BASE_URL}/transferrecipient",
                headers=_headers(),
                json={"type": "nuban", "name": name, "account_number": account_number,
                      "bank_code": bank_code, "currency": "NGN"},
            )
            data = resp.json()
            if resp.status_code in (200, 201) and data.get("status"):
                recipient = data["data"]
                return {"recipient_code": recipient["recipient_code"], "account_name": recipient.get("details", {}).get("account_name")}
            logger.error(f"💳 [PAYSTACK] ❌ Recipient creation rejected: {data.get('message')}")
            return None
    except Exception as e:
        logger.error(f"💳 [PAYSTACK] ❌ Recipient creation failed: {e}")
        return None


async def initiate_transfer(amount_ngn: float, recipient_code: str, reason: str) -> Optional[dict]:
    """
    Pays out amount_ngn (in Naira — converted to kobo here) to a previously
    registered recipient. Returns {"status": ..., "transfer_code": ..., "reference": ...}
    on success, None if unconfigured or the transfer request itself fails.
    A "success" response from Paystack here means the transfer was *accepted*,
    not necessarily settled — Paystack settles asynchronously and would notify
    via webhook in a fully wired integration (not set up here).
    """
    if not PAYSTACK_SECRET_KEY:
        logger.warning("💳 [PAYSTACK] No PAYSTACK_SECRET_KEY configured. Payout not sent.")
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{BASE_URL}/transfer",
                headers=_headers(),
                json={"source": "balance", "amount": round(amount_ngn * 100), "recipient": recipient_code, "reason": reason},
            )
            data = resp.json()
            if resp.status_code in (200, 201) and data.get("status"):
                transfer = data["data"]
                logger.info(f"💳 [PAYSTACK] ✅ Transfer {transfer.get('status')} for ₦{amount_ngn:,.0f} to {recipient_code}")
                return {"status": transfer.get("status"), "transfer_code": transfer.get("transfer_code"), "reference": transfer.get("reference")}
            logger.error(f"💳 [PAYSTACK] ❌ Transfer rejected: {data.get('message')}")
            return None
    except Exception as e:
        logger.error(f"💳 [PAYSTACK] ❌ Transfer failed: {e}")
        return None


async def list_banks() -> list:
    """Returns Paystack's supported bank list (code + name), used to populate a bank-select UI. Empty list if unconfigured."""
    if not PAYSTACK_SECRET_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{BASE_URL}/bank?currency=NGN", headers=_headers())
            data = resp.json()
            if resp.status_code == 200 and data.get("status"):
                return [{"name": b["name"], "code": b["code"]} for b in data["data"]]
            return []
    except Exception as e:
        logger.error(f"💳 [PAYSTACK] ❌ Bank list fetch failed: {e}")
        return []
