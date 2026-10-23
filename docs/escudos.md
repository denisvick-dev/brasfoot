# Escudos

## Escudos


Os escudos ficam em `assets/escudos/` com o nome da sigla do clube — `FLA.png`,
`AME.svg`… — e a interface mostra a imagem no lugar do emoji (cartões de clube,
tabelas, títulos e confrontos). Como o app injeta HTML no `st.markdown`, a
imagem é embutida como *data URI* (cache em `game/escudos.py`), sem servidor de
estáticos.

**O nome do arquivo é exatamente a sigla de `game/clubes.py`** (campo `sigla` da
dataclass `Clube`), em maiúsculas e com 3 ou 4 letras — `IAPE.png`, `CRAC.png`.
As siglas são únicas: nenhum clube divide arquivo com outro. Para conferir:

```python
from game.escudos import faltando, orfaos
faltando()   # [] → todo clube do banco tem escudo
orfaos()     # [] → todo arquivo corresponde a um clube
```

| Origem | Clubes |
|---|---|
| PNG oficial | 156 |
| SVG genérico (cores do clube + sigla) | 0 |

Todos os 156 clubes do banco têm escudo oficial em PNG — nenhum sobrou no
desenho genérico. O `scripts/gerar_escudos.py` continua no projeto para clubes
criados pelo jogador ou para times novos que ainda não tenham imagem: ele
desenha o SVG genérico (contorno de escudo, listras nas cores do clube, faixa
clara com a sigla e um leve gradiente de volume). Se um escudo real for
adicionado depois (`assets/escudos/<SIGLA>.png`), o PNG tem precedência e o SVG
genérico pode ser apagado.

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
