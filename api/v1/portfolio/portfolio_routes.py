from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from api.v1.auth.auth_security import AuthSecurity
from api.v1.services.mongo import MongoDB
from api.v1.config import CONFIG
from api.v1.services.rapidapi_mutfund import RapidAPIService
import asyncio 

router = APIRouter()
mongo_service = MongoDB(CONFIG['MONGO_URL'])
db_name = "mfb_webapp"  # Same database used in auth
collection_name = "purchases"  # Collection for purchase data

@router.get("/portfolio")
async def get_portfolio(authorization: str = Header(None)):
    """
    Fetch the portfolio of the current user.

    Args:
        authorization (str): JWT token for user authentication.

    Returns:
        dict: A list of all mutual fund purchases by the user.
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
        user_email = current_user["email"]  # Use email as the unique identifier

        # Fetch all purchase records for the user
        purchases = await mongo_service.find_all(
            db_name,
            collection_name,
            {"email": user_email}
        )

        if not purchases:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "No purchases found for this user."}
            )

        # Convert ObjectId to string and format the response
        portfolio = [
            {
                "_id": str(purchase["_id"]),
                "email": purchase["email"],
                "Scheme_Code": purchase["Scheme_Code"],
                "Scheme_Name": purchase["Scheme_Name"],
                "Date": purchase["Date"],
                "Scheme_Category": purchase["Scheme_Category"],
                "ISIN_Div_Payout_ISIN_Growth": purchase["ISIN_Div_Payout_ISIN_Growth"],
                "ISIN_Div_Reinvestment": purchase["ISIN_Div_Reinvestment"],
                "units": purchase["units"],
                "Net_Asset_Value": purchase["Net_Asset_Value"],
                "total_cost": purchase["total_cost"],
                "purchase_date": purchase["purchase_date"].isoformat(),
                "last_updated": purchase.get("last_updated", "").isoformat() if purchase.get("last_updated") else None,
            }
            for purchase in purchases
        ]

        return {"status": "success", "portfolio": portfolio}

    except HTTPException as e:
        raise e  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Dev for UI: Testing Only
# @router.get("/portfolio/update")
# async def test_endpoint():
#     scheme_doc = await mongo_service.find_one(
#         db_name,
#         collection_name,
#         {"Scheme_Code": 119551}
#     )
#     if not scheme_doc:
#         return { "status": "error", "message": "No scheme found." }
#     result = await update_nav_and_total_cost(scheme_doc)
#     return result

async def get_all_scheme_documents():
    scheme_documents = await mongo_service.find_all(
        db_name,
        collection_name
    )
    return scheme_documents

async def update_nav_and_total_cost(scheme_document):
    scheme_code = scheme_document['Scheme_Code']
    units = scheme_document['units']

    # fetch NAV data from RapidAPI
    api_data = await RapidAPIService.fetch_oes_schemes(scheme_code)
    
    if api_data and api_data['status'] == 'success':
        latest_nav = api_data['data'][0]['Net_Asset_Value']

        # Calculate new total_cost
        new_total_cost = latest_nav * units

        # Update MongoDB

        # Check for the  purchase for this Scheme_Code
        purchase = await mongo_service.find_one(
            db_name,
            collection_name,
            {"Scheme_Code": scheme_code},
        )

        if purchase:
            # Update the purchase document
            await mongo_service.update_one(
                db_name,
                collection_name,
                {"_id": purchase["_id"]},
                {
                    "Net_Asset_Value": latest_nav, 
                    "total_cost": new_total_cost
                }
            )
            return { "status": "success", "message": "NAV and total_cost updated successfully" }
        else:
            return { "status": "error", "message": "No purchase found for this Scheme Code" }
        

async def run_hourly_updates():
    while True:
        # Get all scheme documents
        scheme_documents = await get_all_scheme_documents()
        for scheme_document in scheme_documents:
            # Sleep for 1 hour: before (more practical to not have updates on every startup)
            await asyncio.sleep(3600)
            await update_nav_and_total_cost(scheme_document)

