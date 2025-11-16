"""Quick test script for ImageRedactor"""
from redactor.image import ImageRedactor
from redactor.base import Entity
from PIL import Image

# Create test image
img = Image.new('RGB', (800, 600), color='lightblue')
img.save('test.jpg')

# Mock entities
entities = [
    Entity(type='FACE', placeholder='[FACE_A]', bbox=(50, 50, 250, 250),
           confidence=0.99, modality='image', original_text=None, metadata={}),
    Entity(type='OCR_TEXT', placeholder='[TEXT_A]', bbox=(300, 100, 700, 150),
           confidence=0.92, modality='image', original_text='Secret Text', metadata={}),
]

# Test redaction
redactor = ImageRedactor(draw_borders=True, border_color='red')
redacted, mapping = redactor.redact('test.jpg', entities)
redacted.save('test_redacted.jpg')

print('✅ Test complete!')
print(f'Config: {redactor.get_redaction_config()}')
print(f'Mapping: {list(mapping.keys())}')
print('Check test_redacted.jpg to see the result')
