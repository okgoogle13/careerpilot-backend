import os
import uuid
import google.generativeai as genai
from pinecone import Pinecone
from services.gcp_service import gcp_service
import config

class VectorDBService:
    def __init__(self):
        """
        Initializes the Vector Database Service, setting up connections to
        Google Generative AI for embeddings and Pinecone for vector storage.
        """
        print("Initializing VectorDBService...")
        # Initialize Google Generative AI
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            try:
                print("Fetching GOOGLE_API_KEY from Secret Manager...")
                google_api_key = gcp_service.get_secret("GOOGLE_API_KEY")
            except Exception as e:
                raise ValueError("GOOGLE_API_KEY not found in environment variables or Secret Manager.") from e
        genai.configure(api_key=google_api_key)

        self.embedder = config.EMBEDDER_MODEL

        # Initialize Pinecone
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            try:
                print("Fetching PINECONE_API_KEY from Secret Manager...")
                pinecone_api_key = gcp_service.get_secret("PINECONE_API_KEY")
            except Exception as e:
                raise ValueError("PINECONE_API_KEY not found in environment variables or Secret Manager.") from e

        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index_name = config.PINECONE_INDEX_NAME

        if self.index_name not in self.pc.list_indexes().names():
             raise EnvironmentError(f"Pinecone index '{self.index_name}' does not exist.")

        self.index = self.pc.Index(self.index_name)
        print("VectorDBService initialized successfully.")

    def upsert(self, chunks: list[str], user_id: str, source: str) -> None:
        """
        Embeds text chunks and upserts them into the Pinecone index.
        """
        if not chunks:
            return

        print(f"Embedding and upserting {len(chunks)} chunks from '{source}' for user '{user_id}'...")
        try:
            response = genai.embed_content(model=self.embedder, content=chunks, task_type="retrieval_document")
            embeddings = response['embedding']

            vectors = [
                {
                    "id": str(uuid.uuid4()),
                    "values": embeddings[i],
                    "metadata": {"text": chunk, "user_id": user_id, "source": source}
                }
                for i, chunk in enumerate(chunks)
            ]

            self.index.upsert(vectors=vectors)
            print(f"Upsert of {len(vectors)} vectors complete.")
        except Exception as e:
            print(f"An error occurred during upsert: {e}")
            raise

    def retrieve(self, query: str, user_id: str, k: int = 5) -> list[dict]:
        """
        Embeds a query and retrieves the top k most relevant documents for a specific user.
        """
        print(f"Retrieving documents for query: '{query}' for user '{user_id}'...")
        try:
            response = genai.embed_content(model=self.embedder, content=[query], task_type="retrieval_query")
            query_embedding = response['embedding'][0]

            results = self.index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True,
                filter={"user_id": {"$eq": user_id}}
            )

            documents = [
                {"text": match.get('metadata', {}).get('text', ''), "score": match.get('score', 0)}
                for match in results.get('matches', [])
            ]

            print(f"Retrieved {len(documents)} documents.")
            return documents
        except Exception as e:
            print(f"An error occurred during retrieval: {e}")
            raise

# Singleton instance
vector_db_service = VectorDBService()
