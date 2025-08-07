# functions/services/ai_service.py

"""
This service acts as a dedicated client for interacting with the Perplexity API.
It encapsulates all the logic for making API calls to Perplexity, serving as
the 'companyDeepDive' tool for our AI agents.
"""

# 1. Import our custom secret service to securely fetch the API key.
from functions.services.secret_service import get_secret

# 2. Fetch the API key when the application starts.
#    If the key is not found, the get_secret function will raise an error,
#    preventing the application from starting in an invalid state.
PERPLEXITY_API_KEY = get_secret("PERPLEXITY_API_KEY")


class PerplexityClient:
    """A client class to encapsulate all Perplexity API operations."""
    
    def __init__(self, api_key: str):
        """
        Initializes the Perplexity client.
        
        Args:
            api_key: The API key for authenticating with the Perplexity API.
        
        Raises:
            ValueError: If the API key is not provided.
        """
        if not api_key:
            raise ValueError("Perplexity API key is missing. The ai_service cannot be initialized.")
        
        self.api_key = api_key
        # In a real application, you might initialize a session object here.
        # e.g., self.session = requests.Session()
        # self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        
        print("PerplexityClient initialized successfully.")

    def company_deep_dive(self, company_name: str) -> dict:
        """
        Performs an in-depth search on a company using the Perplexity API.
        This method acts as a "tool" for our Genkit agents.

        NOTE: This is a MOCK implementation. To enable this feature, you must
        provide a valid PERPLEXITY_API_KEY and implement the API call below.
        """
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! WARNING: Using mock data for Perplexity API call.       !!!")
        print("!!! To implement, provide a PERPLEXITY_API_KEY and          !!!")
        print("!!! implement the API call in ai_service.py.                !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"MOCK-CALL: Performing deep dive for company: '{company_name}'...")
        
        # This is a placeholder for the actual API call.
        response_data = {
            "name": company_name,
            "culture": "Reported to have a highly collaborative and innovative environment with a strong focus on professional development.",
            "recent_news": "Recently secured Series B funding to expand their NDIS support services in Western Australia.",
            "values": ["Client-First", "Integrity", "Community Impact", "Excellence"]
        }
        
        return response_data


# 3. Create a single, reusable instance of the client for the entire application.
#    Your flows and other services will import this 'perplexity_client' object.
#    This pattern is called a "singleton" and is very efficient.
try:
    perplexity_client = PerplexityClient(api_key=PERPLEXITY_API_KEY)
except ValueError as e:
    # If the client fails to initialize (e.g., missing API key),
    # log the error and set the client to None.
    print(f"FATAL ERROR: Failed to initialize PerplexityClient: {e}")
    perplexity_client = None