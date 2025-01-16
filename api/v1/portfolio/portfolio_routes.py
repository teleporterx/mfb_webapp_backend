from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from api.v1.auth.auth_security import AuthSecurity
from api.v1.services.mongo import MongoDB
from api.v1.config import CONFIG
from api.v1.services.rapidapi_mutfund import RapidAPIService

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

# @router.post()
