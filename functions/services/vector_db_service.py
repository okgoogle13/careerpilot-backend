# functions/services/vector_db_service.py

"""
This service handles all interactions with the Pinecone vector database.
It provides an abstraction layer for querying and managing vector embeddings,
which is essential for the RAG (Retrieval-Augmented Generation) capabilities
of the AI agents.
"""

# 1. Import necessary libraries and our custom secret service
import pinecone
import genkit
from functions.services.secret_service import get_secret

# 2. Initialize Pinecone connection details
PINECONE_API_KEY = get_secret("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = "us-west1-gcp"
PINECONE_INDEX_NAME = "career-pilot-index"


class PineconeClient:
    """A client class to encapsulate all Pinecone database operations."""
    
    def __init__(self, api_key: str, environment: str):
        """
        Initializes the Pinecone client. Raises ValueError if config is missing.
        """
        if not api_key or not environment:
            raise ValueError("Pinecone API key and environment must be set.")
        
        pinecone.init(api_key=api_key, environment=environment)
        
        self.index = None
        if PINECONE_INDEX_NAME in pinecone.list_indexes():
            self.index = pinecone.Index(PINECONE_INDEX_NAME)
            print(f"Successfully connected to Pinecone index: '{PINECONE_INDEX_NAME}'")
        else:
            print(f"WARN: Pinecone index '{PINECONE_INDEX_NAME}' not found. Queries will fail.")

    async def _get_embedding(self, text: str) -> list[float]:
        """
        Converts text to a vector embedding using a Genkit embedder.
        """
        print(f"Generating embedding for text: '{text[:30]}...'")
        # Assumes a Google embedding model is configured in the environment.
        embedder = genkit.get_embedder("text-embedding-004")
        result = await embedder.embed(text)
        return result

    async def query_for_context(self, query_text: str, user_id: str, top_k: int = 3) -> list[str]:
        """
        Queries the Pinecone index asynchronously to retrieve relevant document chunks.
        """
        if not self.index:
            print("ERROR: Cannot query because Pinecone index is not available.")
            return []

        print("Generating query embedding...")
        query_embedding = await self._get_embedding(query_text)

        print(f"Querying Pinecone index '{PINECONE_INDEX_NAME}'...")
        try:
            # Note: The Pinecone client library's query method is synchronous.
            # In a high-throughput production app, you might run this in a thread pool.
            # For Firebase Cloud Functions, this is generally acceptable.
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=user_id
            )
            
            retrieved_texts = [match['metadata']['text'] for match in results['matches']]
            print(f"Retrieved {len(retrieved_texts)} contexts from Pinecone for user {user_id}.")
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