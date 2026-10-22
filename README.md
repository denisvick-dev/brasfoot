# Futebol Manager — projeto integrado

```
app.py               interface Streamlit (Brasfoot)
main.py              demo: roda uma temporada inteira no terminal
diagnostico.py       calibração: mede o motor contra metas do futebol real
game/__init__.py
game/modelos.py      Jogador, Time, Partida, Noticia
game/clubes.py       fichas dos 156 clubes (Séries A, B, C e D)
game/banco_dados.py  elencos a partir das fichas + API de consulta
game/piramide.py     temporada com as 4 divisões + acesso e descenso
game/divisao.py     regulamento de cada série: turno único, grupos, mata-mata
game/escudos.py      escudos de assets/escudos/ embutidos como data URI
assets/escudos/      escudos dos 156 clubes (PNG oficial ou SVG)
scripts/gerar_escudos.py  desenha escudo genérico para clube sem imagem
game/dados.py        alias -> game.banco_dados (compatibilidade)
game/jogo_engine.py  MatchEngine (simulação de partidas)
game/campeonato.py   League (calendário, rodadas, classificação)
game/mercado.py      Market (transferências)
```

## Como rodar

```bash
pip install -r requirements.txt   # streamlit + playwright

streamlit run app.py      # interface do jogo
# http://localhost:8501

python main.py            # Brasileirão com 20 clubes (Série A)
python main.py 24         # 24 clubes
python main.py 156        # banco inteiro, 4 divisões
python main.py 20 7       # semente 7 (reproduzível)

python diagnostico.py     # mede gols/jogo, empates, mando de campo etc.
python shots.py           # screenshots das telas ( precisa do app rodando + playwright )
```

## Banco de dados

156 clubes em 4 divisões, a pirâmide do futebol brasileiro de 2026:

| Divisão | Clubes |
|---|---|
| Série A | 20 |
| Série B | 20 |
| Série C | 20 |
| Série D | 96 |

Cada clube tem ficha completa (`Clube`): cidade, estado, escudo, cores, faixa de
força do elenco, finanças, torcida, reputação, **divisão, estádio, capacidade,
fundação e rival**. As fichas ficam em `game/clubes.py`; `game/banco_dados.py`
transforma ficha em `Time` (gerando o elenco).

```python
criar_times()                            # 20 clubes (padrão antigo)
criar_times(24)                          # A + os melhores da B
criar_times(divisao="B")                 # só uma divisão
criar_times(None)                        # todos os 156
criar_times(32, aleatorio=True, semente=7)
criar_todas_divisoes()                   # {"A": [...], "B": [...], "C": [...], "D": [...]}
buscar_clube("FLA")                      # ficha completa do clube
clubes_por_divisao("D")                  # fichas de uma divisão
resumo_banco()                           # contagem por divisão
```

Na interface, o seletor **Divisão** da tela inicial define qual campeonato é
disputado (Série A por padrão); o banco inteiro fica carregado em memória.

## Regulamentos das divisões

Cada série tem o seu formato (`game/divisao.py`), como no futebol brasileiro —
a tela **🏆 Classificações** mostra as tabelas de cada fase e o 📖 Regulamento.

**Séries A e B (20 clubes, 27 rodadas)**

1. Primeira fase: turno único, todos contra todos (19 rodadas).
2. Os 8 melhores passam para a segunda fase, em 2 grupos de 4
   (1º, 4º, 5º e 8º num grupo; 2º, 3º, 6º e 7º no outro), turno e returno
   (6 rodadas). Os dois primeiros de cada grupo avançam.
3. Final em ida e volta entre os líderes dos grupos.
4. **Série B:** os dois primeiros de cada grupo garantem o acesso
   (4 vagas) — a final vale o título.
5. Os 4 últimos da primeira fase caem para a série de baixo.

**Série C (20 clubes, 19 rodadas)**

Turno único; o líder é campeão e os 4 primeiros sobem para a Série B. Os 4
últimos descem para a Série D.

**Série D (96 clubes, 15 rodadas)**

16 grupos de 6 em turno único (5 rodadas); os 2 melhores de cada grupo avançam
para o mata-mata em ida e volta (16-avos → oitavas → quartas → semifinal →
final, 10 rodadas). Os 4 semifinalistas sobem para a Série C; não há descenso.

**Copa do Brasil (128 clubes)**

Atalho em 🛠️ Criador → 🏆 **Copa do Brasil**: mata-mata em ida e volta da
primeira fase até a final (sem jogo único), com os 128 clubes de melhor
reputação das quatro divisões.

## Escudos

Os escudos ficam em `assets/escudos/` com o nome da sigla do clube —
`FLA.png`, `ABE.svg`… — e a interface mostra a imagem no lugar do emoji
(cartões de clube, tabelas, títulos e confrontos). Como o app injeta HTML no
`st.markdown`, a imagem é embutida como *data URI* (cache em `game/escudos.py`),
sem servidor de estáticos.

