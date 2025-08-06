import os
import time
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

# Use the standard GCLOUD_PROJECT environment variable for the Google Cloud Project ID.
GCLOUD_PROJECT = os.getenv("GCLOUD_PROJECT")
ALGORITHMS = ["RS256"]
AUTH_URL = f"https://securetoken.google.com/{GCLOUD_PROJECT}"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
_public_keys_cache = {}

def get_public_keys():
    global _public_keys_cache
    if not _public_keys_cache or _public_keys_cache.get("expires", 0) < time.time():
        try:
            response = requests.get(f"https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com")
            response.raise_for_status()
            keys = response.json()
            max_age = int(response.headers['Cache-Control'].split('=')[1])
            keys['expires'] = time.time() + max_age
            _public_keys_cache = keys
        except requests.RequestException as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Could not fetch Google's public keys: {e}")
    return _public_keys_cache

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not GCLOUD_PROJECT:
        raise HTTPException(status_code=500, detail="GCLOUD_PROJECT is not configured on the server.")
    
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        unverified_header = jwt.get_unverified_header(token)
        public_keys = get_public_keys()
        if unverified_header["kid"] not in public_keys:
            raise credentials_exception
        key = public_keys[unverified_header["kid"]]
        payload = jwt.decode(token, key, algorithms=ALGORITHMS, audience=GCLOUD_PROJECT, issuer=AUTH_URL)
        return payload
    except JWTError:
        raise credentials_exception
    except Exception as e:
        print(f"An unexpected error occurred during token validation: {e}")
        raise credentials_exception
