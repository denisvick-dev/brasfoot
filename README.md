# ⚽ Brasfoot

[![CI](https://github.com/denisvick-dev/brasfoot/actions/workflows/ci.yml/badge.svg)](https://github.com/denisvick-dev/brasfoot/actions/workflows/ci.yml)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

Gerenciador de futebol brasileiro feito em Python + Streamlit: você assume um
clube, monta o time, joga a temporada inteira e tenta chegar à Série A.

O banco cobre **156 clubes reais** das Séries A, B, C e D, com escudo, cores,
estádio, torcida, orçamento e elenco — mais a **Copa do Brasil** (128 clubes),
três **torneios regionais** e a **Supercopa**.

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate   # opcional
pip install -r requirements.txt

streamlit run app.py        # http://localhost:8501
```

No terminal, sem interface:

```bash
python main.py 156          # temporada completa com as quatro divisões
python diagnostico.py       # calibragem do motor (gols, empates, mando de campo)
```

## O que dá para fazer no jogo

- **Escolher ou criar** seu clube (escudo, cores, estádio, orçamento e elenco).
- **Elenco e tática**: formação, estilo de jogo (retranca ↔ ataque total),
  escalação manual ou automática, energia, cartões, lesões e suspensões.
- **Jogar rodada a rodada**, com **relógio de 0' a 90'+ em barra de progresso**
  (os gols aparecem no minuto em que saíram, **piscando em vermelho** com
  **som de gol**), narração do jogo e **todos os placares da rodada** na mesma
  tela, separados por competição. Cada simulação sorteia resultados novos — o
  `Sorteio #` fica visível na tela.
- **Quatro divisões** com regulamentos diferentes (turno e returno, turno único
  e mata-mata), acesso e descenso ao fim da temporada.
- **Copa do Brasil**, **regionais** e **Supercopa** no mesmo calendário.
- **Mercado de transferências**: contratar, vender, salários, valor de mercado.
- **Finanças**: bilheteria, cota de TV, patrocínio, folha salarial, prêmios por
  posição e extrato completo de cada lançamento (tela própria no menu).
- **Ranking de pontos acumulado**: histórico de todos os clubes (pontos, jogos,
  V/E/D, gols, média e títulos) somando temporada após temporada, mais a tabela
  do ano corrente com as quatro divisões juntas.
- **Objetivo da diretoria** por série, com situação atualizada rodada a rodada.
- **Artilharia, notícias e fim de temporada** com balanço do ano.

## Estrutura do repositório

```
app.py                 ponto de entrada (configura a página e roteia as telas)
ui/                    interface Streamlit
  estilos.py             tema, CSS e configuração da página
  apoio.py               leitura do estado do jogo, formatação e tabelas
  inicial.py             tela inicial (escolher/criar clube)
  sidebar.py             menu lateral
  painel.py              painel do clube
  elenco.py              elenco, salários, lesões e suspensões
  tatica.py              formação, estilo e escalação
  jogar.py               pré-jogo, partida e fim de temporada
  competicoes.py         classificação, calendário e resultados
  mercado.py             transferências
  financas.py            caixa, folha, receitas, despesas e extrato
  criador.py             criador de clubes, jogadores e competições
  competicao.py          detalhes de competição personalizada
  ranking.py             ranking de pontos acumulados
  noticias.py            central de notícias
game/                  simulação (sem Streamlit)
  modelos.py             Jogador, Time, Partida, Gol, Noticia
  clubes.py              fichas dos 156 clubes
  banco_dados.py         elencos e consultas
  jogo_engine.py         motor de partida
  campeonato.py          League (pontos corridos)
  divisao.py             regulamento de cada série
  copa.py                Copa do Brasil
  regional.py            torneios regionais
  piramide.py            temporada completa, acesso e descenso
  mercado.py             transferências
  financas.py            extrato, resumo e premiação
  rotina.py              energia, lesões, suspensões e salários entre rodadas
  diretoria.py           objetivo da diretoria por série
  ranking.py             pontos acumulados entre temporadas
  criador.py             criação e persistência de clubes/jogadores
  escudos.py             escudos embutidos como data URI
  persistencia.py        dados/ em JSON
assets/escudos/        156 escudos (PNG)
scripts/               utilitários (gera escudo genérico)
docs/                  documentação detalhada
tests/                 suíte pytest
```

## Documentação

| Documento | Conteúdo |
| --- | --- |
| [docs/arquitetura.md](docs/arquitetura.md) | módulos, fluxo da temporada e da interface |
| [docs/competicoes.md](docs/competicoes.md) | regulamentos das séries, copa, regionais e supercopa |
| [docs/motor.md](docs/motor.md) | como a partida é simulada e constantes tunáveis |
| [docs/escudos.md](docs/escudos.md) | como os escudos são carregados e trocados |
| [docs/financas.md](docs/financas.md) | dinheiro, rotina entre rodadas e diretoria |
| [docs/criador.md](docs/criador.md) | criador de campeonatos |
| [docs/historico.md](docs/historico.md) | correções aplicadas ao longo do projeto |
| [docs/desenvolvimento.md](docs/desenvolvimento.md) | ambiente, testes, lint e CI |
| [CHANGELOG.md](CHANGELOG.md) | versões |
| [CONTRIBUTING.md](CONTRIBUTING.md) | como contribuir |

## Desenvolvimento

```bash
pip install -r requirements-dev.txt
ruff check .      # lint
pyright .         # tipos (mesmo resultado do Pylance)
pytest            # 108 testes (determinístico)
```

O CI roda lint, tipos e testes em Python 3.11 e 3.12 a cada push e pull request.

## Licença

Código sob [MIT](LICENSE). Os escudos em `assets/escudos/` são marcas dos
respectivos clubes e aparecem aqui apenas para identificar os times no jogo.