| Origem | Clubes |
|---|---|
| PNG oficial | 111 |
| SVG importado (Séries A/B) | 4 |
| SVG genérico (duas cores + sigla) | 41 |

Os 41 escudos genéricos são de clubes da Série D que não têm imagem pública
indexada; foram desenhados por `scripts/gerar_escudos.py` (escudo em duas cores
com a sigla), no estilo "escudo genérico" dos jogos de futebol.

Para trocar um escudo, basta salvar `assets/escudos/<SIGLA>.png` (PNG com fundo
transparente). Para criar um clube novo sem imagem:

```bash
python scripts/gerar_escudos.py            # só os que faltam
python scripts/gerar_escudos.py --forcar   # refaz só os genéricos
```

```python
from game.escudos import imagem, tem_escudo
imagem("FLA", "🔴⚫")     # <img class="escudo" src="data:image/png;base64,…">
tem_escudo("FLA")         # True
```

Clube sem imagem (por exemplo, criado pelo jogador) cai no emoji de sempre.
Os escudos são marcas dos clubes; aqui são usados apenas para identificá-los
no jogo.

## Correções aplicadas

| Arquivo | Problema | Correção |
|---|---|---|
| `mercado.py` | `from game.banco_dados import ...` quebrava (módulo se chamava `dados`) | banco renomeado para `banco_dados.py`; `dados.py` virou alias |
| `jogo_engine.py` | goleador contava **2 jogos** por partida | contagem única em `_atualizar_stats` |
| `campeonato.py` | `League([])` gerava calendário vazio e travava depois | validação: mínimo de 2 times |
| `campeonato.py` | `artilharia()` tipada como `list[Jogador]`, mas devolve tuplas | tipo corrigido para `list[tuple[Jogador, str]]` |
| `mercado.py` | elenco não era reescalado após compra/venda | `auto_escalar()` após a transferência |
| `mercado.py` | vender sem outro clube quebrava (`random.choice([])`) e a venda não reescalava o vendedor | validação do comprador + `auto_escalar()` nos dois lados |
| `modelos.py` | `divisao`, `estadio`, `capacidade`, `fundacao`, `rival` e `origem` eram anexados "por fora" da dataclass `Time` (e descartados em silêncio) | viraram campos reais da dataclass |
| `competicoes.py` | pontos corridos gravavam `grupo=""`, então a aba de classificação filtrava `"Geral"` e mostrava a tabela zerada | grupo `"Geral"` desde a montagem (+ compatibilidade com campeonatos antigos) |
| `app.py` | clube criado pelo jogador podia ser escolhido na tela inicial, mas ficava fora da `League`/`Market` (`get_meu_time()` devolvia `None`) | a lista de times da liga agora inclui os clubes criados |
| `app.py` | mata-mata checava `b is None` antes de `a is None` e estourava em confronto com BYE | ordem das checagens corrigida |
| `app.py` | "Contratar" em Meus dados passava um jogador `None` para o elenco | checagem de `None` antes de contratar |
| `criador.py` | `criar_clube()` anexava metadados dentro de `try/except: pass` | atribuição direta nos campos de `Time` |
| `piramide.py` | temporada só em pontos corridos (38 ou 190 rodadas), sem acesso por fase | regulamento por série em `divisao.py` (turno único, grupos e mata-mata) |
| `app.py` (CSS) | regra global `span { font-family: … !important }` vencia a fonte dos ícones nativos do Streamlit: o nome da ligadura aparecia como texto (`keyboard_double_arrow_left` no botão de recolher a sidebar) | regra específica para `[data-testid="stIconMaterial"]` devolvendo `Material Symbols Rounded` (+ fonte de emoji para `stIconEmoji`) |

### Tipos / Pylance

O projeto passa **sem erros e sem warnings** no Pylance (mesma engine do
Pyright) quando o interpretador tem as dependências do `requirements.txt`:

```bash
pip install -r requirements.txt
pyright .        # 0 errors, 0 warnings
ruff check .     # sem problemas (F, E9, B, UP)
```

Principais ajustes de tipagem: `tabela()` de `Campeonato` agora devolve
`list[LinhaTabela]` (TypedDict) em vez de `list[dict]`; `_evento_gol()` e
`_vencedor_confronto()` declaram `str | None` / `Time | None` (era o que o
corpo já devolvia); `Time | None` e `Fase | None` são estreitados antes do uso;
`_gerar_elenco`, `_gerar_jogadores_posicao`, `criar_times` e
`criar_todas_divisoes` têm tipos de retorno; `game.liga`/`game.dados` deixaram
de trocar `sys.modules` e viraram reexports de verdade (o Pylance não
conseguia enxergar `League`).

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
| Times com caixa negativo (banco de 61 clubes da época) | 29 | **4** | — |
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

- Com número ímpar de clubes o round-robin usa **BYE** (rodada de folga) e
  `proximo_adversario()` devolve `"Folga"` nesses casos.
