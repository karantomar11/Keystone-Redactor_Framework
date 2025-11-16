"""
Core data types for Keystone Redactor Framework.

This module defines the foundational data structures used across all
modality-specific implementations (text, image, audio). These types
ensure consistency and type safety throughout the redaction pipeline.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple

@dataclass
class Entity:
    """
    Represents a detected PII entity across any modality (text, image, audio).

    This is the universal format for all detected entities, whether they come
    from text analysis, image detection, or audio transcription.

    Attributes:
        type: Entity classification (e.g., 'PERSON', 'FACE', 'EMAIL', 'OCR_TEXT', 'VEHICLE')
        placeholder: Unique identifier for redaction (e.g., '[PERSON_A]', '[FACE_A]')
        confidence: Detection confidence score between 0.0 and 1.0
        modality: Source modality ('text', 'image', 'audio')
        original_text: Original text content (only for text/OCR entities)
        bbox: Bounding box coordinates for image entities (x1, y1, x2, y2)
        timestamp: Time range for audio entities (start_seconds, end_seconds)
        metadata: Additional modality-specific information
    """
    type: str
    placeholder: str
    confidence: float
    modality: str
    original_text: Optional[str] = None
    bbox: Optional[Tuple[int, int, int, int]] = None
    timestamp: Optional[Tuple[float, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DetectionMetadata:
    """
    Metadata about the detection process for audit, debugging, and compliance.

    This information is critical for GDPR/HIPAA compliance as it provides
    an audit trail of what was detected, how, and with what confidence.

    Attributes:
        total_entities: Total number of entities detected
        entities_by_type: Count of entities per type (e.g., {'FACE': 2, 'OCR_TEXT': 5})
        detection_time: Time taken for detection in seconds
        gpu_used: Whether GPU acceleration was used
        model_info: Information about models used for detection
    """
    total_entities: int
    entities_by_type: Dict[str, int]
    detection_time: float
    gpu_used: bool
    model_info: Dict[str, str]

@dataclass
class Mapping:
    """
    Maps a placeholder to its original entity for restoration and audit.

    This enables the restoration phase where placeholders in LLM output
    are replaced with original values, but only for placeholders that
    were actually detected (preventing hallucination confusion).

    Attributes:
        placeholder: The placeholder string (e.g., '[FACE_A]')
        entity: Full entity object with all detection details
        restorable: Whether this entity can be restored in text output
                   (True for OCR_TEXT, False for FACE - can't restore pixels)
    """
    placeholder: str
    entity: Entity
    restorable: bool