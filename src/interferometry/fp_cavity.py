import numpy as np


class FabryPerotCavity:
    def __init__(
        self,
        R: float = 0.95,
        h: float = 100e-6,
        n: float = 1.0,
        theta: float = 0.0,
    ):
        self.R = R
        self.h = h
        self.n = n
        self.theta = theta

    def _finesse_coefficient(self) -> float:
        return 4 * self.R / (1 - self.R) ** 2

    def _phase_delta(self, wavelength: float | np.ndarray) -> float | np.ndarray:
        return 4 * np.pi * self.n * self.h * np.cos(self.theta) / wavelength

    def transmission(self, wavelength: float | np.ndarray) -> float | np.ndarray:
        F = self._finesse_coefficient()
        delta = self._phase_delta(wavelength)
        return 1.0 / (1.0 + F * np.sin(delta / 2) ** 2)

    def reflection(self, wavelength: float | np.ndarray) -> float | np.ndarray:
        return 1.0 - self.transmission(wavelength)

    def finesse(self) -> float:
        return np.pi * np.sqrt(self.R) / (1 - self.R)

    def fsr(self, lambda0: float = 632e-9) -> float:
        return lambda0**2 / (2 * self.n * self.h)

    def fwhm(self, lambda0: float = 632e-9) -> float:
        return self.fsr(lambda0) / self.finesse()

    def q_factor(self, lambda0: float = 632e-9) -> float:
        return lambda0 / self.fwhm(lambda0)

    def resonance_wavelengths(
        self, lambda_min: float, lambda_max: float
    ) -> np.ndarray:
        m_min = int(np.ceil(2 * self.n * self.h * np.cos(self.theta) / lambda_max))
        m_max = int(np.floor(2 * self.n * self.h * np.cos(self.theta) / lambda_min))
        orders = np.arange(m_min, m_max + 1)
        wavelengths = 2 * self.n * self.h * np.cos(self.theta) / orders
        return wavelengths

    def plot_transmission_comparison(
        self, R_list: list[float], wavelength_range: np.ndarray
    ) -> dict[float, np.ndarray]:
        results = {}
        original_R = self.R
        for R in R_list:
            self.R = R
            results[R] = self.transmission(wavelength_range)
        self.R = original_R
        return results
