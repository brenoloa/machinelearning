from __future__ import annotations

import argparse
import numpy as np
from .fa import optimize
from .objectives import sphere, rastrigin, rosenbrock
from .plotting import contour_with_fireflies, animate_fireflies

OBJECTIVES = {
    "sphere": sphere,
    "rastrigin": rastrigin,
    "rosenbrock": rosenbrock,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Algoritmo dos Vaga-lumes (FA) - Otimização contínua"
    )
    p.add_argument("objective", choices=OBJECTIVES.keys(), help="função objetivo")
    p.add_argument("d", type=int, help="dimensionalidade do problema")
    p.add_argument("--n", type=int, default=25, help="tamanho da população")
    p.add_argument("--iters", type=int, default=100, help="número de iterações")
    p.add_argument("--alpha", type=float, default=0.5, help="passo aleatório")
    p.add_argument("--beta0", type=float, default=1.0, help="atratividade base")
    p.add_argument("--gamma", type=float, default=1.0, help="coeficiente de absorção de luz")
    p.add_argument(
        "--minimize",
        action="store_true",
        help="minimizar (padrão)",
    )
    p.add_argument(
        "--maximize",
        action="store_true",
        help="maximizar (inverte o brilho)",
    )
    p.add_argument("--lower", type=float, default=-5.0, help="limite inferior")
    p.add_argument("--upper", type=float, default=5.0, help="limite superior")
    p.add_argument("--seed", type=int, default=None, help="semente aleatória")
    p.add_argument("--plot", action="store_true", help="exibir gráfico 2D (apenas d=2)")
    p.add_argument("--save", type=str, default=None, help="caminho para salvar a figura")
    p.add_argument("--no-show", action="store_true", help="não abrir janela do gráfico")
    p.add_argument("--frames", type=str, default=None, help="caminho .gif para salvar animação (d=2)")
    return p.parse_args()


essential = ["objective", "d"]


def main() -> None:
    args = parse_args()
    minimize = True if args.minimize or not args.maximize else False
    f = OBJECTIVES[args.objective]
    best_x, best_val, info = optimize(
        func=f,
        d=args.d,
        n=args.n,
        iters=args.iters,
        alpha=args.alpha,
        beta0=args.beta0,
        gamma=args.gamma,
        minimize=minimize,
        lower=args.lower,
        upper=args.upper,
        seed=args.seed,
        track_positions=args.plot and args.d == 2,
    )
    print(f"melhor_x: {np.array2string(best_x, precision=4, floatmode='fixed')}")
    print(f"melhor_valor: {best_val:.6f}")

    if args.plot:
        if args.d != 2:
            print("Aviso: plot 2D disponível apenas quando d=2.")
        else:
            positions = info.get("history_positions")
            if positions is None:
                print("Nenhum histórico de posições disponível para plot.")
            else:
                bounds = np.array([[args.lower, args.upper], [args.lower, args.upper]], dtype=float)
                try:
                    contour_with_fireflies(
                        func=f,
                        bounds=bounds,
                        positions_history=positions,
                        title=f"FA - {args.objective} (d=2)",
                        save_path=args.save,
                        show=not args.no_show,
                    )
                    if args.frames:
                        animate_fireflies(
                            func=f,
                            bounds=bounds,
                            positions_history=positions,
                            save_path=args.frames,
                        )
                except RuntimeError as e:
                    print(str(e))
                    print("Instale o extra: pip install .[plot]")


if __name__ == "__main__":
    main()
