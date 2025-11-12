"""
This module defines the Restorer class, which is responsible for the final,
critical step in the privacy-preserving workflow: de-redaction.

It takes the placeholder-filled output from an LLM and restores the original,
sensitive data, ensuring that the PII was never exposed to the third-party
LLM service.
"""

import logging
from typing import Dict

# Configure basic logging for informational output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Restorer:
    """
    Handles the 'de-redaction' process by re-inserting original PII values
    into an LLM's output using a secure placeholder map.

    Privacy-Critical Explanation:
    This class performs the final step in a secure, privacy-first LLM workflow.
    The core principle is that sensitive data (PII) is processed in three stages:
    1. REDACT: PII is identified and replaced with non-sensitive placeholders
       before leaving the secure environment.
    2. PROCESS: The redacted, safe prompt is sent to a third-party LLM for processing.
       The LLM *never* sees the original PII.
    3. RESTORE: The LLM's response, which contains the same placeholders, is
       returned to the secure environment. This 'Restorer' class then uses the
       original placeholder map to safely re-insert the PII.

    This ensures that the end-user receives a complete, coherent text while
    maintaining compliance with regulations like GDPR, as sensitive data
    never leaves the trusted system boundary.
    """

    def restore(self, llm_output: str, placeholder_map: Dict[str, str]) -> str:
        """
        Replaces all placeholder instances in the LLM's output text with their
        original values from the provided map.

        Args:
            llm_output: The text string received from the LLM, potentially
                        containing placeholders like [PERSON_A].
            placeholder_map: A dictionary mapping placeholders to their original
                             sensitive values (e.g., {'[PERSON_A]': 'Jane Doe'}).

        Returns:
            The fully restored text with the original PII re-inserted.
        """
        logging.info("Starting restoration process...")
        print("-" * 25 + " Restoration Analysis " + "-" * 25)
        print(f"Before Restoration (LLM Output):\n'{llm_output}'\n")

        restored_text = llm_output

        # Iterate through the map and replace each placeholder with its original value.
        # This approach is simple and effective for our placeholder format.
        # Edge Case Consideration: If a placeholder's value contained another
        # placeholder key (e.g., map = {'[A]': 'B', '[B]': 'C'}), the order of
        # replacement would matter. However, our redactor generates maps from
        # original text, making this scenario virtually impossible. A simple iteration
        # is therefore safe and clean.
        for placeholder, original_value in placeholder_map.items():
            if placeholder in restored_text:
                logging.info(f"Restoring '{placeholder}' -> '{original_value}'")
                restored_text = restored_text.replace(placeholder, original_value)
            else:
                # This handles cases where the LLM might have omitted a placeholder.
                # It's a graceful failure, as no action is needed.
                logging.warning(
                    f"Placeholder '{placeholder}' from map was not found in the LLM output. Ignoring."
                )
        
        print(f"\nAfter Restoration (Final Text):\n'{restored_text}'")
        print("-" * 70 + "\n")
        
        return restored_text


if __name__ == "__main__":
    """
    Minimal test harness to demonstrate the Restorer functionality.
    This simulates the final step of the end-to-end PII redactor workflow.
    """
    print("=" * 20 + " Running Restorer Test Harness " + "=" * 20)

    # 1. Define a sample placeholder map, as created by the Redactor.
    sample_map = {
        '[PERSON_A]': 'Jane Doe',
        '[GPE_A]': 'London',
        '[EMAIL_A]': 'jane.d.doe@example.com'
    }

    # 2. Define a sample response from an LLM, using the placeholders.
    sample_llm_response = (
        "Of course! Here is a poem about the wonderful city of [GPE_A].\n"
        "It's a place where someone like [PERSON_A] could truly thrive.\n"
        "For inquiries, one might try reaching out, perhaps to an address like [EMAIL_A]."
    )

    # 3. Initialize the Restorer and run the restoration process.
    restorer = Restorer()
    final_text = restorer.restore(sample_llm_response, sample_map)

    # 4. Final verification
    print("Test harness complete. The 'After Restoration' text above is the final, de-redacted output.")
    print("=" * 70)
