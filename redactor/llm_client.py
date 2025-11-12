"""
This module defines the GeminiClient class, a client for interacting with
the Google Gemini API. It handles API key management and sending prompts.

Note: This module requires the 'google-generativeai' and 'python-dotenv'
packages. Ensure they are in your requirements.txt and installed.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging
from typing import Optional

# Load API key BEFORE any Gemini API usage
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Now it's safe to call any Gemini function!
print([m.name for m in genai.list_models()])     # For debug, can be removed for production

# For the test harness demonstration
from redactor.detector import PIIDetector
from redactor.redactor import Redactor

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiClient:
    """
    A client for sending prompts to the Google Gemini Pro model.
    
    It automatically loads the API key from a .env file in the project root.
    """

    def __init__(self):
        """
        Initializes the GeminiClient.
        
        - Loads environment variables from a .env file.
        - Retrieves the GEMINI_API_KEY.
        - Configures the generative AI model.
        """
        self.model: Optional[genai.GenerativeModel] = None
        self.api_key_found: bool = False

        # Load environment variables from a .env file in the project's root
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            logging.error(
                "GEMINI_API_KEY not found in environment variables or .env file. "
                "The client will not be able to send requests."
            )
            return

        try:
            genai.configure(api_key=api_key)
            
            # Hardcode the model name for consistency in this demo.
            # 'gemini-1.5-flash-latest' is a modern, efficient model suitable for testing and free-tier usage.
            model_name = 'models/gemini-2.5-flash'
            self.model = genai.GenerativeModel(model_name)

            
            self.api_key_found = True
            logging.info(f"GeminiClient initialized successfully with hardcoded model: {model_name}")

        except Exception as e:
            logging.error(f"Failed to configure Gemini client: {e}")

    def send(self, prompt: str) -> str:
        """
        Sends a prompt to the Gemini model and returns the text response.

        Args:
            prompt: The text prompt to send to the model.

        Returns:
            The model's text response, or an error message if the request fails.
        """
        if not self.model:
            error_msg = "Cannot send prompt: GeminiClient is not initialized (check API key)."
            logging.warning(error_msg)
            return error_msg

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = f"An error occurred while sending the prompt to Gemini: {e}"
            logging.error(error_msg)
            return error_msg


if __name__ == "__main__":
    """
    Test harness to demonstrate GeminiClient functionality.
    
    This shows how to redact PII from a prompt before sending it to the LLM,
    which is a critical safety and privacy practice.
    """
    print("=" * 25 + " GeminiClient Test Harness " + "=" * 25)
    
    # --- Step 1: Initialize the client ---
    # It will automatically look for your .env file with GEMINI_API_KEY
    gemini_client = GeminiClient()

    if not gemini_client.api_key_found:
        print("\nTest harness cannot run because Gemini API key is missing.")
        print("Please create a '.env' file in your project root with:")
        print("GEMINI_API_KEY='your_key_here'")
    else:
        # --- Step 2: Demonstrate sending a prompt WITHOUT PII ---
        print("\n--- Demonstrating a simple prompt with no PII ---")
        safe_prompt = "What is the speed of light?"
        print(f"Sending prompt: '{safe_prompt}'")
        response = gemini_client.send(safe_prompt)
        print(f"\nLLM Response:\n---\n{response}\n---\n")

        # --- Step 3: Demonstrate redacting a prompt WITH PII ---
        print("\n--- Demonstrating a prompt with PII that needs redaction ---")
        
        # IMPORTANT: In a real application, never send unredacted PII to an LLM.
        # This example shows the correct, redacted workflow.
        pii_prompt = "My name is Jane Doe and I live in London. My email is jane.doe@email.com. Can you write a short email to Bucky about the meeting at 10 am?"
        
        print(f"Original prompt with PII:\n'{pii_prompt}'\n")
        
        # Use our existing tools to detect and redact PII
        pii_detector = PIIDetector()
        redactor = Redactor()
        
        # Detect entities (output is printed by the detector)
        entities = pii_detector.detect(pii_prompt)
        
        # Redact entities (output is printed by the redactor)
        redacted_prompt, mapping = redactor.redact(pii_prompt, entities)
        
        print("\n>>> Sending REDACTED prompt to Gemini... <<<")
        
        # Send the safe, redacted prompt to the LLM
        llm_response = gemini_client.send(redacted_prompt)
        
        print(f"LLM Response (to redacted prompt):\n---\n{llm_response}\n---")
        print("\nReminder: Always redact sensitive information before sending it to a third-party API.")

    print("=" * 70)