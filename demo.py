"""
demo.py: End-to-End Demonstration of the Keystone Redactor Framework.

This script showcases the full pipeline:
1. Detect PII in a sample text.
2. Redact the text, replacing PII with placeholders.
3. Send the safe, redacted text to the Gemini LLM.
4. Receive the LLM's response (still containing placeholders).
5. Restore the original PII into the LLM's response for the end-user.

This entire process ensures that no sensitive data is ever exposed to the
third-party LLM, providing a privacy-preserving workflow.
"""

import sys
from redactor.detector import PIIDetector
from redactor.redactor import Redactor
from redactor.llm_client import GeminiClient
from redactor.restorer import Restorer

def run_demo_pipeline():
    """
    Executes the full, sequential PII redaction and restoration pipeline.
    """
    print("=" * 30)
    print("  KEYSTONE REDACTOR FRAMEWORK DEMO  ")
    print("=" * 30)
    print("This demo will walk through the full, privacy-preserving workflow.\n")

    # --- Initialize all framework components ---
    try:
        pii_detector = PIIDetector()
        redactor = Redactor()
        gemini_client = GeminiClient()
        restorer = Restorer()
    except Exception as e:
        print(f"Failed to initialize framework components: {e}")
        sys.exit(1)

    # Verify that the Gemini client is ready (API key is present)
    if not gemini_client.api_key_found:
        print("\nDemo cannot proceed: Gemini API key is missing.")
        print("Please ensure your .env file is correctly set up.")
        sys.exit(1)

    # --- (a) Define a sample text with multiple PII types ---
    # This text contains a person's name, a date, a location, an email, and a monetary value.
    original_text = (
        "Please schedule a call with Dr. Evelyn Reed for May 20, 2024. "
        "She is currently in Berlin. Her contact email is e.reed@science-corp.net. "
        "The budget for the consultation is $750."
    )
    print("--- ORIGINAL TEXT ---")
    print(f"'{original_text}'\n")

    # --- (b) Stage 1: PII Detection ---
    print("\n" + "=" * 15 + " STAGE 1: PII DETECTION " + "=" * 15)
    print("Using PIIDetector (spaCy + regex) to find sensitive data...")
    # The .detect() method prints its own detailed findings.
    detected_entities = pii_detector.detect(original_text)
    if not detected_entities:
        print("No PII was detected. Exiting demo.")
        return

    # --- (c) Stage 2: PII Redaction ---
    print("\n" + "=" * 15 + " STAGE 2: PII REDACTION " + "=" * 15)
    print("Using Redactor to replace PII with placeholders...")
    # The .redact() method prints the redacted text and the placeholder map.
    redacted_prompt, placeholder_map = redactor.redact(original_text, detected_entities)

    # --- (d) Stage 3: Secure LLM Call ---
    print("\n" + "=" * 15 + " STAGE 3: SECURE LLM CALL " + "=" * 15)
    print("Sending the SAFE, REDACTED prompt to the Gemini LLM...")
    print(f"Prompt being sent: '{redacted_prompt}'\n")
    
    # We'll ask the LLM to summarize the information it received.
    llm_task_prompt = f"Based on the following text, please summarize the key points in a bulleted list:\n\n{redacted_prompt}"
    
    llm_response = gemini_client.send(llm_task_prompt)
    
    print("--- LLM RESPONSE (contains only placeholders) ---")
    print(f"'{llm_response}'")
    print(">>> Note: The LLM never saw the original names, dates, or emails. <<<\n")

    # --- (e) Stage 4: PII Restoration ---
    print("\n" + "=" * 15 + " STAGE 4: PII RESTORATION " + "=" * 15)
    print("Using Restorer to de-redact the LLM's response...")
    # The .restore() method prints a before-and-after comparison.
    final_text = restorer.restore(llm_response, placeholder_map)

    # --- (f) Final Verification ---
    print("\n" + "=" * 15 + " DEMO COMPLETE: FINAL OUTPUT " + "=" * 15)
    print("This is the final, human-readable text after re-inserting the PII.")
    print("The original data was protected throughout the entire process.")
    print("\n--- FINAL RESTORED TEXT ---")
    print(f"'{final_text}'")
    print("=" * 55)


if __name__ == "__main__":
    try:
        run_demo_pipeline()
    except Exception as e:
        print(f"\nAn unexpected error occurred during the demo: {e}", file=sys.stderr)
        sys.exit(1)
