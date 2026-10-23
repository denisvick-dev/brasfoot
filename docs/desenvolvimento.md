# Desenvolvimento

## Requisitos

- Python 3.11 ou mais novo
- Streamlit (vem do `requirements.txt`)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt   # inclui ruff, pyright, pytest e playwright
```

## Rodando

```bash
streamlit run app.py      # interface do jogo, em http://localhost:8501
python main.py            # Brasileirão com 20 clubes (Série A)
python main.py 24         # 24 clubes
python main.py 156        # banco inteiro, 4 divisões
python main.py 20 7       # semente 7 (reproduzível)
python diagnostico.py     # mede gols/jogo, empates, mando de campo etc.
python shots.py           # screenshots das telas (app rodando + playwright)
```

## Testes

```bash
pytest                          # suíte completa (93 testes, ~70 s)
pytest -k piramide              # só um arquivo/tema
pytest -v                       # nome de cada teste
BRASFOOT_SEED=1234 pytest       # reproduz a semente usada na investigação
```

A suíte é **determinística**: o fixture `semente_fixa` (em `tests/conftest.py`)
semeia o `random` global antes de cada teste com `BRASFOOT_SEED` (padrão
`2026`). Sem isso, cada execução gerava um universo diferente e o teste de
classificação falhava de vez em quando — o que apareceu como "CI vermelho sem
motivo". Para caçar testes frágeis, varra várias sementes:

```bash
bash scripts/testar_sementes.sh                 # sementes 1..5 (o que o CI roda)
bash scripts/testar_sementes.sh $(seq 1 50)     # varredura longa
```

O script quebra em anotação do GitHub (`::error title=Semente N::teste`) quando
uma semente falha, então dá para ver no PR qual teste caiu sem abrir o log.

A suíte cobre modelos, banco de clubes e escudos, campeonato, copa, pirâmide
(acesso/descenso), motor, mercado, finanças/rotina, diretoria,
criador/persistência, progresso da simulação e um smoke test das telas com `streamlit.testing.v1.AppTest` (o app precisa montar sem exceção).

## Lint e tipos

```bash
ruff check .     # F, E9, B, UP, I — configurado em pyproject.toml
pyright .        # 0 errors, 0 warnings
```

A configuração do Ruff fica no `pyproject.toml` **de propósito**: sem ela, o
resultado muda conforme a versão instalada (versões novas ligam regras de
preview). O Pyright usa o `pyrightconfig.json`, que é o mesmo arquivo lido pelo
Pylance no VS Code.

## Integração contínua

`.github/workflows/ci.yml` roda em cada push na `main` e em todo pull request:

1. `ruff check .`
2. `pyright .`
3. `pytest`

Em Python 3.11 e 3.12.

## Publicando

O app é um Streamlit puro — qualquer serviço que rode
`streamlit run app.py` (Streamlit Community Cloud, Render, Fly.io) serve.
Basta apontar para o `requirements.txt`.
