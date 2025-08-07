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
        Initialize a PerplexityClient instance with the provided API key.
        
        Raises:
            ValueError: If the API key is missing or empty.
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
        Retrieve structured insights about a specified company, including culture, recent news, and values.
        
        Parameters:
            company_name (str): The name of the company to research.
        
        Returns:
            dict: A dictionary containing detailed information about the company.
        """
        print(f"Performing deep dive for company: '{company_name}' using Perplexity API...")
        
        # This is a placeholder for the actual API call.
        # In a real implementation, you would use a library like 'requests'
        # to make a POST request to the Perplexity API endpoint with your prompt.
        
        # Example placeholder response:
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