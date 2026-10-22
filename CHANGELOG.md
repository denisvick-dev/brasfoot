# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
O projeto usa versionamento semântico.

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
