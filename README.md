# Futebol Manager — projeto integrado

```
app.py               interface Streamlit (Brasfoot)
main.py              demo: roda uma temporada inteira no terminal
diagnostico.py       calibração: mede o motor contra metas do futebol real
game/__init__.py
game/modelos.py      Jogador, Time, Partida, Noticia
game/banco_dados.py  base de clubes (61 times em 3 divisões) + geração de elencos
game/dados.py        alias -> game.banco_dados (compatibilidade)
game/jogo_engine.py  MatchEngine (simulação de partidas)
game/campeonato.py   League (calendário, rodadas, classificação)
game/mercado.py      Market (transferências)
```

## Como rodar

```bash
streamlit run app.py      # interface do jogo
# http://localhost:8501

python main.py            # Brasileirão com 20 clubes (Série A)
python main.py 24         # 24 clubes
python main.py 61         # banco inteiro (122 rodadas, ~1,5s)
python main.py 20 7       # semente 7 (reproduzível)

python diagnostico.py     # mede gols/jogo, empates, mando de campo etc.
python shots.py           # screenshots das telas ( precisa do app rodando + playwright )
```

## Banco de dados

61 clubes em 3 divisões: 20 na Série A, 20 na Série B, 21 na Série C/regional.
Cada clube tem ficha completa (`Clube`): cidade, estado, escudo, cores, faixa de
força do elenco, finanças, torcida, reputação, **divisão, estádio, capacidade,
fundação e rival**.

```python
criar_times()                            # 20 clubes (padrão antigo)
criar_times(24)                          # A + os melhores da B
criar_times(divisao="B")                 # só uma divisão
criar_times(None)                        # todos os 61
criar_times(32, aleatorio=True, semente=7)
criar_todas_divisoes()                   # {"A": [...], "B": [...], "C": [...]}
buscar_clube("FLA")                      # ficha completa do clube
```

## Correções aplicadas

| Arquivo | Problema | Correção |
|---|---|---|
| `mercado.py` | `from game.banco_dados import ...` quebrava (módulo se chamava `dados`) | banco renomeado para `banco_dados.py`; `dados.py` virou alias |
| `jogo_engine.py` | goleador contava **2 jogos** por partida | contagem única em `_atualizar_stats` |
| `campeonato.py` | `League([])` gerava calendário vazio e travava depois | validação: mínimo de 2 times |
| `campeonato.py` | `artilharia()` tipada como `list[Jogador]`, mas devolve tuplas | tipo corrigido para `list[tuple[Jogador, str]]` |
| `mercado.py` | elenco não era reescalado após compra/venda | `auto_escalar()` após a transferência |

## Rebalanceamento do motor

**Causa raiz do campeonato aleatório:** a força dos times só decidia *quem*
atacava; a conversão em gol era 15% fixa, independente da qualidade do ataque e
da defesa. Agora cada chance é resolvida por **ataque x defesa**
(`CONVERSAO * ataque / (ataque + defesa)`), com bônus de mando de campo, moral,
energia e tática.

Medido em 5 temporadas de 20 clubes (`diagnostico.py`):

| Métrica | Antes | Depois | Meta |
|---|---|---|---|
| Gols por jogo | 0,85 | **2,52** | 2,2 – 2,7 |
| Empates | 49,3% | **25,3%** | 22 – 30% |
| Vitórias do mandante | 26,1% | **44,2%** | 42 – 50% |
| Correlação overall x pontos | +0,19 | **+0,71** | ≥ 0,55 |
| Artilheiro (38 rodadas) | 9 gols | **15 gols** | — |
| Energia média (sistema inerte) | 97 | **77** | — |
| Times com caixa negativo (61 clubes) | 29 | **4** | — |
| Jogos com público acima da capacidade | 227 | **0** | — |

Outras mudanças:

- **Público** agora respeita a capacidade do estádio (`capacidade` da ficha do
  clube) — antes o Vasco lotava São Januário com 35 mil lugares.
- **Renda** = bilheteria + cota de TV (por torcida), paga ao mandante.
- **Salários** saem a cada 6 rodadas (≈ 1 folha por mês), em vez de a cada 4 —
  era o que quebrava os clubes pequenos.
- **Energia** pesa de verdade: desgaste 20–35, recuperação 12–26, e
  `Time.auto_escalar(considerar_energia=True)` escala por
  `overall * (0,6 + 0,4 * energia/100)`. Resultado: 404 de 440 jogadores são
  usados na temporada (rodízio real).
- **Tática** tem custo: atacar mais melhora o ataque e piora a defesa.

## Constantes tunáveis

Tudo está em `MatchEngine` (topo da classe), e `diagnostico.py` mostra se cada
métrica está na meta:

```python
CHANCE_EVENTO = 0.12          # eventos por minuto
PESOS_EVENTO = {"chance": 58, "cartao": 8, "falta": 14, "escanteio": 20}
CONVERSAO = 0.74              # ~0,37 de conversão em confronto equilibrado
BONUS_CASA_ATAQUE = 11.0 / BONUS_CASA_DEFESA = 5.0 / BONUS_CASA_GERAL = 11.0
PESO_TATICA_ATAQUE = 0.22 / PESO_TATICA_DEFESA = 0.18
DESGASTE 20–35 / RECUPERACAO 12–26 / PROB_LESAO = 0.03
INGRESSO 40–90 / COTA_TV_POR_TORCEDOR = 12_000 / RODADAS_POR_MES = 6
```

Para recalibrar, altere a constante e rode `python diagnostico.py`.

## Observações

- Com 61 clubes o round-robin usa **BYE** (rodada de folga) e a temporada tem
  122 rodadas — `proximo_adversario()` devolve `"Folga"` nesses casos.
- Numa temporada longa (61 clubes), 3 ou 4 clubes pequenos podem terminar com
  caixa negativo; é o comportamento esperado da régua econômica atual.
- `is_player_home` / `is_player_away` continuam sem uso dentro de `simular()` —
  ficaram disponíveis para a interface (narração, escalação do jogador).

## Interface (Streamlit)

`app.py` é a interface do jogo. O app importa `from game.liga import League`;
como a implementação mora em `game/campeonato`, existe `game/liga.py` que só
reexporta o módulo (mesmo truque de `game/dados.py`), então qualquer um dos
dois nomes funciona.

**Tipografia**

| Fonte | Uso |
|---|---|
| Plus Jakarta Sans | títulos, placares e números de destaque |
| Manrope | interface, textos e botões |
| Inter | tabelas e dados (com `tabular-nums` para alinhar colunas) |

As fontes vêm do Google Fonts via `<link>`; se não carregarem, o CSS cai para
`system-ui` sem quebrar o layout.

**Componentes visuais**

- Hero em gradiente com o escudo e o resumo da temporada.
- Cards de clube com as cores de cada time (`cor_primaria` / `cor_secundaria`).
- Tabelas HTML (classificação, elenco, artilharia) com zebra, zona colorida
  (Libertadores / Sul-Americana / rebaixamento) e destaque do seu time.
- Campo tático com grama listrada, linha de meio e círculo central, e chips de
  jogador com overall e energia.
- Placar em gradiente por resultado e narração em linha do tempo (gol, amarelo,
  vermelho, defesa).
- Barras de energia em gradiente e selos de status (disponível / lesionado /
  suspenso).
