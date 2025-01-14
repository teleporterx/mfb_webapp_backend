# /api/v1/auth/auth_routes.py

from fastapi import APIRouter, HTTPException
from api.v1.auth.models import UserRegistrationRequest
from api.v1.services.mongo import MongoDB
from api.v1.config import CONFIG
from api.v1.auth.auth_security import AuthSecurity

auth_router = APIRouter()
mongo_service = MongoDB(CONFIG['MONGO_URL'])

@auth_router.post("/register")
async def register_user(request: UserRegistrationRequest):
    try:
        # Check if the email is already registered
        existing_user = await mongo_service.find_one("mfb_webapp", "user_data", {"email": request.email})
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
