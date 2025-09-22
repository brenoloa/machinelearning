# Algoritmo dos Vaga-lumes (Firefly Algorithm)

Implementação simples e didática do Algoritmo dos Vaga-lumes (FA) em Python, usando apenas NumPy (e Matplotlib/Pillow opcionais para plots).

## Conceitos
- Atratividade aumenta com o brilho; todos são unissexuais.
- Brilho definido pela função objetivo (minimização por padrão).
- Movimento: vaga-lume menos brilhante move em direção ao mais brilhante proporcionalmente à atratividade; caso contrário, passeio aleatório.

## Instalação
Requer Python 3.9+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Para gráficos e GIFs:
```powershell
pip install .[plot]
```

## Uso rápido (CLI)
```powershell
# Minimizar Sphere em 5D
python -m fa sphere 5 --iters 200 --n 30 --seed 42

# Minimizar Rastrigin em 10D
python -m fa rastrigin 10 --iters 300 --n 40 --alpha 0.3 --seed 7

# Maximizar (ex.: -sphere)
python -m fa sphere 5 --maximize --seed 1

# Visualização 2D (PNG)
python -m fa sphere 2 --iters 100 --n 25 --seed 7 --plot --save fig-fa-sphere-2d.png --no-show

# Animação GIF (2D)
python -m fa sphere 2 --iters 60 --n 25 --seed 7 --plot --frames fa-sphere-2d.gif --no-show
```

Parâmetros principais:
- `d`: dimensionalidade; `--n`: tamanho da população; `--iters`: iterações.
- `--alpha`: passo aleatório; `--beta0`: atratividade base; `--gamma`: atenuação da luz.
- `--lower`/`--upper`: limites do espaço de busca.
- `--minimize` (padrão) ou `--maximize`.
- `--plot`: desenha contorno (apenas d=2) e posições dos vaga-lumes.
- `--save`: caminho para salvar a figura; `--no-show` evita abrir janela.
- `--frames`: caminho .gif para salvar animação 2D.

## API
```python
import numpy as np
from fa import optimize, sphere

best_x, best_val, info = optimize(
	func=sphere, d=5, n=30, iters=200, seed=42
)
```

`info["history_best"]` contém a evolução do melhor valor (sempre que `d=2` e `track_positions=True`, também há `info["history_positions"]`).

## Notas
- Código focado em clareza para fins educacionais.
- Somente NumPy é usado no núcleo; Matplotlib/Pillow são opcionais.
