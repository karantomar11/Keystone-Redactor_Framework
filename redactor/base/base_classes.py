"""
Abstract base classes for Keystone Redactor Framework.

This module defines the interfaces (contracts) that all modality-specific
implementations must follow. This ensures consistency and allows for
modular, independent development of text, image, and audio pipelines.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
import logging
from .entities import Entity, DetectionMetadata, Mapping

logger = logging.getLogger(__name__)

class BaseDetector(ABC):
    """
    Abstract base class for all PII detectors (text, image, audio).

    All detector implementations must provide these methods to ensure
    a consistent interface across modalities.
    """

    @abstractmethod
    def detect(self, input_path: str) -> Tuple[List[Entity], DetectionMetadata]:
        """
        Detect PII entities from input file.
        
        This is the main entry point for detection. It should handle all
        modality-specific detection logic and return a standardized format.
        
        Args:
            input_path: Path to input file (text file, image, audio, etc.)
        
        Returns:
            Tuple containing:
                - List of detected Entity objects
                - DetectionMetadata with process information
        
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If input file is corrupted or invalid format
        """
        pass

    @abstractmethod
    def get_supported_entity_types(self) -> List[str]:
        """
        Return list of entity types this detector can find.
        
        Returns:
            List of entity type strings (e.g., ['FACE', 'OCR_TEXT'])
        """
        pass
class BaseRedactor(ABC):
    """
    Abstract base class for all PII redactors.

    Redactors take detected entities and remove/obscure them from the
    original input, creating a safe version for LLM processing.
    """

    @abstractmethod
    def redact(self, input_path: str, entities: List[Entity]) -> Tuple[str, Dict[str, Mapping]]:
        """
        Redact detected entities from input.
        
        Args:
            input_path: Path to input file
            entities: List of Entity objects to redact
        
        Returns:
            Tuple containing:
                - output_path: Path to redacted file
                - mapping: Dict mapping placeholders to Mapping objects
        
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If entities list is empty or invalid
        """
        pass

    @abstractmethod
    def get_redaction_methods(self) -> List[str]:
        """
        Return list of supported redaction methods.
        
        Returns:
            List of method names (e.g., ['blur', 'blackout', 'pixelate'])
        """
        pass
class BaseRestorer(ABC):
    """
    Abstract base class for all PII restorers.

    Restorers take LLM output (which contains placeholders) and
    selectively replace placeholders with original values based on
    the stored mapping.
    """

    @abstractmethod
    def restore(self, text: str, mapping: Dict[str, Mapping]) -> str:
        """
        Restore placeholders in text with original values.
        
        Only replaces placeholders that exist in the mapping to prevent
        confusion between real detected PII and LLM-generated content.
        
        Args:
            text: Text containing placeholders (LLM output)
            mapping: Dict mapping placeholders to Mapping objects
        
        Returns:
            Restored text with placeholders replaced
        """
        pass