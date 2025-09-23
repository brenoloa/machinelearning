from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Tuple, Dict, Any, List
import numpy as np

ObjectiveFn = Callable[[np.ndarray], float]


def _as_bounds(lower: float, upper: float, d: int) -> np.ndarray:
    """Cria um array de limites (d, 2) com [lower, upper] por dimensão."""
    b = np.empty((d, 2), dtype=float)
    b[:, 0] = lower
    b[:, 1] = upper
    return b


@dataclass
class FAParams:
    n: int = 25
    d: int = 2
    alpha: float = 0.5
    beta0: float = 1.0
    gamma: float = 1.0
    iters: int = 100
    minimize: bool = True
    seed: int | None = None
    lower: float = -5.0
    upper: float = 5.0


class Firefly:
    def __init__(
        self,
        func: ObjectiveFn,
        bounds: np.ndarray | None = None,
        params: FAParams | None = None,
    ) -> None:
        """Prepara o estado do algoritmo e inicializa a população dentro dos limites."""
        self.func = func
        self.params = params or FAParams()
        self.rng = np.random.default_rng(self.params.seed)
        self.d = self.params.d
        self.n = self.params.n
        self.alpha = self.params.alpha
        self.beta0 = self.params.beta0
        self.gamma = self.params.gamma
        self.iters = self.params.iters
        self.minimize = self.params.minimize
        if bounds is None:
            self.bounds = _as_bounds(self.params.lower, self.params.upper, self.d)
        else:
            self.bounds = np.asarray(bounds, dtype=float)
            assert self.bounds.shape == (self.d, 2)
        self._init_population()

    def _init_population(self) -> None:
        """Inicializa X ~ Uniform(bounds); avalia f, brilho e o índice do melhor."""
        lo = self.bounds[:, 0]
        hi = self.bounds[:, 1]
        self.X = self.rng.uniform(lo, hi, size=(self.n, self.d))
        self.values = np.apply_along_axis(self.func, 1, self.X)
        self.I = self._brightness(self.values)
        self.best_idx = int(np.argmax(self.I))

    def _brightness(self, fvals: np.ndarray) -> np.ndarray:
        """Mapeia valores da função para intensidade: -f para minimizar, f para maximizar."""
        return -fvals if self.minimize else fvals

    def _move_towards(self, xi: np.ndarray, xj: np.ndarray, beta: float) -> np.ndarray:
        """Retorna xi movido em direção a xj com atratividade beta e ruído aleatório alpha."""
        step_attract = beta * (xj - xi)
        step_random = self.alpha * (self.rng.random(self.d) - 0.5)
        return xi + step_attract + step_random

    def _clip(self, X: np.ndarray) -> np.ndarray:
        """Recorta as posições para os limites [lower, upper] em cada dimensão."""
        return np.clip(X, self.bounds[:, 0], self.bounds[:, 1])

    def step(self) -> None:
        """Uma iteração do FA: move cada i em direção aos j mais brilhantes e aceita se a intensidade melhora."""
        X_new = self.X.copy()
        for i in range(self.n):
            for j in range(self.n):
                if self.I[j] > self.I[i]:
                    rij = np.linalg.norm(self.X[i] - self.X[j])
                    beta = self.beta0 * np.exp(-self.gamma * (rij ** 2))
                    X_new[i] = self._move_towards(self.X[i], self.X[j], beta)
        X_new = self._clip(X_new)
        vals_new = np.apply_along_axis(self.func, 1, X_new)
        I_new = self._brightness(vals_new)
        for i in range(self.n):
            if I_new[i] > self.I[i]:
                self.X[i] = X_new[i]
                self.values[i] = vals_new[i]
                self.I[i] = I_new[i]
        self.best_idx = int(np.argmax(self.I))

    def run(self, track_positions: bool = False) -> Tuple[np.ndarray, float, Dict[str, Any]]:
        """Executa por 'iters' passos; opcionalmente coleta posições. Retorna best_x, best_val e info."""
        history_best: List[float] = []
        history_positions: List[np.ndarray] | None = [] if track_positions else None
        if track_positions:
            history_positions.append(self.X.copy())
        for _ in range(self.iters):
            self.step()
            if track_positions:
                history_positions.append(self.X.copy())
            history_best.append(self.values[self.best_idx])
        info: Dict[str, Any] = {
            "best_idx": self.best_idx,
            "history_best": np.asarray(history_best),
            "best_intensity": float(self.I[self.best_idx]),
        }
        if track_positions:
            info["history_positions"] = np.asarray(history_positions)
        return self.X[self.best_idx].copy(), float(self.values[self.best_idx]), info


def optimize(
    func: ObjectiveFn,
    d: int,
    n: int = 25,
    iters: int = 100,
    alpha: float = 0.5,
    beta0: float = 1.0,
    gamma: float = 1.0,
    minimize: bool = True,
    lower: float = -5.0,
    upper: float = 5.0,
    seed: int | None = None,
    track_positions: bool = False,
) -> Tuple[np.ndarray, float, Dict[str, Any]]:
    """Atalho conveniente: configura o FA com os parâmetros dados e executa a otimização."""
    params = FAParams(
        n=n,
        d=d,
        alpha=alpha,
        beta0=beta0,
        gamma=gamma,
        iters=iters,
        minimize=minimize,
        seed=seed,
        lower=lower,
        upper=upper,
    )
    fa = Firefly(func=func, bounds=None, params=params)
    return fa.run(track_positions=track_positions)
