# Criador de campeonatos

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
    "Copa Aurora",
    times,
    formato="grupos_mata",
    times_por_grupo=5,
    classificados_por_grupo=2,
    ida_e_volta=True,
    ida_e_volta_mata=False,
    distribuicao="forca",
    terceiro_lugar=True,
    final_unica=True,
    semente=42,
)
camp.simular_tudo()
camp.jogo_terceiro_lugar  # Partida da disputa de 3º lugar
```
