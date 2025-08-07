# functions/services/firebase_service.py

"""
This service manages all interactions with Google Cloud Firestore.
It handles initializing the Firebase Admin SDK and provides methods
for database operations like saving and retrieving document metadata.
"""

# 1. Import necessary libraries
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 2. Initialize the Firebase Admin SDK
# The 'if not firebase_admin._apps:' check is a crucial best practice.
# It prevents the SDK from being re-initialized on every "warm" invocation
# of the Cloud Function, which would cause errors.
if not firebase_admin._apps:
    # In the cloud, this initializes with default credentials.
    # For local development, you must set the GOOGLE_APPLICATION_CREDENTIALS
    # environment variable to point to your service account key file.
    firebase_admin.initialize_app()

# 3. Get a client instance for the Firestore database
# This object will be used for all our database operations.
db = firestore.client()


class FirebaseService:
    """A client class to encapsulate all Firestore database operations."""

    def save_document_metadata(self, user_id: str, document_data: dict) -> str:
        """
        Save metadata for a generated document under a user's 'documents' subcollection in Firestore.
        
        Adds a UTC timestamp to the metadata and stores it as a new document with an auto-generated ID.
        
        Parameters:
            user_id (str): The unique identifier of the user.
            document_data (dict): Metadata to associate with the document.
        
        Returns:
            str: The Firestore ID of the newly created document.
        
        Raises:
            Exception: If the document could not be saved to Firestore.
        """
        try:
            # Create a reference to a new document in the user's 'documents' subcollection.
            # Firestore will automatically generate a unique ID for this document.
            doc_ref = db.collection('users').document(user_id).collection('documents').document()
            
            # Add a server-side timestamp to the data
            document_data['created_at'] = datetime.utcnow()
            
            # Set the data for the new document
            doc_ref.set(document_data)
            
            print(f"Successfully saved document metadata for user '{user_id}' with doc ID '{doc_ref.id}'")
            return doc_ref.id
        except Exception as e:
            print(f"FATAL ERROR: Could not save document metadata for user '{user_id}'. Error: {e}")
            raise

    def get_user_documents(self, user_id: str) -> list[dict]:
        """
        Retrieve all document metadata for a given user from their Firestore `documents` subcollection.
        
        Parameters:
            user_id (str): The unique identifier of the user whose documents are to be retrieved.
        
        Returns:
            list[dict]: A list of dictionaries containing each document's metadata, including the document ID under the key 'id'. Returns an empty list if retrieval fails.
        """
        try:
            docs_ref = db.collection('users').document(user_id).collection('documents')
            docs = docs_ref.stream() # stream() returns an iterator of DocumentSnapshot
            
            document_list = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id # Add the document ID to the dictionary
                document_list.append(doc_data)
                
            print(f"Retrieved {len(document_list)} documents for user '{user_id}'")
            return document_list
        except Exception as e:
            print(f"ERROR: Could not retrieve documents for user '{user_id}'. Error: {e}")
            return []

# Create a single, reusable instance of the service for the entire application.
firebase_service = FirebaseService()