import numpy as np


class FresnelLens:
    def __init__(
        self,
        focal_length: float = 0.1,
        wavelength: float = 632e-9,
        radius: float = 0.0125,
        n: float = 1.5,
    ):
        self.focal_length = focal_length
        self.wavelength = wavelength
        self.radius = radius
        self.n = n

    def phase_map(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        r = np.sqrt(x**2 + y**2)
        phase = -(2 * np.pi / self.wavelength) * (
            np.sqrt(r**2 + self.focal_length**2) - self.focal_length
        )
        mask = r > self.radius
        phase[mask] = np.nan
        return phase

    def wrapped_phase(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        phase = self.phase_map(x, y)
        return np.mod(phase, 2 * np.pi)

    def quantize_phase(
        self, x: np.ndarray, y: np.ndarray, levels: int = 8
    ) -> np.ndarray:
        phase = self.wrapped_phase(x, y)
        step = 2 * np.pi / levels
        quantized = np.round(phase / step) * step
        mask = np.isnan(phase)
        quantized[mask] = np.nan
        return quantized

    def ring_radii(self, max_order: int | None = None) -> np.ndarray:
        if max_order is None:
            max_order = int(np.floor(self.radius**2 / (self.wavelength * self.focal_length)))
        orders = np.arange(1, max_order + 1)
        radii = np.sqrt(orders * self.wavelength * self.focal_length)
        valid = radii <= self.radius
        return radii[valid]

    def etch_depth(self) -> float:
        return self.wavelength / (self.n - 1)

    def focal_spot_size(self) -> float:
        return 1.22 * self.wavelength * self.focal_length / (2 * self.radius)

    def f_number(self) -> float:
        return self.focal_length / (2 * self.radius)

    def num_rings(self) -> int:
        return len(self.ring_radii())
