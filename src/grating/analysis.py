import numpy as np
from scipy.special import jv


class DiffractionGrating:
    def __init__(
        self,
        period: float = 2e-6,
        wavelength: float = 632e-9,
        incidence_angle: float = 0.0,
        max_order: int = 5,
    ):
        self.period = period
        self.wavelength = wavelength
        self.incidence_angle = incidence_angle
        self.max_order = max_order

    def diffraction_angle(self, order: int) -> float | None:
        sin_theta_m = order * self.wavelength / self.period + np.sin(
            self.incidence_angle
        )
        if np.abs(sin_theta_m) <= 1:
            return np.arcsin(sin_theta_m)
        return None

    def all_diffraction_angles(self) -> dict[int, float | None]:
        result = {}
        for m in range(-self.max_order, self.max_order + 1):
            result[m] = self.diffraction_angle(m)
        return result

    def efficiency_sine_phase(self, order: int, phase_depth: float) -> float:
        return float(jv(order, phase_depth / 2) ** 2)

    def efficiency_amplitude(self, order: int, duty_cycle: float = 0.5) -> float:
        if order == 0:
            return duty_cycle**2
        sinc_arg = np.pi * order * duty_cycle
        return (duty_cycle * np.sin(sinc_arg) / sinc_arg) ** 2

    def efficiency_rect_phase(
        self, order: int, duty_cycle: float = 0.5, phase_depth: float = np.pi
    ) -> float:
        if order == 0:
            return (
                1
                - 2 * duty_cycle * (1 - duty_cycle) * (1 - np.cos(phase_depth))
            )
        return (
            (4 / (np.pi * order) ** 2)
            * np.sin(np.pi * order * duty_cycle) ** 2
            * np.sin(phase_depth / 2) ** 2
        )

    def scan_angle(
        self,
        angle_range: np.ndarray,
        order: int = 1,
    ) -> tuple[np.ndarray, np.ndarray]:
        valid_angles = []
        valid_diff_angles = []
        for theta_i in angle_range:
            sin_theta_m = order * self.wavelength / self.period + np.sin(theta_i)
            if np.abs(sin_theta_m) <= 1:
                valid_angles.append(theta_i)
                valid_diff_angles.append(np.arcsin(sin_theta_m))
        return np.array(valid_angles), np.array(valid_diff_angles)

    def scan_wavelength(
        self,
        wavelength_range: np.ndarray,
        order: int = 1,
    ) -> tuple[np.ndarray, np.ndarray]:
        valid_wavelengths = []
        valid_angles = []
        for lam in wavelength_range:
            sin_theta_m = order * lam / self.period + np.sin(
                self.incidence_angle
            )
            if np.abs(sin_theta_m) <= 1:
                valid_wavelengths.append(lam)
                valid_angles.append(np.arcsin(sin_theta_m))
        return np.array(valid_wavelengths), np.array(valid_angles)

    def scan_period(
        self,
        period_range: np.ndarray,
        order: int = 1,
    ) -> tuple[np.ndarray, np.ndarray]:
        valid_periods = []
        valid_angles = []
        for d in period_range:
            sin_theta_m = order * self.wavelength / d + np.sin(
                self.incidence_angle
            )
            if np.abs(sin_theta_m) <= 1:
                valid_periods.append(d)
                valid_angles.append(np.arcsin(sin_theta_m))
        return np.array(valid_periods), np.array(valid_angles)
