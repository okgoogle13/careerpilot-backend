# functions/services/vector_db_service.py

"""
This service handles all interactions with the Pinecone vector database.
It provides an abstraction layer for querying and managing vector embeddings,
which is essential for the RAG (Retrieval-Augmented Generation) capabilities
of the AI agents.
"""

# 1. Import necessary libraries and our custom secret service
import pinecone
from functions.services.secret_service import get_secret

# 2. Initialize Pinecone connection details
#    These are fetched once when the application starts up.
PINECONE_API_KEY = get_secret("PINECONE_API_KEY")
# NOTE: The Pinecone environment is usually not a secret.
# You can store this in config.py if you prefer.
PINECONE_ENVIRONMENT = "us-west1-gcp" # Replace with your Pinecone environment
PINECONE_INDEX_NAME = "career-pilot-index" # The name of your index in Pinecone


class PineconeClient:
    """A client class to encapsulate all Pinecone database operations."""
    
    def __init__(self, api_key: str, environment: str):
        """
        Initializes the Pinecone client. Raises ValueError if config is missing.
        """
        if not api_key or not environment:
            raise ValueError("Pinecone API key and environment must be set.")
        
        # Initialize the connection to Pinecone
        pinecone.init(api_key=api_key, environment=environment)
        
        self.index = None
        # Connect to the specific index if it exists
        if PINECONE_INDEX_NAME in pinecone.list_indexes():
            self.index = pinecone.Index(PINECONE_INDEX_NAME)
            print(f"Successfully connected to Pinecone index: '{PINECONE_INDEX_NAME}'")
        else:
            print(f"WARN: Pinecone index '{PINECONE_INDEX_NAME}' not found. Queries will fail.")

    def _get_embedding(self, text: str) -> list[float]:
        """
        Placeholder for converting text to a vector embedding.
        In a real application, you would use a model like 'text-embedding-ada-002'
        from OpenAI or a Google embedding model.
        """
        print(f"Generating embedding for text: '{text[:30]}...'")
        # Returning a dummy vector of the correct dimension (e.g., 1536 for ada-002)
        return [0.0] * 1536

    def query_for_context(self, query_text: str, user_id: str, top_k: int = 3) -> list[str]:
        """
        Queries the Pinecone index to retrieve the most relevant document chunks
        for a given query text and user.

        Args:
            query_text: The text to find relevant context for.
            user_id: The ID of the user to scope the search. This is used as the namespace.
            top_k: The number of top results to return.

        Returns:
            A list of strings, where each string is the text from a relevant document chunk.
        """
        if not self.index:
            print("ERROR: Cannot query because Pinecone index is not available.")
            return []

        # Convert the query text into a vector embedding
        query_embedding = self._get_embedding(query_text)

        # Perform the query against the Pinecone index
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=user_id # Use the user_id as a namespace for multi-tenancy
            )
            
            # Extract the text from the metadata of the results
            retrieved_texts = [match['metadata']['text'] for match in results['matches']]
            print(f"Retrieved {len(retrieved_texts)} contexts from Pinecone.")
            return retrieved_texts
            
        except Exception as e:
            print(f"An error occurred while querying Pinecone: {e}")
            return []


# 3. Create a single, reusable instance of the client for the entire application.
#    Your flows and other services will import this 'pinecone_client' object.
try:
    pinecone_client = PineconeClient(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
except ValueError as e:
    print(e)
    pinecone_client = None