# functions/services/secret_service.py

import os
import google.auth
from google.cloud import secretmanager
from dotenv import load_dotenv

# Load .env variables for local development when this module is first imported
load_dotenv()

def get_secret(secret_id: str, is_local_dev: bool = not os.getenv("GOOGLE_CLOUD_PROJECT")) -> str:
    """
    Fetches a secret from Google Secret Manager in a production environment,
    or from a local .env file for development.
    
    Args:
        secret_id: The name of the secret to fetch (e.g., "PINECONE_API_KEY").
        is_local_dev: Flag to force local or production mode. Defaults to checking env var.
    
    Returns:
        The secret value as a string.
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