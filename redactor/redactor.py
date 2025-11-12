"""
This module defines the Redactor class, which is responsible for replacing
detected PII entities in a text with placeholders.
"""

from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict
import pprint

# Import PIIDetector for use in the test harness
from .detector import PIIDetector

class Redactor:
    """
    A class to redact text by replacing specified PII entities with placeholders.
    """

    def _generate_placeholder_id(self, count: int) -> str:
        """
        Generates a character-based ID (A, B, C, ...) from an integer count.
        This simple version supports up to 26 entities per label type.
        """
        if count < 26:
            return chr(ord('A') + count)
        # Fallback for more than 26 entities of the same type
        return str(count)

    def redact(
        self,
        text: str,
        entities: List[Dict[str, Any]],
        labels_to_redact: Optional[List[str]] = None
    ) -> Tuple[str, Dict[str, str]]:
        """
        Redacts text by replacing entities with labeled placeholders.

        Args:
            text: The original text string.
            entities: A list of entity dictionaries from a PIIDetector.
            labels_to_redact: An optional list of labels to redact. If None,
                              all detected entities will be redacted.

        Returns:
            A tuple containing:
            - The redacted text string.
            - A mapping dictionary of {placeholder: original_entity_value}.
        """
        redacted_text = text
        placeholder_map = {}
        
        # 1. Filter entities if labels_to_redact is specified
        if labels_to_redact:
            entities_to_process = [e for e in entities if e['label'] in labels_to_redact]
        else:
            entities_to_process = entities

        # 2. Sort entities by start index in descending order
        # This is crucial to ensure that replacements at the end of the string
        # don't invalidate the indices of entities at the beginning.
        sorted_entities = sorted(entities_to_process, key=lambda e: e['start'], reverse=True)

        # 3. Generate placeholders and replace text
        label_counts = defaultdict(int)
        for entity in sorted_entities:
            label = entity['label']
            
            # Generate a unique placeholder like [PERSON_A], [PERSON_B], etc.
            placeholder_id = self._generate_placeholder_id(label_counts[label])
            placeholder = f"[{label}_{placeholder_id}]"
            label_counts[label] += 1
            
            # Replace the original entity text with the placeholder
            start, end = entity['start'], entity['end']
            redacted_text = redacted_text[:start] + placeholder + redacted_text[end:]
            
            # Store the mapping from placeholder to original value
            placeholder_map[placeholder] = entity['entity']

        # For demo purposes, print the results every time
        self._print_redaction_results(text, redacted_text, placeholder_map)

        return redacted_text, placeholder_map

    def _print_redaction_results(
        self,
        original_text: str,
        redacted_text: str,
        placeholder_map: Dict[str, str]
    ):
        """Helper function to print redaction results in a readable format."""
        print("=" * 25 + " Redaction Result " + "=" * 25)
        print(f"Original Text:  '{original_text}'")
        print(f"Redacted Text:  '{redacted_text}'")
        if placeholder_map:
            print("Placeholder Map:")
            # Sort map for consistent output
            sorted_map = dict(sorted(placeholder_map.items()))
            pprint.pprint(sorted_map, indent=2)
        else:
            print("No entities were redacted.")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    """
    Test harness to demonstrate the Redactor functionality.
    
    This script initializes a PIIDetector to find entities and then uses
    a Redactor to replace them in sample texts.
    """
    print("Initializing PII Detector and Redactor for test run...")
    
    # Initialize both the detector and the redactor
    pii_detector = PIIDetector()
    redactor = Redactor()

    # Proceed only if the spaCy model was loaded successfully
    if pii_detector.nlp:
        sample_texts = [
            "John Doe, a software engineer at Google, can be reached at john.d.doe@google.com.",
            "The conference is scheduled for August 10, 2024, in San Francisco.",
            "Alice paid $500 for a ticket to the 'Future of AI' event."
        ]

        # --- Test Case 1: Redact all detected entities ---
        print("\n--- Running Test Case 1: Redacting ALL detected PII ---\n")
        for sample in sample_texts:
            detected_entities = pii_detector.detect(sample)
            redactor.redact(sample, detected_entities)

        # --- Test Case 2: Redact only specific labels ---
        print("\n--- Running Test Case 2: Redacting ONLY PERSON and EMAIL ---\n")
        text_for_selective_redaction = "Contact John Doe at john.d.doe@google.com, who works for Google."
        
        # First, detect all entities
        all_detected_entities = pii_detector.detect(text_for_selective_redaction)
        
        # Then, redact only a subset of labels
        redactor.redact(
            text_for_selective_redaction,
            all_detected_entities,
            labels_to_redact=["PERSON", "EMAIL"]
        )
