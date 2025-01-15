# /api/v1/auth/auth_routes.py

from fastapi import APIRouter, HTTPException, Header
from api.v1.auth.models import UserRegistrationRequest
from api.v1.services.mongo import MongoDB
from api.v1.config import CONFIG
from api.v1.auth.auth_security import AuthSecurity

auth_router = APIRouter()
mongo_service = MongoDB(CONFIG['MONGO_URL'])
db_name = "mfb_webapp"  # Same database used in auth
collection_name = "user_data"  # Collection for purchase data

@auth_router.post("/register")
async def register_user(request: UserRegistrationRequest):
    try:
        # Check if the email is already registered
        existing_user = await mongo_service.find_one(db_name, collection_name, {"email": request.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash the password (use a hashing library like bcrypt, or Argon2 here)
        hashed_password = AuthSecurity.hash_password(request.password)

        # Create the user data object
        user_data = {
            "email": request.email,
            "password": hashed_password,
            # Add any other necessary fields
        }

        # Save to the database
        await mongo_service.insert_one("mfb_webapp", "user_data", user_data)
        return {"message": "User registered successfully."}
    
    except HTTPException as http_exc:
        raise http_exc  # Re-raise HTTP exceptions (e.g., email already registered)
    
    except Exception as e:
        # Catch any general exception, e.g., MongoDB connection issues
        raise HTTPException(status_code=500, detail=f"[Is MongoDB offline?] Internal server error: {str(e)}")

@auth_router.post("/login")
async def login_user(request: UserRegistrationRequest): # Reuse the same request model to reduce redundancy
    try:
        # Check if the email is registered
        user_data = await mongo_service.find_one("mfb_webapp", "user_data", {"email": request.email})
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid email")
        
        # Verify the password
        if not AuthSecurity.verify_password(request.password, user_data['password']):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Generate JWT token
        # Debug here for JWT token generation issues (usually .env related)
        access_token =AuthSecurity.create_access_token(data={"email": request.email})

        #`user_data` contains the user document retrieved from the database which includes a sensitive field
        if "password" in user_data:
            user_data["password"] = "[REDACTED]"
        return {"message": "Login successful", "access_token": access_token, "user": user_data}
    
    except HTTPException as http_exc:
        raise http_exc  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@auth_router.get("/check_login")
async def check_login_status(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization token is missing.")
    
    # Extract the token from "Bearer <token>"
    token_prefix = "Bearer "
    if not authorization.startswith(token_prefix):
        raise HTTPException(status_code=401, detail="Invalid authorization code.")
    
    token = authorization[len(token_prefix):]  # Get the actual token

    try:
        current_user = AuthSecurity.get_current_user(token)  # Validate and decode the token
        return {"message": "Token is valid", "user": current_user}  # Return user info if valid
    except HTTPException as e:
        raise e  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
