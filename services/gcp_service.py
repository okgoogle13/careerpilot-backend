import os
from google.cloud import secretmanager

class GCPService:
    def __init__(self):
        self.project_id = os.getenv("GCLOUD_PROJECT")
        if not self.project_id:
            raise ValueError("GCLOUD_PROJECT environment variable not set.")
        self.client = secretmanager.SecretManagerServiceClient()

    def get_secret(self, secret_id: str) -> str:
        """
        Retrieves a secret from Google Cloud Secret Manager.
        """
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Error retrieving secret '{secret_id}': {e}")
            raise

# Singleton instance
gcp_service = GCPService()
