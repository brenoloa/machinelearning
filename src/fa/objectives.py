from __future__ import annotations

import numpy as np


def sphere(x: np.ndarray) -> float:
    """Sphere: soma dos quadrados. Mínimo global em 0."""
    return float(np.sum(x**2))


def rastrigin(x: np.ndarray) -> float:
    """multimodal com muitos mínimos locais (mais difícil)."""
    A = 10.0
    x = np.asarray(x)
    return float(A * x.size + np.sum(x**2 - A * np.cos(2 * np.pi * x)))


def rosenbrock(x: np.ndarray) -> float:
    """(vale do banana): mínimo global em (1, ..., 1)."""
    x = np.asarray(x)
    return float(np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2))
