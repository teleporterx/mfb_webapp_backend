# api/v1/fund_families/fund_families_routes.py

import httpx
from fastapi import APIRouter, HTTPException, Header, Depends
from api.v1.auth.auth_security import AuthSecurity
from api.v1.funds.models import FundFamilyRequest
from api.v1.services.rapidapi_mutfund import RapidAPIService

router = APIRouter()

@router.get("/fund_families")
async def get_fund_families(
    authorization: str = Header(None)
    ):
    """
    Fetch all open ended schemes and filter all families using the /latest endpoint.
    """
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization token is missing.")
    
    # Extract the token from "Bearer <token>"
    token_prefix = "Bearer "
    if not authorization.startswith(token_prefix):
        raise HTTPException(status_code=401, detail="Invalid authorization code.")
    
    token = authorization[len(token_prefix):]  # Get the actual token

    try:
        current_user = AuthSecurity.get_current_user(token)
        # Fetch data from RapidAPI
        all_open_ended_schemes = await RapidAPIService.fetch_latest_open_ended_schemes()

        # Extract and filter fund families from all schemes
        # fund_families = list(set(scheme["Mutual_Fund_Family"] for scheme in all_open_ended_schemes))
        
        # Dev for UI
        fund_families = {
            "Aditya Birla Sun Life Mutual Fund",
            "Axis Mutual Fund",
            "HDFC",
            "ICICI",
            "SBI",
            "Union",
            "Canara"}  # Example fund family houses
        
        if not fund_families:
            raise HTTPException(status_code=404, detail="No fund families found!")

        return {"status": "success", "fund_families": fund_families}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/fund_schemes/latest/open_ended")
async def get_open_ended_latest_schemes(
    request: FundFamilyRequest,
    authorization: str = Header(None)
):
    """
    Filter out selected fund family and associated details.
    """
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization token is missing.")

    # Extract the token from "Bearer <token>"
    token_prefix = "Bearer "
    if not authorization.startswith(token_prefix):
        raise HTTPException(status_code=401, detail="Invalid authorization header format.")
    
    token = authorization[len(token_prefix):]  # Get the actual token

    try:
        # Validate and decode the token
        current_user = AuthSecurity.get_current_user(token)

        # Fetch data from RapidAPI
        all_schemes = await RapidAPIService.fetch_latest_ff_open_ended_schemes(request.fund_family)

        return all_schemes
    
    except HTTPException as e:
        raise e  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")