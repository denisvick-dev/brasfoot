# Arquitetura

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
- Abas **🌎 Regionais** em Classificações e Resultados (tabelas dos grupos, chave
  do mata-mata e jogos rodada a rodada) e cards dos campeões regionais, da
  Supercopa e do acesso/descenso no fim da temporada.
- Acabamento: rolagem horizontal nas tabelas largas, abas roláveis e paddings
  menores em telas estreitas, microinterações em linhas de resultado e cartões
  de clube (escudo ao lado do nome), foco visível no teclado e respeito a
  `prefers-reduced-motion`.
