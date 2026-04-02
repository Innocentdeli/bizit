from fastapi import APIRouter


router = APIRouter()

EXTENSIONS = [
    {"id": "ext-1", "name": "QuickBooks Sync", "category": "Finance", "status": "INSTALLED"},
    {"id": "ext-2", "name": "Slack Notifications", "category": "Communication", "status": "AVAILABLE"},
    {"id": "ext-3", "name": "Mailchimp Integration", "category": "Marketing", "status": "AVAILABLE"}
]

@router.get("/market")
async def get_extension_market():
    """
    Module 20: Ecosystem Extensions
    List available plugins.
    """
    return {"extensions": EXTENSIONS}

@router.post("/install/{ext_id}")
async def install_extension(ext_id: str):
    """
    Module 20: Install Plugin
    """
    ext = next((e for e in EXTENSIONS if e["id"] == ext_id), None)
    if ext:
        ext["status"] = "INSTALLED"
        return {"status": "success", "message": f"Installed {ext['name']}"}
    return {"status": "error", "message": "Extension not found"}
