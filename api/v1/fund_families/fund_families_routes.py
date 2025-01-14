# api/v1/fund_families/fund_families_routes.py

from fastapi import APIRouter, HTTPException, Header
from api.v1.auth.auth_security import AuthSecurity
from api.v1.config import CONFIG

router = APIRouter()

@router.get("/fund_families")
async def get_fund_families(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization token is missing.")
    
    # Extract the token from "Bearer <token>"
    token_prefix = "Bearer "
    if not authorization.startswith(token_prefix):
        raise HTTPException(status_code=401, detail="Invalid authorization code.")
    
    token = authorization[len(token_prefix):]  # Get the actual token

    try:
        current_user = AuthSecurity.get_current_user(token)
        # You can use the current_user to fetch fund families or perform user-specific actions
        return {"fund_families": [
            "HDFC",
            "ICICI",
            "SBI",
            "Union",
            "Canara"]}  # Example fund family houses
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")