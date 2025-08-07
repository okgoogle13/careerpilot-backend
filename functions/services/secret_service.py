# functions/services/secret_service.py

import os
import google.auth
from google.cloud import secretmanager
from dotenv import load_dotenv

# Load .env variables for local development when this module is first imported
load_dotenv()

def get_secret(secret_id: str, is_local_dev: bool = not os.getenv("GOOGLE_CLOUD_PROJECT")) -> str:
    """
    Retrieve a secret value from Google Secret Manager in production or from a local `.env` file during development.
    
    Parameters:
        secret_id (str): The identifier of the secret to retrieve.
    
    Returns:
        str: The secret value as a string.
    
    Raises:
        Exception: If retrieval from Google Secret Manager fails in production.
        ValueError: If the local secret is not found in the `.env` file during development.
    
    In production, the function fetches the latest version of the specified secret from Google Secret Manager using the current project credentials. In local development, it retrieves the secret from environment variables loaded from a `.env` file, expecting the variable name to be the secret ID suffixed with `_LOCAL`.
    """
    if not is_local_dev:
        # Production environment: Fetch from Google Secret Manager
        try:
            _, project_id = google.auth.default()
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"FATAL: Could not access GCP secret '{secret_id}'. Error: {e}")
            raise  # Re-raise the exception to stop the application
    else:
        # Local development: Fetch from .env file
        # Assumes local secrets are named like "PINECONE_API_KEY_LOCAL"
        local_secret_name = f"{secret_id}_LOCAL"
        secret_val = os.getenv(local_secret_name)
        if not secret_val:
            print(f"FATAL: Local secret '{local_secret_name}' not found in .env file.")
            raise ValueError(f"Missing local secret: {local_secret_name}")
        return secret_val