import firebase_admin
from firebase_admin import credentials

class FirebaseService:
    def __init__(self):
        try:
            # The SDK will automatically use Google Application Default Credentials
            # in a Firebase/Google Cloud environment.
            firebase_admin.initialize_app()
            print("Firebase Admin SDK initialized successfully.")
        except ValueError as e:
            # This can happen if the app is already initialized, which is fine.
            if "The default Firebase app already exists" in str(e):
                print("Firebase Admin SDK already initialized.")
            else:
                print(f"Error initializing Firebase Admin SDK: {e}")
                raise

# Singleton instance to ensure it's initialized only once
firebase_service = FirebaseService()
