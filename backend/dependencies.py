from fastapi import Header, HTTPException

async def get_current_user(x_api_key: str = Header(None)):
    """
    Module 19: Security & Trust
    Stub for authentication. In real app, verifies JWT tokens.
    """
    if x_api_key == "secret_admin_key":
        return {"id": "u1", "role": "SUPER_ADMIN"}
    return {"id": "u_guest", "role": "GUEST"}

def require_role(role: str):
    def dependency(user: dict = None): # In real app, user injected by Depends(get_current_user)
        # Mock logic
        return True
    return dependency
