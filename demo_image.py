"""
Complete demonstration of the Keystone Redactor Framework - Image Pipeline.

This script demonstrates the full privacy-preserving workflow for images:
1. Detection: Find faces, OCR text, and objects
2. Redaction: Apply blackout boxes with placeholder labels
3. Restoration: Selectively restore only verified placeholders

Author: Karan Tomar
Date: November 16, 2025
"""

import logging
from pathlib import Path
from PIL import Image

from redactor.image import ImageDetector, ImageRedactor, ImageRestorer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

print("=" * 70)
print("KEYSTONE REDACTOR FRAMEWORK - IMAGE PIPELINE DEMO")
print("=" * 70)
print()

# ============================================================================
# STEP 1: Create a Test Image
# ============================================================================
print("STEP 1: Creating test image...")
print("-" * 70)

# Create a simple test image (white background, 800x600)
test_image = Image.new('RGB', (800, 600), color='white')
test_image_path = 'test_demo_image.jpg'
test_image.save(test_image_path)
print(f"✅ Created test image: {test_image_path}")
print()

# ============================================================================
# STEP 2: Detect Entities (Faces, Text, Objects)
# ============================================================================
print("STEP 2: ENTITY DETECTION")
print("-" * 70)
print("Using ImageDetector to find PII in the image...")
print()

detector = ImageDetector(use_gpu=True, enable_object_detection=True)

# For this demo, we'll use mock entities since our test image is blank
# In a real scenario, detector.detect() would find actual faces/text
from redactor.base import Entity

mock_entities = [
    Entity(
        type='FACE',
        placeholder='[FACE_A]',
        bbox=(50, 50, 250, 250),
        confidence=0.99,
        modality='image',
        original_text=None,
        metadata={'detection_method': 'cnn'}
    ),
    Entity(
        type='FACE',
        placeholder='[FACE_B]',
        bbox=(500, 50, 700, 250),
        confidence=0.97,
        modality='image',
        original_text=None,
        metadata={'detection_method': 'cnn'}
    ),
    Entity(
        type='OCR_TEXT',
        placeholder='[TEXT_A]',
        bbox=(100, 350, 600, 400),
        confidence=0.95,
        modality='image',
        original_text='CONFIDENTIAL DOCUMENT - XYZ-1234',
        metadata={'language': 'en', 'ocr_engine': 'easyocr'}
    ),
    Entity(
        type='VEHICLE',
        placeholder='[VEHICLE_A]',
        bbox=(200, 450, 450, 550),
        confidence=0.88,
        modality='image',
        original_text=None,
        metadata={'object_class': 'car', 'yolo_model': 'yolov8n'}
    )
]

print(f"✅ Detected {len(mock_entities)} entities:")
for i, entity in enumerate(mock_entities, 1):
    print(f"   {i}. {entity.type}: {entity.placeholder} (confidence: {entity.confidence:.2f})")
    if entity.original_text:
        print(f"      Original text: '{entity.original_text}'")
print()

# ============================================================================
# STEP 3: Redact Image (Blackout + Labels)
# ============================================================================
print("STEP 3: IMAGE REDACTION")
print("-" * 70)
print("Applying hybrid redaction (blackout + label overlay)...")
print()

redactor = ImageRedactor(draw_borders=True, border_color='red', border_width=2)
redacted_image, mapping = redactor.redact(test_image_path, mock_entities)

# Save the redacted image
redacted_image_path = 'test_demo_image_REDACTED.jpg'
redacted_image.save(redacted_image_path)

print(f"✅ Redaction complete!")
print(f"   Redacted image saved: {redacted_image_path}")
print(f"   Total entities redacted: {len(mapping)}")
print()

print("Redaction Mapping (Placeholder → Original Entity Info):")
for placeholder, info in mapping.items():
    print(f"   {placeholder} → {info['original_type']} at {info['bbox']}")
print()

# ============================================================================
# STEP 4: Simulate LLM Response
# ============================================================================
print("STEP 4: SIMULATED LLM RESPONSE")
print("-" * 70)
print("The LLM receives the redacted image and generates a response...")
print("(Note: The LLM only sees placeholders, not the original PII)")
print()

# Simulate an LLM analyzing the redacted image
simulated_llm_response = """
Based on the provided image, I can observe the following:

There are two individuals visible in the image: [FACE_A] and [FACE_B]. 
They appear to be standing near a [VEHICLE_A].

The image contains text that reads: [TEXT_A].

Additionally, I notice there might be another person [FACE_C] in the 
background (though this is uncertain), and possibly a [DEVICE_A] on 
the left side of the image.

The overall scene suggests a formal or professional setting.
"""

print("LLM Response (with placeholders):")
print(simulated_llm_response)
print()

# ============================================================================
# STEP 5: Selective Restoration
# ============================================================================
print("STEP 5: SELECTIVE RESTORATION")
print("-" * 70)
print("Restoring ONLY verified placeholders (preventing hallucinations)...")
print()

restorer = ImageRestorer()
restored_text, restoration_stats = restorer.restore(simulated_llm_response, mapping)

print("Restoration Statistics:")
print(f"   Total placeholders found: {restoration_stats['total_placeholders_found']}")
print(f"   Restored (verified): {restoration_stats['restored_count']}")
print(f"   Hallucinated (left as-is): {len(restoration_stats['hallucinated_placeholders'])}")
print(f"   Restoration time: {restoration_stats['restoration_time']:.6f}s")
print()

if restoration_stats['hallucinated_placeholders']:
    print("⚠️  Hallucinated placeholders detected (NOT in original mapping):")
    for hallucination in restoration_stats['hallucinated_placeholders']:
        print(f"   - {hallucination} (LLM generated, not verified)")
    print()

print("-" * 70)
print("FINAL RESTORED TEXT:")
print("-" * 70)
print(restored_text)
print()

# ============================================================================
# STEP 6: Comparison and Key Insights
# ============================================================================
print("=" * 70)
print("KEY INSIGHTS - PRIVACY-PRESERVING WORKFLOW")
print("=" * 70)
print()

print("✅ What worked:")
print("   1. Original PII never sent to LLM (faces, text, vehicle)")
print("   2. LLM received only placeholders and generated analysis")
print("   3. Verified entities restored successfully:")
for placeholder in restoration_stats['restored_placeholders']:
    print(f"      - {placeholder} → {mapping[placeholder]['original_type']}")
print()

print("⚠️  What was prevented:")
print("   1. LLM hallucinations caught and left as placeholders:")
for hallucination in restoration_stats['hallucinated_placeholders']:
    print(f"      - {hallucination} (not in original detection)")
print()

print("🎯 USER BENEFIT:")
print("   Users can distinguish between:")
print("   - Verified facts (restored from detection)")
print("   - AI-generated inferences (placeholders remain)")
print()

# ============================================================================
# Cleanup
# ============================================================================
print("=" * 70)
print("DEMO COMPLETE")
print("=" * 70)
print()
print(f"Generated files:")
print(f"   - {test_image_path} (original test image)")
print(f"   - {redacted_image_path} (redacted with blackout + labels)")
print()
print("The image pipeline is ready for production use!")
print()