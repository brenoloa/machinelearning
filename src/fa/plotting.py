from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional
import numpy as np

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None  # type: ignore
try:
    from matplotlib import animation
except Exception:  # pragma: no cover
    animation = None  # type: ignore

try:
    import PIL  # noqa: F401
except Exception:  # pragma: no cover
    PIL = None  # type: ignore


@dataclass
class PlotConfig:
    levels: int = 30
    cmap: str = "viridis"
    figsize: tuple[int, int] = (6, 5)
    alpha_points: float = 0.8
    s_points: int = 25


def _require_matplotlib():
    if plt is None:
        raise RuntimeError("Matplotlib não está disponível. Instale com 'pip install matplotlib'.")


def contour_with_fireflies(
    func: Callable[[np.ndarray], float],
    bounds: np.ndarray,
    positions_history: np.ndarray,
    title: str = "Firefly Algorithm - 2D",
    save_path: Optional[str] = None,
    show: bool = True,
    config: PlotConfig | None = None,
) -> None:
    _require_matplotlib()
    cfg = config or PlotConfig()

    lo, hi = bounds[:, 0], bounds[:, 1]
    x = np.linspace(lo[0], hi[0], 200)
    y = np.linspace(lo[1], hi[1], 200)
    Xg, Yg = np.meshgrid(x, y)
    Z = np.zeros_like(Xg)
    for i in range(Xg.shape[0]):
        for j in range(Xg.shape[1]):
            Z[i, j] = func(np.array([Xg[i, j], Yg[i, j]]))

    fig, ax = plt.subplots(figsize=cfg.figsize)
    cs = ax.contourf(Xg, Yg, Z, levels=cfg.levels, cmap=cfg.cmap)
    fig.colorbar(cs, ax=ax)

    positions_history = np.asarray(positions_history)
    ax.scatter(
        positions_history[0, :, 0],
        positions_history[0, :, 1],
        c="white",
        edgecolor="black",
        s=cfg.s_points,
        alpha=cfg.alpha_points,
        label="início",
    )
    ax.scatter(
        positions_history[-1, :, 0],
        positions_history[-1, :, 1],
        c="red",
        edgecolor="black",
        s=cfg.s_points,
        alpha=cfg.alpha_points,
        label="final",
    )

    for t in range(1, positions_history.shape[0]):
        ax.plot(
            [positions_history[t - 1, :, 0], positions_history[t, :, 0]],
            [positions_history[t - 1, :, 1], positions_history[t, :, 1]],
            color="black",
            alpha=0.05,
        )

    ax.set_title(title)
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.legend(loc="upper right")
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])

    if save_path:
        fig.tight_layout()
        fig.savefig(save_path, dpi=150)
    if show:
        plt.show()
    plt.close(fig)


def animate_fireflies(
    func: Callable[[np.ndarray], float],
    bounds: np.ndarray,
    positions_history: np.ndarray,
    save_path: str,
    config: PlotConfig | None = None,
    interval_ms: int = 120,
) -> None:
    _require_matplotlib()
    if animation is None:
        raise RuntimeError("Matplotlib.animation não está disponível. Atualize o matplotlib.")
    if PIL is None:
        raise RuntimeError("Pillow não está disponível. Instale com 'pip install pillow' ou 'pip install .[plot]'.")

    cfg = config or PlotConfig()
    lo, hi = bounds[:, 0], bounds[:, 1]
    x = np.linspace(lo[0], hi[0], 200)
    y = np.linspace(lo[1], hi[1], 200)
    Xg, Yg = np.meshgrid(x, y)
    Z = np.zeros_like(Xg)
    for i in range(Xg.shape[0]):
        for j in range(Xg.shape[1]):
            Z[i, j] = func(np.array([Xg[i, j], Yg[i, j]]))

    fig, ax = plt.subplots(figsize=cfg.figsize)
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    cs = ax.contourf(Xg, Yg, Z, levels=cfg.levels, cmap=cfg.cmap)
    fig.colorbar(cs, ax=ax)
    scat = ax.scatter([], [], c="red", edgecolor="black", s=cfg.s_points, alpha=cfg.alpha_points)
    ax.set_title("FA - trajetória (2D)")
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")

    positions_history = np.asarray(positions_history)

    def init():
        scat.set_offsets(np.empty((0, 2)))
        return (scat,)

    def update(frame: int):
        pts = positions_history[frame]
        scat.set_offsets(pts[:, :2])
        return (scat,)

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=positions_history.shape[0],
        init_func=init,
        interval=interval_ms,
        blit=True,
        repeat=False,
    )

    writer = animation.PillowWriter(fps=max(1, int(1000 / interval_ms)))
    ani.save(save_path, writer=writer)
    plt.close(fig)
