# Motor de simulação

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
  e a D (96 clubes) tem 15. As quatro divisões, os três regionais, a Copa do
  Brasil e a Supercopa correm juntas (35 rodadas no total);
  quando a sua divisão termina e você já saiu da copa, o botão "Simular o
  restante da temporada" fecha o ano. Se a sua divisão acaba mas você continua
  vivo na copa, o ⚽ Jogar Rodada passa a mostrar só os jogos da copa.
- O acesso e o descenso são definidos pelo regulamento de cada série e aplicados
  ao fechar a temporada (`Piramide.aplicar_acesso_descenso`).
- Numa temporada longa, 3 ou 4 clubes pequenos podem terminar com caixa
  negativo; é o comportamento esperado da régua econômica atual.
- `is_player_home` / `is_player_away` continuam sem uso dentro de `simular()` —
  ficaram disponíveis para a interface (narração, escalação do jogador).
