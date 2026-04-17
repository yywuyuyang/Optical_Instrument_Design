import numpy as np
from math import factorial


NOLL_TO_NM = [
    (0, 0),
    (1, 1),
    (1, -1),
    (2, 0),
    (2, 2),
    (2, -2),
    (3, 1),
    (3, -1),
    (3, 3),
    (3, -3),
    (4, 0),
    (4, 2),
    (4, -2),
    (4, 4),
    (4, -4),
    (5, 1),
    (5, -1),
    (5, 3),
    (5, -3),
    (5, 5),
    (5, -5),
    (6, 0),
    (6, 2),
    (6, -2),
    (6, 4),
    (6, -4),
    (6, 6),
    (6, -6),
    (7, 1),
    (7, -1),
    (7, 3),
    (7, -3),
    (7, 5),
    (7, -5),
    (7, 7),
    (7, -7),
]

ABERRATION_NAMES = [
    "Piston",
    "Tip",
    "Tilt",
    "Defocus",
    "Astigmatism 45deg",
    "Astigmatism 0deg",
    "Coma X",
    "Coma Y",
    "Trefoil X",
    "Trefoil Y",
    "Spherical",
    "Sec Astig 45deg",
    "Sec Astig 0deg",
    "Quadrafoil X",
    "Quadrafoil Y",
    "Sec Coma X",
    "Sec Coma Y",
    "Sec Trefoil X",
    "Sec Trefoil Y",
    "Pentafoil X",
    "Pentafoil Y",
    "Ter Spherical",
    "Ter Astig 45deg",
    "Ter Astig 0deg",
    "Ter Quadrafoil X",
    "Ter Quadrafoil Y",
    "Hexafoil X",
    "Hexafoil Y",
    "Ter Coma X",
    "Ter Coma Y",
    "Ter Trefoil X",
    "Ter Trefoil Y",
    "Ter Pentafoil X",
    "Ter Pentafoil Y",
    "Heptafoil X",
    "Heptafoil Y",
]


def radial_polynomial(n: int, m: int, rho: np.ndarray) -> np.ndarray:
    m_abs = abs(m)
    result = np.zeros_like(rho, dtype=float)
    for k in range((n - m_abs) // 2 + 1):
        coeff = (
            (-1) ** k
            * factorial(n - k)
            / (
                factorial(k)
                * factorial((n + m_abs) // 2 - k)
                * factorial((n - m_abs) // 2 - k)
            )
        )
        result += coeff * rho ** (n - 2 * k)
    return result


def zernike_noll(j: int, rho: np.ndarray, theta: np.ndarray) -> np.ndarray:
    n, m = NOLL_TO_NM[j - 1]
    R_nm = radial_polynomial(n, m, rho)
    if m >= 0:
        return R_nm * np.cos(m * theta)
    else:
        return R_nm * np.sin(abs(m) * theta)


def zernike_grid(j: int, resolution: int = 256) -> np.ndarray:
    x = np.linspace(-1, 1, resolution)
    y = np.linspace(-1, 1, resolution)
    X, Y = np.meshgrid(x, y)
    rho = np.sqrt(X**2 + Y**2)
    theta = np.arctan2(Y, X)
    Z = zernike_noll(j, rho, theta)
    Z[rho > 1] = np.nan
    return Z


def plot_zernike_modes(noll_max: int = 36, resolution: int = 256, save_path: str | None = None):
    import matplotlib.pyplot as plt

    ncols = 6
    nrows = (noll_max + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(20, 3.4 * nrows))

    for idx in range(nrows * ncols):
        row, col = idx // ncols, idx % ncols
        ax = axes[row, col] if nrows > 1 else axes[col]

        if idx < noll_max:
            j = idx + 1
            n, m = NOLL_TO_NM[idx]
            Z = zernike_grid(j, resolution)
            im = ax.imshow(
                Z,
                cmap="RdBu_r",
                extent=[-1, 1, -1, 1],
                vmin=-1,
                vmax=1,
            )
            ax.set_title(f"Z{j} {ABERRATION_NAMES[idx]}\n(n={n}, m={m})", fontsize=8)
        else:
            ax.set_visible(False)

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")

    plt.suptitle("Zernike多项式前36项像差分布", fontsize=14)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()