- O calendário segue o regulamento de cada série: A/B têm 27 rodadas, C tem 19
  e a D (96 clubes) tem 15. As quatro divisões correm juntas; quando a sua
  termina, o botão "Simular o restante das outras divisões" fecha a temporada.
- O acesso e o descenso são definidos pelo regulamento de cada série e aplicados
  ao fechar a temporada (`Piramide.aplicar_acesso_descenso`).
- Numa temporada longa, 3 ou 4 clubes pequenos podem terminar com caixa
  negativo; é o comportamento esperado da régua econômica atual.
- `is_player_home` / `is_player_away` continuam sem uso dentro de `simular()` —
  ficaram disponíveis para a interface (narração, escalação do jogador).

## Temporada com as quatro divisões

A carreira joga **todas as divisões ao mesmo tempo**: no início do jogo é criada
uma `Piramide` (`game/piramide.py`) com uma `League` por divisão. Cada rodada
simulada avança A, B, C e D; a sua divisão decide o calendário da tela
"Jogar Rodada", mas o resto do país joga junto.

```python
from game.piramide import Piramide

piramide = Piramide(times)          # times com .divisao = "A".."D"
piramide.ordem                      # ['A', 'B', 'C', 'D']
piramide.rodada("B")                # rodada atual da Série B
piramide.simular_rodada("Flamengo") # uma rodada em cada divisão
piramide.classificacao("D")         # tabela completa da Série D
piramide.confrontos_da_rodada("C", 12)   # jogos da rodada 12 (com placar)
piramide.data_da_rodada(1)          # data fictícia da rodada
piramide.acesso_descenso()          # prévia do sobe-e-desce
piramide.nova_temporada()           # aplica e recomeça
```

Regras do sobe-e-desce (`ACESSO_PADRAO`): caem **4** de cada divisão, sobem os
**4** primeiros da de baixo. A Série D não tem divisão abaixo, então só recebe
quem cai da C. Os times que mudam de divisão levam elenco e finanças junto; as
estatísticas zeram no início da temporada seguinte.

**Telas**

- **🏆 Classificações** — uma aba por divisão, com a tabela completa, as zonas
  (Libertadores/Sul-Americana/acesso/rebaixamento), a legenda e a artilharia por
  divisão.
- **📅 Calendário** — rodada a rodada de qualquer divisão, com data, placar dos
  jogos já disputados e destaque do seu time; a aba "Meus jogos" lista a sua
  temporada inteira com V/E/D.
- **📊 Resultados** — placares por rodada, com abas para as quatro divisões.

## Criador de campeonatos

O criador monta torneios com todas as combinações que o motor suporta:

| Opção | Onde vale | Efeito |
|---|---|---|
| Formato | todos | pontos corridos, copa ou grupos + eliminatórias |
| Ida e volta na fase de grupos | pontos corridos, grupos | turno único ou turno e returno |
| Ida e volta nas fases | copa, grupos | jogo único ou ida e volta no mata-mata |
| Final em jogo único | copa, grupos | a final sempre em jogo único |
| Disputa de 3º lugar | copa, grupos | jogo extra entre os perdedores das semifinais |
| Distribuição dos times | todos | sorteio ou cabeças de chave (potes por força) |
| Número de grupos | grupos | de 2 a 12 grupos |
| Times por grupo | grupos | fixa o tamanho e deriva a quantidade de grupos |
| Classificados por grupo | grupos | quantos avançam de cada grupo |
| Promovidos / rebaixados | pontos corridos | quantos sobem e caem no fim |
| Temporada | todos | ano exibido no torneio |
| Sorteio reproduzível + semente | todos | mesmo sorteio para a mesma semente |

A tela mostra uma **prévia** do formato antes de criar ("4 grupos (5 times) ·
classificam 2 por grupo (8 no mata-mata) · 40 jogos na fase de grupos + 7 no
mata-mata..."), e os limites se ajustam ao número de times escolhido.

```python
from game.competicoes import Campeonato

camp = Campeonato(
    "Copa Aurora", times, formato="grupos_mata",
    times_por_grupo=5, classificados_por_grupo=2,
    ida_e_volta=True, ida_e_volta_mata=False,
    distribuicao="forca", terceiro_lugar=True,
    final_unica=True, semente=42,
)
camp.simular_tudo()
camp.jogo_terceiro_lugar        # Partida da disputa de 3º lugar
```

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
- Tabelas HTML (classificações das 4 divisões, elenco, artilharia) com zebra,
  zona colorida (Libertadores / Sul-Americana / acesso / rebaixamento) e
  destaque do seu time.
- Calendário com uma linha por jogo, data da rodada e placar (ou "a jogar").
- Campo tático com grama listrada, linha de meio e círculo central, e chips de
  jogador com overall e energia.
- Placar em gradiente por resultado e narração em linha do tempo (gol, amarelo,
  vermelho, defesa).
- Barras de energia em gradiente e selos de status (disponível / lesionado /
  suspenso).
