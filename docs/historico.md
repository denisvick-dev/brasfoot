# Histórico de correções

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
Pyright) quando o interpretador tem as dependências instaladas. O Pylance segue
o `pyrightconfig.json` do repositório, então o resultado no VS Code é o mesmo da
linha de comando. As ferramentas de conferência estão em `requirements-dev.txt`:

```bash
pip install -r requirements-dev.txt
pyright .        # 0 errors, 0 warnings  (config em pyrightconfig.json)
ruff check .     # sem problemas (F, E9, B, UP — config em ruff.toml)
```

O Playwright (usado só por `shots.py`) também vem do `requirements-dev.txt`;
depois rode `playwright install chromium`.

Principais ajustes de tipagem: `tabela()` de `Campeonato` agora devolve
`list[LinhaTabela]` (TypedDict) em vez de `list[dict]`; `_evento_gol()` e
`_vencedor_confronto()` declaram `str | None` / `Time | None` (era o que o
corpo já devolvia); `Time | None` e `Fase | None` são estreitados antes do uso;
`_gerar_elenco`, `_gerar_jogadores_posicao`, `criar_times` e
`criar_todas_divisoes` têm tipos de retorno; `game.liga`/`game.dados` deixaram
de trocar `sys.modules` e viraram reexports de verdade (o Pylance não
conseguia enxergar `League`).
