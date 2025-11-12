import spacy
import re
from typing import List, Dict, Any



class PIIDetector:
    """
    A class to detect Personal Identifiable Information (PII) in a given text
    using spaCy's Named Entity Recognition (NER) and regex fallbacks.
    """

    # Class-level constant for default spaCy NER labels to be detected.
    DEFAULT_LABELS = [
        "PERSON", "ORG", "GPE", "DATE", "CARDINAL", "NORP",
        "LOC", "MONEY", "TIME", "FAC", "EVENT", "PRODUCT",
        "LAW", "LANGUAGE", "WORK_OF_ART"
    ]
    
    # Regex for finding email addresses.
    EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    def __init__(self):
        """
        Initializes the PIIDetector by loading the spaCy 'en_core_web_sm' model.
        Handles errors if the model is not found and provides instructions.
        """
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Spacy model 'en_core_web_sm' not found.")
            print("Please run: python -m spacy download en_core_web_sm")
            self.nlp = None

    def _find_emails(self, text: str) -> List[Dict[str, Any]]:
        """Finds email addresses using a regular expression."""
        entities = []
        for match in re.finditer(self.EMAIL_REGEX, text):
            entities.append({
                "entity": match.group(0),
                "label": "EMAIL",
                "start": match.start(),
                "end": match.end()
            })
        return entities

    def _deduplicate_and_sort_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sorts entities by their start index and removes duplicates or overlaps.

        This method ensures that in cases of overlap, the first-occurring and
        longest entity is preferred.
        """
        if not entities:
            return []

        # Sort by start index, and for ties, by the inverse of the end index (longer entities first)
        sorted_entities = sorted(entities, key=lambda e: (e['start'], -e['end']))

        deduplicated = []
        last_end = -1

        for entity in sorted_entities:
            # Skip if the entity is completely contained within the previously added one.
            if entity['end'] <= last_end:
                continue
            
            # As the list is sorted, if the current entity starts before the last one ended,
            # it's an overlap. We simply skip it to honor the "no overlapping indices" rule,
            # effectively keeping the first and longest entity from the sorted list.
            if entity['start'] < last_end:
                continue

            deduplicated.append(entity)
            last_end = entity['end']

        return deduplicated

    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Detects PII entities in the given text using spaCy and regex.

        Args:
            text: The input string to analyze.

        Returns:
            A sorted and de-duplicated list of dictionaries, where each
            dictionary represents a detected PII entity.
        """
        if not self.nlp:
            print("PIIDetector is not initialized. Cannot process text.")
            return []

        # 1. Detect entities using spaCy NER
        doc = self.nlp(text)
        spacy_entities = []
        # Also check for 'EMAIL' label from spaCy models that might support it
        supported_labels = self.DEFAULT_LABELS + ["EMAIL"]
        for ent in doc.ents:
            if ent.label_ in supported_labels:
                spacy_entities.append({
                    "entity": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })

        # 2. Add regex fallback for EMAIL detection
        regex_emails = self._find_emails(text)

        # 3. Combine entities from both sources
        all_entities = spacy_entities + regex_emails

        # 4. Sort and de-duplicate entities to resolve overlaps and duplicates
        final_entities = self._deduplicate_and_sort_entities(all_entities)

        # 5. Print detected entities for debug/demo purposes
        self._print_detected_entities(text, final_entities)

        return final_entities

    def _print_detected_entities(self, text: str, entities: List[Dict[str, Any]]):
        """Helper function to print detected entities in a readable format."""
        print("-" * 50)
        print(f"Original Text: '{text}'")
        if not entities:
            print("--> No PII entities detected.")
        else:
            print("--> Detected PII Entities:")
            for entity in entities:
                print(
                    f"  - Entity: '{entity['entity']}', "
                    f"Label: {entity['label']}, "
                    f"Indices: [{entity['start']}, {entity['end']}]"
                )
        print("-" * 50 + "\n")


if __name__ == "__main__":
    """
    Test harness to demonstrate the PIIDetector functionality on sample sentences.
    This block will only execute when the script is run directly.
    """
    print("Initializing PIIDetector and running test cases...")
    
    detector = PIIDetector()

    # Proceed only if the spaCy model was loaded successfully
    if detector.nlp:
        sample_texts = [
            "John Doe, a software engineer at Google, can be reached at john.d.doe@google.com.",
            "The conference is scheduled for August 10, 2024, in San Francisco. Contact event-info@conference.org for more details.",
            "Alice paid $500 for a ticket to the 'Future of AI' event. Her confirmation number is 892374.",
            "This is a simple sentence with no personal information.",
            "Edge case with multiple emails: bob@example.com and robert.smith@sub.domain.co.uk are attending.",
            "Dr. Evelyn Reed works at the Jet Propulsion Laboratory (JPL) and lives in Pasadena."
        ]

        for sample in sample_texts:
            # The detect method will internally print the results
            detector.detect(sample)
