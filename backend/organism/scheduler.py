"""
BIZIT Organism Scheduler
========================
Registers all autonomous cycles with APScheduler.
The Organism runs continuously in the background as long as the
FastAPI server is alive.

Schedule:
  • ENRICH + VERIFY  → every 10 minutes  (keeps profiles fresh)
  • DEMAND           → every 5 minutes   (near real-time trend detection)
  • OUTREACH + AUDIT → every 30 minutes  (strategic cadence)
  • CRAWL            → every 60 minutes  (ghost listing discovery)
  • FULL cycle       → every hour        (comprehensive sweep)
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from organism.worker import (
    run_organism_cycle_sync,
    run_enrich_cycle,
    run_verify_cycle,
    run_demand_cycle,
    run_outreach_cycle,
    run_audit_cycle,
    run_crawl_cycle,
)
from organism.social_manager import run_social_cycle
from organism.project_monitor import run_project_stage_monitor
import asyncio

logger = logging.getLogger("organism.scheduler")

scheduler = BackgroundScheduler()


def _async_wrap(coro_fn):
    """Wrap an async function for synchronous APScheduler execution."""
    def wrapper():
        asyncio.run(coro_fn())
    return wrapper


def start_organism():
    """
    Initialise and start the Organism background scheduler.
    Called once on FastAPI startup.
    """
    if scheduler.running:
        logger.warning("[SCHEDULER] Already running, skipping start.")
        return

    # ── Near real-time: Demand signals every 5 min ──
    scheduler.add_job(
        _async_wrap(run_demand_cycle),
        trigger=IntervalTrigger(minutes=5),
        id="demand_cycle",
        name="Demand Signal Monitor",
        replace_existing=True,
    )

    # ── Regular cadence: Enrich every 10 min ──
    scheduler.add_job(
        _async_wrap(run_enrich_cycle),
        trigger=IntervalTrigger(minutes=10),
        id="enrich_cycle",
        name="Profile Auto-Enricher",
        replace_existing=True,
    )

    # ── Regular cadence: Verification every 15 min ──
    scheduler.add_job(
        _async_wrap(run_verify_cycle),
        trigger=IntervalTrigger(minutes=15),
        id="verify_cycle",
        name="Auto-Verification Engine",
        replace_existing=True,
    )

    # ── Strategic cadence: Outreach every 30 min ──
    scheduler.add_job(
        _async_wrap(run_outreach_cycle),
        trigger=IntervalTrigger(minutes=30),
        id="outreach_cycle",
        name="Proactive Outreach Engine",
        replace_existing=True,
    )

    # ── Full sweep: Audit every 30 min ──
    scheduler.add_job(
        _async_wrap(run_audit_cycle),
        trigger=IntervalTrigger(minutes=30),
        id="audit_cycle",
        name="Platform Health Audit",
        replace_existing=True,
    )

    # ── Expansion sweep: Crawl every 60 min ──
    scheduler.add_job(
        _async_wrap(run_crawl_cycle),
        trigger=IntervalTrigger(minutes=60),
        id="crawl_cycle",
        name="Ghost Listing Crawler",
        replace_existing=True,
    )

    # ── Promotional sweep: Social every 4 hours ──
    scheduler.add_job(
        _async_wrap(run_social_cycle),
        trigger=IntervalTrigger(hours=4),
        id="social_cycle",
        name="Social Media Manager",
        replace_existing=True,
    )

    # ── Marketing OS orchestrator: advance project stages + auto-dispatch every 10 min ──
    scheduler.add_job(
        _async_wrap(run_project_stage_monitor),
        trigger=IntervalTrigger(minutes=10),
        id="marketing_os_monitor",
        name="Marketing OS Project Stage Monitor",
        replace_existing=True,
    )

    # ── Immediate boot cycle: run everything NOW on startup ──
    scheduler.add_job(
        run_organism_cycle_sync,
        id="boot_cycle",
        name="Boot Cycle (Immediate)",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("✅ BIZIT Organism is ALIVE. Autonomous cycles active.")


def stop_organism():
    """Graceful shutdown — called on FastAPI shutdown."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("🛑 Organism scheduler stopped.")


def get_scheduler_status():
    """Return current scheduler status for the API."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else "immediate",
        })
    return {
        "running": scheduler.running,
        "jobs": jobs,
        "job_count": len(jobs),
    }
