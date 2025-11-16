"""
Image entity detection module for Keystone Redactor Framework.

This module provides the ImageDetector class, which is responsible for
detecting various types of privacy-relevant entities in images. It uses a
multi-method approach to identify faces, readable text (OCR), and specific
objects like vehicles and electronic devices.
"""

import logging
import time
from typing import List, Optional, Tuple

import easyocr
import face_recognition
from PIL import Image

from redactor.base.base_classes import BaseDetector
from redactor.base.entities import DetectionMetadata, Entity

# Conditionally import YOLO for object detection
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class ImageDetector(BaseDetector):
    """
    Detects faces, text, and objects in images.

    This detector inherits from BaseDetector and uses three primary methods:
    1. Face detection via the 'face_recognition' library (CNN for GPU, HOG for CPU).
    2. OCR text detection via 'EasyOCR' (GPU-accelerated).
    3. Object detection via YOLOv8 for privacy-relevant objects (vehicles, devices).

    It is designed to be robust, with graceful error handling and clear logging.
    """

    def __init__(self, use_gpu: bool = True, ocr_languages: Optional[List[str]] = None,
                 enable_object_detection: bool = True):
        """
        Initializes the ImageDetector with specified configurations.

        Args:
            use_gpu: If True, attempts to use GPU for acceleration. Defaults to True.
            ocr_languages: List of languages for OCR detection (e.g., ['en', 'de']).
                           Defaults to ['en', 'de'].
            enable_object_detection: If True, enables YOLO-based object detection.
                                     Defaults to True.
        """
        self.logger = logging.getLogger(__name__)
        self.use_gpu = use_gpu
        self.enable_object_detection = enable_object_detection

        if ocr_languages is None:
            ocr_languages = ['en', 'de']

        # 1. Configure face detection model based on GPU availability
        self.face_model = 'cnn' if self.use_gpu else 'hog'

        # 2. Initialize EasyOCR reader
        try:
            self.ocr_reader = easyocr.Reader(ocr_languages, gpu=self.use_gpu)
            self.logger.info("EasyOCR reader initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize EasyOCR reader: {e}")
            self.ocr_reader = None

        # 3. Initialize YOLO model for object detection
        self.yolo_model = None
        if self.enable_object_detection and YOLO_AVAILABLE:
            try:
                self.yolo_model = YOLO('yolov8n.pt')
                self.logger.info("YOLOv8 model loaded successfully.")
            except Exception as e:
                self.logger.warning(f"Failed to load YOLOv8 model: {e}. Disabling object detection.")
                self.enable_object_detection = False
        elif self.enable_object_detection and not YOLO_AVAILABLE:
            self.logger.warning("Ultralytics YOLO is not installed. Disabling object detection.")
            self.enable_object_detection = False

        # 4. Initialize entity counters for generating unique placeholders
        self._face_counter = 0
        self._text_counter = 0
        self._object_counter = 0

        self.logger.info(
            f"ImageDetector initialized. GPU usage: {self.use_gpu}. "
            f"Face model: '{self.face_model}'. OCR enabled: {self.ocr_reader is not None}. "
            f"Object detection enabled: {self.enable_object_detection}."
        )

    def detect_faces(self, image_path: str) -> List[Entity]:
        """
        Detects human faces in an image using the face_recognition library.

        Args:
            image_path: The path to the image file.

        Returns:
            A list of Entity objects, one for each detected face.
        """
        results: List[Entity] = []
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image, model=self.face_model)

            for (top, right, bottom, left) in face_locations:
                self._face_counter += 1
                placeholder = f'[FACE_{chr(64 + self._face_counter)}]'
                bbox = (left, top, right, bottom)

                entity = Entity(
                    type='FACE',
                    placeholder=placeholder,
                    bbox=bbox,
                    confidence=0.99,  # face_recognition doesn't provide confidence
                    modality='image',
                    original_text=None,
                    metadata={'detection_method': self.face_model}
                )
                results.append(entity)

            if results:
                self.logger.info(f"Detected {len(results)} faces in {image_path}.")
            return results
        except FileNotFoundError:
            self.logger.error(f"Image file not found at {image_path}.")
            return []
        except Exception as e:
            self.logger.error(f"An error occurred during face detection: {e}")
            return []

    def detect_text(self, image_path: str, confidence_threshold: float = 0.5) -> List[Entity]:
        """
        Detects and recognizes text in an image using EasyOCR.

        Args:
            image_path: The path to the image file.
            confidence_threshold: The minimum confidence to consider a text detection valid.

        Returns:
            A list of Entity objects for each detected text region.
        """
        if not self.ocr_reader:
            self.logger.warning("OCR reader not available. Skipping text detection.")
            return []

        results: List[Entity] = []
        try:
            ocr_results = self.ocr_reader.readtext(image_path)

            for (bbox_polygon, text, confidence) in ocr_results:
                if confidence < confidence_threshold:
                    continue

                # Convert polygon to a simple rectangular bounding box
                xs = [point[0] for point in bbox_polygon]
                ys = [point[1] for point in bbox_polygon]
                normalized_bbox = (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys)))

                self._text_counter += 1
                placeholder = f'[TEXT_{chr(64 + self._text_counter)}]'

                entity = Entity(
                    type='OCR_TEXT',
                    placeholder=placeholder,
                    bbox=normalized_bbox,
                    confidence=float(confidence),
                    modality='image',
                    original_text=text,
                    metadata={'language': 'auto', 'ocr_engine': 'easyocr'}
                )
                results.append(entity)

            if results:
                self.logger.info(f"Detected {len(results)} text regions in {image_path}.")
            return results
        except Exception as e:
            self.logger.error(f"An error occurred during OCR text detection: {e}")
            return []

    def detect_objects(self, image_path: str) -> List[Entity]:
        """
        Detects privacy-relevant objects (vehicles, devices) using YOLOv8.

        Args:
            image_path: The path to the image file.

        Returns:
            A list of Entity objects for each detected relevant object.
        """
        if not self.enable_object_detection or self.yolo_model is None:
            return []

        RELEVANT_OBJECTS = {
            'car': 'VEHICLE', 'motorcycle': 'VEHICLE', 'truck': 'VEHICLE', 'bus': 'VEHICLE',
            'laptop': 'DEVICE', 'cell phone': 'DEVICE', 'tv': 'DEVICE'
        }
        results: List[Entity] = []
        try:
            yolo_results = self.yolo_model(image_path, verbose=False)

            for detection in yolo_results[0].boxes:
                class_id = int(detection.cls)
                class_name = self.yolo_model.names[class_id]

                if class_name in RELEVANT_OBJECTS:
                    conf = float(detection.conf)
                    if conf < 0.5:
                        continue

                    x1, y1, x2, y2 = detection.xyxy[0].tolist()
                    self._object_counter += 1
                    placeholder = f'[OBJECT_{chr(64 + self._object_counter)}]'
                    entity_type = RELEVANT_OBJECTS[class_name]

                    entity = Entity(
                        type=entity_type,
                        placeholder=placeholder,
                        bbox=(int(x1), int(y1), int(x2), int(y2)),
                        confidence=conf,
                        modality='image',
                        original_text=None,
                        metadata={'object_class': class_name, 'yolo_model': 'yolov8n'}
                    )
                    results.append(entity)

            if results:
                self.logger.info(f"Detected {len(results)} relevant objects in {image_path}.")
            return results
        except Exception as e:
            self.logger.warning(f"An error occurred during object detection: {e}")
            return []

    def detect(self, image_path: str) -> Tuple[List[Entity], DetectionMetadata]:
        """
        Main entry point for running all detection methods on an image.

        This method orchestrates face, text, and object detection, combines the
        results, and returns them along with metadata about the process.

        Args:
            image_path: The path to the input image file.

        Returns:
            A tuple containing:
            - A list of all detected Entity objects.
            - A DetectionMetadata object with summary information.
        """
        self.logger.info(f"Starting comprehensive detection for {image_path}")
        start_time = time.time()

        # Reset counters for each new image
        self._face_counter = 0
        self._text_counter = 0
        self._object_counter = 0

        # Run all detection methods
        faces = self.detect_faces(image_path)
        texts = self.detect_text(image_path)
        objects = self.detect_objects(image_path)

        all_entities = faces + texts + objects
        detection_time = time.time() - start_time

        # Aggregate results for metadata
        entities_by_type = {}
        for entity in all_entities:
            entities_by_type[entity.type] = entities_by_type.get(entity.type, 0) + 1

        metadata = DetectionMetadata(
            total_entities=len(all_entities),
            entities_by_type=entities_by_type,
            detection_time=detection_time,
            gpu_used=self.use_gpu,
            model_info={
                'face_detection': self.face_model,
                'ocr': 'easyocr' if self.ocr_reader else 'disabled',
                'object_detection': 'yolov8n' if self.enable_object_detection else 'disabled'
            }
        )

        self.logger.info(
            f"Detection complete for {image_path}: Found {len(all_entities)} "
            f"entities in {detection_time:.2f}s."
        )
        return all_entities, metadata

    def get_supported_entity_types(self) -> List[str]:
        """
        Returns the list of entity types this detector supports.

        Returns:
            A list of strings representing supported entity types.
        """
        base_types = ['FACE', 'OCR_TEXT']
        if self.enable_object_detection:
            return base_types + ['VEHICLE', 'DEVICE']
        return base_types
