# functions/auth.py

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, credentials

from functions.schemas import User

# Initialize Firebase Admin SDK.
# It will automatically use the project's service account credentials in the cloud.
# For local testing, you'd need to set the GOOGLE_APPLICATION_CREDENTIALS env var.
if not firebase_admin._apps:
    firebase_admin.initialize_app()

bearer_scheme = HTTPBearer()

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> User:
    """
    Verifies a Firebase ID token from HTTP Bearer credentials and returns the authenticated user's information.
    
    Raises:
        HTTPException: If credentials are missing or the token is invalid, with status code 401.
    
    Returns:
        User: An object containing the user's UID and email extracted from the verified token.
    """
    if not creds:
        raise HTTPException(
            status_code=401,
            detail="No authorization credentials provided."
        )
    try:
        token = creds.credentials
        decoded_token = auth.verify_id_token(token)
        return User(uid=decoded_token['uid'], email=decoded_token.get('email', ''))
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {e}"
        )