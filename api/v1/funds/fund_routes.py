# api/v1/fund_families/fund_families_routes.py

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from api.v1.auth.auth_security import AuthSecurity
from api.v1.funds.models import FundFamilyRequest, BuyRequest
from api.v1.services.rapidapi_mutfund import RapidAPIService
from api.v1.services.mongo import MongoDB
from api.v1.config import CONFIG
from datetime import datetime, timezone
import os
import json

router = APIRouter()
mongo_service = MongoDB(CONFIG['MONGO_URL'])
db_name = "mfb_webapp"  # Same database used in auth
collection_name = "purchases"  # Collection for purchase data

# For API Savings (Direct File cache instead of using Redis)
# Load fund families from the specific JSON file in the "funds" directory
FUND_FAMILIES_JSON_PATH = os.path.join(os.path.dirname(__file__), "fund_families.json")

# Read the fund families from the JSON file
with open(FUND_FAMILIES_JSON_PATH, "r") as f:
    fund_families_data = json.load(f)

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

        # Return the fund families directly from the JSON file
        return JSONResponse(
            status_code=200,
            content={"status": "success", "fund_families": fund_families_data["fund_families"]}
        )

        # Fetch data from RapidAPI
        # all_open_ended_schemes = await RapidAPIService.fetch_latest_open_ended_schemes()

        # Extract and filter fund families from all schemes
        # fund_families = list(set(scheme["Mutual_Fund_Family"] for scheme in all_open_ended_schemes))

        # Dev for UI
        # fund_families = {
        #     "Aditya Birla Sun Life Mutual Fund",
        #     "Axis Mutual Fund",
        #     "HDFC",
        #     "ICICI",
        #     "SBI",
        #     "Union",
        #     "Canara"}  # Example fund family houses
        
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

        # Dev for UI
        return {
            "status": "success",
            "data": [
                {
                    "Scheme_Code": 119551,
                    "ISIN_Div_Payout_ISIN_Growth": "INF209KA12Z1",
                    "ISIN_Div_Reinvestment": "INF209KA13Z9",
                    "Scheme_Name": "Aditya Birla Sun Life Banking & PSU Debt Fund  - DIRECT - IDCW",
                    "Net_Asset_Value": 102.5067,
                    "Date": "14-Jan-2025",
                    "Scheme_Type": "Open Ended Schemes",
                    "Scheme_Category": "Debt Scheme - Banking and PSU Fund",
                    "Mutual_Fund_Family": "Aditya Birla Sun Life Mutual Fund"
                },
                {
                    "Scheme_Code": 119552,
                    "ISIN_Div_Payout_ISIN_Growth": "INF209K01YM2",
                    "ISIN_Div_Reinvestment": "-",
                    "Scheme_Name": "Aditya Birla Sun Life Banking & PSU Debt Fund  - DIRECT - MONTHLY IDCW",
                    "Net_Asset_Value": 115.5344,
                    "Date": "14-Jan-2025",
                    "Scheme_Type": "Open Ended Schemes",
                    "Scheme_Category": "Debt Scheme - Banking and PSU Fund",
                    "Mutual_Fund_Family": "Aditya Birla Sun Life Mutual Fund"
                }
                ]
            }
        return {"status": "success", "data": all_schemes}
    
    except HTTPException as e:
        raise e  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/buy")
async def buy_fund(
    request: BuyRequest,
    authorization: str = Header(None)  
):
    """
    Endpoint to simulate the purchase of mutual fund units.

    Args:
        request (BuyRequest): Request body containing Scheme_Code and units.
        authorization (str): JWT token for user authentication.

    Returns:
        dict: Confirmation of the simulated purchase or an error message.
    """
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization token is missing.")

    # Extract the token from "Bearer <token>"
    token_prefix = "Bearer "
    if not authorization.startswith(token_prefix):
        raise HTTPException(status_code=401, detail="Invalid authorization header format.")
    
    token = authorization[len(token_prefix):]  # Get the actual token
    try:
        current_user = AuthSecurity.get_current_user(token)
        user_email = current_user["email"]  # Use email as the unique identifier
        scheme_code = request.Scheme_Code
        scheme_name = request.Scheme_Name
        date = request.Date
        scheme_category = request.Scheme_Category
        units = request.units
        nav = request.nav
        isig = request.ISIN_Div_Payout_ISIN_Growth 
        isir = request.ISIN_Div_Reinvestment

        if units <= 0:
            raise HTTPException(status_code=400, detail="Units must be greater than 0.")

        if nav <= 0:
            raise HTTPException(status_code=400, detail="NAV must be greater than 0.")

        # Calculate total cost
        total_cost = nav * units

        # Check if the user already has a purchase for this Scheme_Code
        existing_purchase = await mongo_service.find_one(
            db_name,
            collection_name,
            {"email": user_email, "Scheme_Code": scheme_code}
        )

        if existing_purchase:
            # Update the existing purchase
            updated_units = existing_purchase["units"] + units
            updated_total_cost = updated_units * nav  # Recalculate total cost
            await mongo_service.update_one(
                db_name,
                collection_name,
                {"_id": existing_purchase["_id"]},
                {
                    "units": updated_units,
                    "total_cost": updated_total_cost,
                    "last_updated": datetime.now(timezone.utc)
                }
            )
            action = "updated"
        else:
            # Create a new purchase record
            new_purchase = {
                "email": user_email,
                "Scheme_Code": scheme_code,
                "Scheme_Name": scheme_name,
                "Date": date,
                "Scheme_Category": scheme_category,
                "units": units,
                "Net_Asset_Value": nav,
                "ISIN_Div_Payout_ISIN_Growth": isig,
                "ISIN_Div_Reinvestment": isir,
                "total_cost": total_cost,
                "purchase_date": datetime.now(timezone.utc)
            }
            await mongo_service.insert_one(db_name, collection_name, new_purchase)
            action = "created"
            
        # Respond with success
        return {
            "status": "success",
            "message": f"Purchase {action} successfully.",
            "Scheme_Code": scheme_code,
            "units": units,
            "total_cost": f"{total_cost:.2f}",
        }

    except HTTPException as e:
        raise e  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
