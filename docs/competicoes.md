# Competições

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

A copa faz parte da temporada (`game/copa.py`): 128 clubes das quatro divisões,
mata-mata em ida e volta da primeira fase até a final, sem jogo único.
As datas vêm **depois** das rodadas dos regionais (8, 10, 12, … 34), então o
clube joga a copa no meio da semana e o Brasileirão no fim de semana — as duas
competições aparecem juntas em 📅 Calendário, 🏆 Classificações e 📊 Resultados.
Empate no agregado vai para os pênaltis.

O atalho 🛠️ Criador → 🏆 **Copa do Brasil** continua existindo para montar uma
copa avulsa, fora da carreira.

**Torneios regionais (12 clubes cada, 7 rodadas)**

No começo da temporada abrem três torneios regionais (`game/regional.py`), com os
12 clubes mais tradicionais de cada região:

| Torneio | Estados |
|---|---|
| Rio-SP | RJ, SP |
| Sul-Minas | RS, SC, PR, MG |
| Copa do Nordeste | BA, PE, CE, RN, PB, AL, SE, PI, MA |

1. Três grupos de 4 em turno único (3 rodadas).
2. Classificam os 2 primeiros de cada grupo + os 2 melhores terceiros (8 clubes),
   em mata-mata de jogo único: quartas (1×8, 2×7, 3×6, 4×5) e semifinal, sempre
   na casa do melhor colocado; empate vai para os pênaltis.
3. Final em ida e volta (agregado + pênaltis), com o pior campanha em casa no
   primeiro jogo.

**Supercopa do Brasil (jogo único)**

Fecha a temporada (`Piramide`): campeão brasileiro (Série A) × campeão da Copa do
Brasil, em jogo único na casa do campeão brasileiro. Se o mesmo clube ganhar as
duas competições, o adversário é o vice da Copa. Empate vai para os pênaltis.
É a última rodada do calendário (`total_rodadas_global`).


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
