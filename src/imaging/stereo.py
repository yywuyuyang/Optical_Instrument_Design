import numpy as np


class StereoRangingSystem:
    def __init__(
        self,
        baseline: float = 0.065,
        focal_length: float = 0.008,
        pixel_size: float = 3.45e-6,
        image_width: int = 1920,
        image_height: int = 1080,
    ):
        self.baseline = baseline
        self.focal_length = focal_length
        self.pixel_size = pixel_size
        self.image_width = image_width
        self.image_height = image_height

    def distance_from_disparity(self, disparity_pixels: float) -> float:
        return (self.baseline * self.focal_length) / (disparity_pixels * self.pixel_size)

    def disparity_from_distance(self, distance: float) -> float:
        return (self.baseline * self.focal_length) / (distance * self.pixel_size)

    def fov_horizontal(self) -> float:
        return 2 * np.arctan(
            (self.image_width * self.pixel_size) / (2 * self.focal_length)
        )

    def fov_vertical(self) -> float:
        return 2 * np.arctan(
            (self.image_height * self.pixel_size) / (2 * self.focal_length)
        )

    def range_error(self, distance: float, disparity_error: float = 0.5) -> float:
        disparity = self.disparity_from_distance(distance)
        return distance**2 * disparity_error * self.pixel_size / (
            self.baseline * self.focal_length
        )

    def relative_error(self, distance: float, disparity_error: float = 0.5) -> float:
        disparity = self.disparity_from_distance(distance)
        return disparity_error / disparity

    def min_measurable_distance(self, min_disparity: float = 1.0) -> float:
        return self.distance_from_disparity(min_disparity)

    def max_measurable_distance(self, disparity_precision: float = 0.1) -> float:
        return self.distance_from_disparity(disparity_precision)

    def design_from_requirements(
        self,
        z_min: float,
        z_max: float,
        accuracy_percent: float,
        disparity_error: float = 0.5,
    ) -> dict:
        required_disparity_at_max = disparity_error / (accuracy_percent / 100)
        required_Bf = z_max * required_disparity_at_max * self.pixel_size
        min_Bf = z_min * 1.0 * self.pixel_size

        if required_Bf < min_Bf:
            Bf = min_Bf
        else:
            Bf = required_Bf

        baseline = Bf / self.focal_length
        return {
            "baseline": baseline,
            "Bf_product": Bf,
            "z_min": z_min,
            "z_max": z_max,
            "accuracy_percent": accuracy_percent,
            "disparity_at_z_min": self.baseline * self.focal_length / (z_min * self.pixel_size) if baseline == self.baseline else Bf / (z_min * self.pixel_size),
            "disparity_at_z_max": Bf / (z_max * self.pixel_size),
        }
