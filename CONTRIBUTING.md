# Contribuindo

Obrigado pelo interesse! Este é um projeto pequeno e o fluxo é direto.

## Ambiente

```bash
git clone https://github.com/denisvick-dev/brasfoot.git
cd brasfoot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
playwright install chromium   # só se for usar o shots.py
streamlit run app.py
```

## Antes de abrir um PR

```bash
ruff check .      # lint (F, E9, B, UP, I)
pyright .         # tipos — tem que dar "0 errors"
pytest            # testes
python main.py 156 1   # temporada completa, sem exceção
```

O CI repete os três primeiros em Python 3.11 e 3.12.

## Padrões do código

- **Sem Streamlit em `game/`**: a simulação precisa rodar no terminal
  (`main.py`, `diagnostico.py`, testes). Interface é só em `ui/`.
- **Uma tela por módulo em `ui/`**; o roteamento fica no `app.py`.
- **Dataclasses** em `game/modelos.py` para tudo que é persistido.
- **Nada de mágica em `try/except`**: erro de dado deve aparecer no teste.
- Comentários e docstrings em português, sem acento em nomes de código.

## Escudos

Arquivos em `assets/escudos/<SIGLA>.png`, com a sigla exatamente como está em
`game/clubes.py`. PNG 128×128 com fundo transparente. Confira com:

```python
from game.escudos import faltando, orfaos

faltando(), orfaos()  # os dois devem voltar []
```

## Commits e PRs

- Commits curtos, no imperativo (`Corrige escalação com jogador suspenso`).
- Um PR por assunto, com uma linha explicando o "antes" e o "depois".
- Se mexer no motor, rode `python diagnostico.py` e cole os números no PR.
