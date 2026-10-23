# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
O projeto usa versionamento semântico.

## [2.2.0] — 2026-10-23

### Adicionado

- **Rodada ao vivo, com relógio**: ao simular, a tela mostra o tempo correndo de
  `0'` a `90'+` numa barra de progresso, com os gols aparecendo no minuto em que
  aconteceram — jogo do seu clube em destaque e os demais jogos da rodada
  atualizando junto, no estilo Brasfoot.
- **Velocidade do relógio** na tela de jogo: `⏩ Rápida` (2 s), `▶️ Normal`
  (5 s) e `🐢 Detalhada` (10 s). A simulação em si continua instantânea; o que
  muda é quanto tempo a revelação dura.
- **Sorteio da rodada**: cada simulação sorteia um número (`Sorteio #a3f9c2`),
  mostrado na tela e usado como semente do motor. Serve para dois fins: deixar
  claro que **os resultados são sorteados a cada rodada** e permitir reproduzir
  exatamente uma rodada estranha.
- `Partida.gols` (`Gol`: minuto, clube, jogador e assistência) e
  `Partida.placar_ate(minuto)`, base do replay com relógio.
- `ui/ao_vivo.py` com as funções puras do relógio (minuto final, passos da
  animação, placar por minuto e o HTML do painel).
- 12 testes novos (80 no total): relógio, acréscimos, placar revelado aos
  poucos, sorteio diferente a cada rodada e um teste que garante que o placar
  não se repete sempre.

### Alterado

- `ui/jogar.py` não usa mais o "sleep" de 0,7 s para a barra não piscar: a
  própria animação do relógio preenche o tempo.

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
- **Barra de carregamento** ao simular a rodada: mostra a competição em
  andamento (Série A, B, C, D, Copa, regionais) e o jogo sendo simulado no
  campeonato avulso, com um instante de pausa para dar para acompanhar.
- **Placares da rodada** na tela de jogo: todos os jogos da rodada, agrupados
  por competição (estilo Brasfoot), com escudo, mandante, visitante e placar.
- Testes de finanças, rotina, diretoria e progresso da simulação (68 no total).
- Teste de desempate da classificação (pontos → vitórias → saldo → gols pró).

### Corrigido

- Suíte de testes **determinística**: o `random` global é semeado antes de cada
  teste (`BRASFOOT_SEED`, padrão `2026`). Antes, o teste de classificação
  falhava de vez em quando (o CI ficava vermelho sem mudança de código) porque a
  ordenação usa também vitórias e gols pró, e o teste só comparava pontos/saldo.
- Teste de cartões não tinha asserção de verdade (`... or True`); agora confere
  que só fica suspenso quem levou 3 amarelos ou vermelho.
- Teste do mando de campo falhava em ~1% das sementes (120 jogos era pouco para
  separar bônus de casa de força do elenco). Agora cada confronto é jogado nos
  dois sentidos, com 400 partidas, e há um teste determinístico que confere o
  bônus direto nas funções de força.
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
