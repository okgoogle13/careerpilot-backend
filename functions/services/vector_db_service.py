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
        Initialize a Pinecone client connection using the provided API key and environment.
        
        Raises:
            ValueError: If the API key or environment is not provided.
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
        Generate a dummy vector embedding for the given text.
        
        This placeholder method returns a zero vector of length 1536, simulating the output of a real embedding model.
        """
        print(f"Generating embedding for text: '{text[:30]}...'")
        # Returning a dummy vector of the correct dimension (e.g., 1536 for ada-002)
        return [0.0] * 1536

    def query_for_context(self, query_text: str, user_id: str, top_k: int = 3) -> list[str]:
        """
        Retrieve the most relevant document chunks from the Pinecone index for a given query and user.
        
        Parameters:
            query_text (str): The input text to search for relevant context.
            user_id (str): The user identifier used as the namespace for scoping the search.
            top_k (int, optional): The maximum number of relevant results to return. Defaults to 3.
        
        Returns:
            list[str]: A list of text snippets from the most relevant document chunks, or an empty list if no results are found or an error occurs.
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