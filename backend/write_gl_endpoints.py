import os

APPEND = r'''

# ?? AUTO-ENQUEUE (called by Organism worker autonomously) ?????????????????????

class AutoEnqueueRequest(BaseModel):
    business_id: str
    surge_term: str
    pct_change: float
    category: Optional[str] = "General"
    email_subject: str = ""
    email_body: str = ""
    whatsapp_body: str = ""
    source: str = "organism_auto"

@router.post("/auto-enqueue")
def auto_enqueue_growth_loop(req: AutoEnqueueRequest, db: Session = Depends(get_db)):
    """
    Called internally by the Organism when it autonomously detects a surge.
    Writes a GROWTH_LOOP activity with status=pending_review so the Execution Hub
    can surface it as a 1-click dispatch item ? no user action required to get here.
    """
    biz = db.query(Business).filter(Business.id == req.business_id).first()
    business_name = biz.name if biz else "Business"

    run_id = "auto_{}".format(uuid.uuid4().hex[:10])
    db.add(OrganismActivity(
        timestamp=time.time(),
        cycle="GROWTH_LOOP",
        business_id=req.business_id,
        business_name=business_name,
        action="[AUTO] Growth Loop Ready: {} +{:.0f}%".format(req.surge_term, req.pct_change),
        detail=(
            "Category: {} | Email: '{}' | WhatsApp drafted. "
            "Source: Organism autonomous trigger. Status: pending_review. "
            "Run ID: {}".format(req.category, req.email_subject[:60], run_id)
        ),
        impact="Auto-queued for {}: {} surge campaign".format(business_name, req.surge_term),
        status="pending_review",
        autonomous=True,
    ))
    db.commit()
    return {"run_id": run_id, "status": "pending_review", "business": business_name}


@router.get("/auto-queue-status")
def get_auto_queue_status(db: Session = Depends(get_db)):
    """
    Returns the count of autonomously queued growth loops pending dispatch.
    Used by the Execution Hub badge to show real-time pending count.
    """
    pending = (db.query(OrganismActivity)
               .filter(
                   OrganismActivity.cycle == "GROWTH_LOOP",
                   OrganismActivity.status == "pending_review"
               )
               .order_by(desc(OrganismActivity.timestamp))
               .limit(50)
               .all())

    return {
        "pending_count": len(pending),
        "items": [
            {
                "id": a.id,
                "timestamp": a.timestamp,
                "action": a.action,
                "detail": a.detail,
                "impact": a.impact,
                "business_name": a.business_name,
            }
            for a in pending
        ]
    }
'''

with open(r'routers\growth_loop.py', 'a', encoding='utf-8', newline='\n') as f:
    f.write(APPEND)
print('growth_loop.py updated with auto-enqueue + auto-queue-status endpoints')
