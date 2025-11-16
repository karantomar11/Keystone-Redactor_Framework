"""Image Redaction Module for Keystone Redactor Framework.

This module provides the ImageRedactor class, which is responsible for redacting
sensitive information from images based on detected entities. It uses a hybrid
strategy of drawing blackout boxes over sensitive regions and overlaying them
with placeholder text labels.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

from redactor.base.base_classes import BaseRedactor
from redactor.base.entities import Entity


class ImageRedactor(BaseRedactor):
    """
    Redacts entities from an image using a hybrid blackout and label strategy.

    This class inherits from BaseRedactor and implements the logic for applying
    redactions to image files. For each detected entity, it draws a black
    rectangle over the bounding box and overlays a white text label with the

    entity's placeholder. This approach ensures that sensitive visual information
    is completely obscured while maintaining a reference to what was redacted.

    Attributes:
        draw_borders (bool): Whether to draw a colored border around redaction boxes.
        border_color (str): The color of the border (e.g., 'red', '#FF0000').
        border_width (int): The width of the border in pixels.
        logger (logging.Logger): Logger instance for the class.
        font (ImageFont): The font used for drawing placeholder labels.
    """

    def __init__(
        self,
        draw_borders: bool = True,
        border_color: str = "red",
        border_width: int = 2,
    ):
        """
        Initializes the ImageRedactor.

        Args:
            draw_borders (bool): If True, a colored border is drawn around each
                redacted area. Defaults to True.
            border_color (str): The color of the border. Defaults to 'red'.
            border_width (int): The pixel width of the border. Defaults to 2.
        """
        self.draw_borders = draw_borders
        self.border_color = border_color
        self.border_width = border_width
        self.logger = logging.getLogger(__name__)

        # Attempt to load a better font, fallback to default
        try:
            self.font = ImageFont.truetype("arial.ttf", 15)
            self._font_info = "arial.ttf (size 15)"
        except IOError:
            self.logger.warning(
                "Arial font not found. Falling back to default PIL font."
            )
            self.font = ImageFont.load_default()
            self._font_info = "PIL default"

    def _draw_blackout_box(
        self,
        draw: ImageDraw,
        bbox: Tuple[int, int, int, int],
    ) -> None:
        """
        Draws a filled black rectangle over the specified bounding box.

        Optionally draws a colored border around the box if configured.

        Args:
            draw (ImageDraw): The PIL ImageDraw object to draw on.
            bbox (Tuple[int, int, int, int]): The bounding box (x1, y1, x2, y2)
                of the area to redact.
        """
        if self.draw_borders:
            # Draw the border first (slightly larger than the blackout box)
            bordered_bbox = (
                bbox[0] - self.border_width,
                bbox[1] - self.border_width,
                bbox[2] + self.border_width,
                bbox[3] + self.border_width,
            )
            draw.rectangle(bordered_bbox, fill=self.border_color)

        # Draw the main blackout box
        draw.rectangle(bbox, fill="black")

    def _draw_label_text(
        self, draw: ImageDraw, bbox: Tuple[int, int, int, int], text: str
    ) -> None:
        """
        Draws a white text label centered on a bounding box.

        Args:
            draw (ImageDraw): The PIL ImageDraw object to draw on.
            bbox (Tuple[int, int, int, int]): The bounding box where the text
                should be centered.
            text (str): The placeholder text to draw (e.g., '[FACE_A]').
        """
        # Ensure text can be drawn even on small boxes
        if bbox[2] - bbox[0] < 10 or bbox[3] - bbox[1] < 10:
            self.logger.warning(
                f"Bounding box for '{text}' is very small. "
                "Skipping label drawing to avoid clutter."
            )
            return

        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        draw.text(
            (center_x, center_y), text, font=self.font, fill="white", anchor="mm"
        )

    def redact(
        self, image_path: str, entities: List[Entity]
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Redacts detected entities from an image.

        Loads an image, draws redactions for each entity, and creates a mapping
        that links each placeholder to the original entity's information.

        Args:
            image_path (str): The file path to the image to be redacted.
            entities (List[Entity]): A list of Entity objects detected in the image.

        Returns:
            Tuple[Image.Image, Dict[str, Any]]: A tuple containing:
                - The redacted PIL Image object.
                - A dictionary mapping each placeholder to its original entity data.

        Raises:
            FileNotFoundError: If the image_path does not exist.
            IOError: If the file at image_path is not a valid image.
        """
        try:
            image = Image.open(image_path)
            # Work on a copy, ensure it's in RGB for consistency
            redacted_image = image.copy().convert("RGB")
        except FileNotFoundError:
            self.logger.error(f"Image file not found at: {image_path}")
            raise
        except IOError:
            self.logger.error(f"Invalid or corrupted image file: {image_path}")
            raise

        if not entities:
            self.logger.info("No entities provided for redaction. Returning original image.")
            return redacted_image, {}

        draw = ImageDraw.Draw(redacted_image)
        mapping: Dict[str, Any] = {}

        for entity in entities:
            if not entity.bbox:
                self.logger.warning(
                    f"Entity '{entity.placeholder}' is missing a bounding box. Skipping."
                )
                continue

            try:
                # 1. Draw the blackout box (and optional border)
                self._draw_blackout_box(draw, entity.bbox)

                # 2. Overlay the placeholder text
                self._draw_label_text(draw, entity.bbox, entity.placeholder)

                # 3. Create the mapping entry for this redaction
                mapping[entity.placeholder] = {
                    "placeholder": entity.placeholder,
                    "original_type": entity.type,
                    "bbox": entity.bbox,
                    "confidence": entity.confidence,
                    "redacted_at": datetime.now(timezone.utc).isoformat(),
                    "modality": "image",
                    "original_text": entity.original_text,
                    "metadata": entity.metadata or {},
                }
                self.logger.debug(f"Redacted entity: {entity.placeholder}")

            except Exception as e:
                self.logger.error(
                    f"Failed to redact entity {entity.placeholder}: {e}",
                    exc_info=True,
                )

        self.logger.info(f"Redaction complete. Processed {len(mapping)} entities.")
        return redacted_image, mapping

    def get_redaction_config(self) -> Dict[str, Any]:
        """
        Returns the current configuration of the redactor.

        Returns:
            Dict[str, Any]: A dictionary with the current settings.
        """
        return {
            "draw_borders": self.draw_borders,
            "border_color": self.border_color,
            "border_width": self.border_width,
            "font_info": self._font_info,
        }

    def get_redaction_methods(self) -> List[str]:
        """
        Returns the list of redaction methods supported by this class.

        Returns:
            List[str]: A list containing the name of the redaction strategy.
        """
        return ["hybrid_blackout_and_label"]
