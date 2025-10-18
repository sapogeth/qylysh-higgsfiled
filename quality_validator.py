"""
Quality Validation System for Generated Images
Checks image quality and triggers regeneration if needed
"""

from PIL import Image, ImageStat
import numpy as np
from typing import Dict, Any, Tuple
import config


class QualityValidator:
    """Validates the quality of generated images"""

    def __init__(self):
        """Initialize the quality validator"""
        self.min_sharpness = 50.0  # Minimum acceptable sharpness
        self.max_brightness_std = 80.0  # Maximum standard deviation in brightness
        self.min_contrast = 30.0  # Minimum contrast

    def validate(self, image: Image.Image, frame_desc: str = "") -> Tuple[bool, Dict[str, Any]]:
        """
        Validate image quality

        Args:
            image: PIL Image to validate
            frame_desc: Frame description for context

        Returns:
            Tuple of (is_valid, metrics_dict)
        """

        metrics = {}
        issues = []

        # Check 1: Image is not corrupted
        try:
            image.verify()
            metrics['corrupted'] = False
        except:
            metrics['corrupted'] = True
            issues.append("Image file is corrupted")
            return False, {'issues': issues, **metrics}

        # Reload image after verify (verify closes the file)
        image = image.copy()

        # Check 2: Image dimensions
        width, height = image.size
        metrics['width'] = width
        metrics['height'] = height

        if width < 512 or height < 512:
            issues.append(f"Image too small: {width}x{height}")

        # Check 3: Sharpness (using edge detection approximation)
        sharpness = self._calculate_sharpness(image)
        metrics['sharpness'] = sharpness

        if sharpness < self.min_sharpness:
            issues.append(f"Image too blurry: sharpness {sharpness:.1f} < {self.min_sharpness}")

        # Check 4: Brightness and contrast
        brightness, contrast = self._calculate_brightness_contrast(image)
        metrics['brightness'] = brightness
        metrics['contrast'] = contrast

        if contrast < self.min_contrast:
            issues.append(f"Low contrast: {contrast:.1f} < {self.min_contrast}")

        # Check 5: Color distribution (detect completely black/white images)
        is_monochrome = self._check_monochrome(image)
        metrics['monochrome'] = is_monochrome

        if is_monochrome:
            issues.append("Image appears to be monochrome or failed")

        # Check 6: Detect common artifacts
        has_artifacts = self._detect_artifacts(image)
        metrics['has_artifacts'] = has_artifacts

        if has_artifacts:
            issues.append("Detected visual artifacts")

        # Overall validation
        is_valid = len(issues) == 0
        metrics['issues'] = issues
        metrics['is_valid'] = is_valid

        return is_valid, metrics

    def _calculate_sharpness(self, image: Image.Image) -> float:
        """
        Calculate image sharpness using edge detection
        Higher values = sharper image
        """
        # Convert to grayscale
        gray = image.convert('L')

        # Calculate gradient magnitude using simple edge detection
        np_img = np.array(gray, dtype=float)

        # Sobel-like edge detection
        gx = np.abs(np_img[1:, :] - np_img[:-1, :])
        gy = np.abs(np_img[:, 1:] - np_img[:, :-1])

        # Average gradient magnitude
        sharpness = np.mean(gx) + np.mean(gy)

        return float(sharpness)

    def _calculate_brightness_contrast(self, image: Image.Image) -> Tuple[float, float]:
        """
        Calculate brightness and contrast

        Returns:
            Tuple of (brightness, contrast)
        """
        # Convert to grayscale
        gray = image.convert('L')
        stat = ImageStat.Stat(gray)

        # Brightness is the mean pixel value
        brightness = stat.mean[0]

        # Contrast is the standard deviation
        contrast = stat.stddev[0]

        return brightness, contrast

    def _check_monochrome(self, image: Image.Image) -> bool:
        """
        Check if image is essentially monochrome (single color)

        Returns:
            True if monochrome, False otherwise
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Get statistics for each channel
        stat = ImageStat.Stat(image)

        # Check if standard deviation is very low in all channels
        # (indicates little color variation)
        for stddev in stat.stddev:
            if stddev < 10.0:  # Very low variation
                return True

        return False

    def _detect_artifacts(self, image: Image.Image) -> bool:
        """
        Detect common image generation artifacts

        Returns:
            True if artifacts detected, False otherwise
        """
        # Convert to numpy array
        np_img = np.array(image)

        # Check for extreme values (completely black or white regions)
        black_pixels = np.sum(np.all(np_img < 10, axis=-1))
        white_pixels = np.sum(np.all(np_img > 245, axis=-1))

        total_pixels = np_img.shape[0] * np_img.shape[1]

        # If more than 30% of image is pure black or white, likely an artifact
        if (black_pixels / total_pixels) > 0.3 or (white_pixels / total_pixels) > 0.3:
            return True

        return False

    def should_regenerate(self, metrics: Dict[str, Any]) -> bool:
        """
        Determine if image should be regenerated based on metrics

        Args:
            metrics: Metrics dictionary from validate()

        Returns:
            True if should regenerate, False otherwise
        """
        if not config.ENABLE_QUALITY_VALIDATION:
            return False

        # Don't regenerate if already at max attempts
        return not metrics.get('is_valid', True)

    def get_quality_score(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate overall quality score (0-100)

        Args:
            metrics: Metrics dictionary from validate()

        Returns:
            Quality score as float
        """
        score = 100.0

        # Penalize for issues
        if metrics.get('corrupted', False):
            return 0.0

        if metrics.get('monochrome', False):
            score -= 40

        if metrics.get('has_artifacts', False):
            score -= 20

        # Penalize for low sharpness
        sharpness = metrics.get('sharpness', 0)
        if sharpness < self.min_sharpness:
            score -= (self.min_sharpness - sharpness) / 2

        # Penalize for low contrast
        contrast = metrics.get('contrast', 0)
        if contrast < self.min_contrast:
            score -= (self.min_contrast - contrast)

        # Ensure score is between 0-100
        score = max(0.0, min(100.0, score))

        return score


def test_validator():
    """Test the quality validator"""

    print("=" * 70)
    print("TESTING QUALITY VALIDATOR")
    print("=" * 70)
    print()

    validator = QualityValidator()

    # Test with reference images
    import config

    for img_path in config.REFERENCE_IMAGES:
        if img_path.exists():
            print(f"Testing: {img_path.name}")

            img = Image.open(img_path)
            is_valid, metrics = validator.validate(img)
            quality_score = validator.get_quality_score(metrics)

            print(f"  Valid: {is_valid}")
            print(f"  Quality Score: {quality_score:.1f}/100")
            print(f"  Sharpness: {metrics.get('sharpness', 0):.1f}")
            print(f"  Contrast: {metrics.get('contrast', 0):.1f}")
            print(f"  Brightness: {metrics.get('brightness', 0):.1f}")

            if not is_valid:
                print(f"  Issues: {', '.join(metrics['issues'])}")

            print()

    print("=" * 70)
    print("TEST COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    test_validator()
