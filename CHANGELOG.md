# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
O projeto usa versionamento semântico.

## [2.1.0] — 2026-10-22

### Adicionado

- **Tela de finanças** (`ui/financas.py`): caixa, folha, receitas, saldo,
  resumo por tipo e extrato dos últimos lançamentos.
- **Extrato financeiro** por clube (`game/financas.py`): bilheteria, cota de TV,
  patrocínio, salários, transferências e premiação, com limite de 400 linhas.
- **Cota de TV por rodada e patrocínio mensal** por divisão, para os clubes
  pequenos não fecharem a temporada no vermelho.
- **Premiação de fim de temporada** por posição, Copa do Brasil e Supercopa.
- **Rotina entre rodadas** (`game/rotina.py`) compartilhada por `League` e
  `Piramide`: energia, cura de lesão, cumprimento de suspensão, salários e
  re-escalação.
- **Objetivo da diretoria** por série (`game/diretoria.py`), no painel e na
  tela de finanças.
- **Barra de status** no topo, estilo Brasfoot: clube, série, rodada, posição
  e caixa.
- Testes de finanças, rotina e diretoria (62 no total).

### Corrigido

- Na pirâmide (jogo principal) a energia dos jogadores **nunca** era recuperada,
  as lesões não saravam, as suspensões não eram cumpridas e os salários não eram
  cobrados — a rotina só existia no campeonato avulso.
- Cartão não zerava o contador de amarelos após a suspensão, o que suspenderia o
  jogador de novo no jogo seguinte.
- Suspensão passa a durar exatamente um jogo (antes sumia em sorteio de 50%).

## [2.0.0] — 2026-10-22

### Adicionado

- **156 clubes reais** das Séries A, B, C e D, com escudo, cores, estádio,
  torcida, orçamento, fundação e rival.
- **Pirâmide completa**: quatro divisões com regulamentos próprios (turno e
  returno, turno único e mata-mata), acesso e descenso.
- **Copa do Brasil** com 128 clubes em mata-mata de ida e volta.
- **Torneios regionais** (Rio-SP, Sul-Minas, Copa do Nordeste) e **Supercopa**.
- **Criador** de clubes, jogadores e competições personalizadas.
- **Escudos de todos os 156 clubes** em PNG, embutidos como data URI.
- Tema visual do app, com tabelas, cartões de clube e narração da partida.
- Suíte de testes com `pytest`, lint com `ruff`, tipos com `pyright` e CI.
- Documentação em `docs/` (arquitetura, competições, motor, escudos, criador).

### Alterado

- `app.py` (4 mil linhas) dividido no pacote `ui/`, uma tela por módulo.
- Configuração centralizada em `pyproject.toml` (ruff, pytest e metadados).
- `game/dados.py` e `game/liga.py` (aliases antigos) removidos; os nomes atuais
  são `game/banco_dados.py` e `game/campeonato.py`.

### Corrigido

- Escudos com nomes fora do padrão (19 arquivos sem clube, 17 clubes sem escudo)
  e siglas duplicadas (`FER`, `SBR`).
- Goleador contava dois jogos por partida; artilharia tipada errado.
- Classificação de pontos corridos aparecia zerada; mata-mata estourava com BYE.
- Diversos erros de lint e de tipagem (ver `docs/historico.md`).

## [1.0.0] — 2026-09

- Primeira versão jogável: 20 clubes, pontos corridos, mercado e interface
  Streamlit.
