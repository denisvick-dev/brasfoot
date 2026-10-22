"""
Base de dados com times e jogadores brasileiros.

As fichas dos clubes ficam em ``game.clubes``: 156 clubes na piramide
completa (Serie A 20, Serie B 20, Serie C 20 e Serie D 96), cada um com
cidade, estado, escudo, cores, forca do elenco, financas, torcida,
reputacao, estadio, capacidade, ano de fundacao e rival. Este modulo
transforma ficha em ``Time`` (gerando o elenco) e conhece a API de
consulta usada pelo jogo.

Uso rapido
----------
>>> from game.dados import criar_times
>>> times = criar_times()             # 20 clubes (Serie A) - padrao, como antes
>>> times = criar_times(24)           # 24 clubes: os 20 da A + os 4 melhores da B
>>> times = criar_times(divisao="B")  # so a Serie B (20 clubes)
>>> tudo  = criar_times(None)         # todos os 156 clubes
>>> misto = criar_times(32, aleatorio=True, semente=42)
"""

import random
from game.clubes import (
    DIVISOES,
    NOMES_DIVISAO,
    TIMES_DATA,
    TOTAL_TIMES,
    Clube,
    clubes_por_divisao,
)
from game.modelos import Jogador, Time

# Contador global de IDs
_jogador_id = 0


def _next_id() -> int:
    global _jogador_id
    _jogador_id += 1
    return _jogador_id


def _criar_jogador(
    nome: str,
    posicao: str,
    idade: int,
    hab: int,
    vel: int,
    fin: int,
    pas: int,
    defe: int,
    fis: int,
) -> Jogador:
    return Jogador(_next_id(), nome, posicao, idade, hab, vel, fin, pas, defe, fis)


# ============================================================
# Nomes brasileiros para geração procedural
# ============================================================
PRIMEIROS_NOMES = [
    "Lucas",
    "Gabriel",
    "Rafael",
    "Pedro",
    "Matheus",
    "Bruno",
    "Felipe",
    "Thiago",
    "André",
    "Diego",
    "Marcos",
    "Vinicius",
    "Guilherme",
    "Leonardo",
    "Rodrigo",
    "Gustavo",
    "Carlos",
    "Eduardo",
    "Henrique",
    "João",
    "Daniel",
    "Willian",
    "Leandro",
    "Caio",
    "Victor",
    "Alex",
    "Renan",
    "Fabio",
    "Igor",
    "Adriano",
    "Wesley",
    "Neymar",
    "Romário",
    "Ronaldo",
    "Rivaldo",
    "Kaká",
    "Denílson",
    "Hulk",
    "Oscar",
    "Luiz",
    "Éverton",
    "Richarlison",
    "Firmino",
    "Coutinho",
    "Casemiro",
    "Marcelo",
    "Danilo",
    "Ederson",
    "Alisson",
    "Weverton",
]

SOBRENOMES = [
    "Silva",
    "Santos",
    "Oliveira",
    "Souza",
    "Pereira",
    "Costa",
    "Rodrigues",
    "Almeida",
    "Nascimento",
    "Lima",
    "Araújo",
    "Ferreira",
    "Ribeiro",
    "Carvalho",
    "Gomes",
    "Martins",
    "Rocha",
    "Barbosa",
    "Moreira",
    "Dias",
    "Nunes",
    "Cardoso",
    "Mendes",
    "Batista",
    "Campos",
    "Correia",
    "Teixeira",
    "Vieira",
    "Monteiro",
    "Moura",
]


def _nome_aleatorio() -> str:
    return f"{random.choice(PRIMEIROS_NOMES)} {random.choice(SOBRENOMES)}"


def _gerar_jogadores_posicao(
    posicao: str, qtd: int, min_hab: int, max_hab: int
) -> list[Jogador]:
    jogadores = []
    for _ in range(qtd):
        idade = random.randint(18, 36)
        base = random.randint(min_hab, max_hab)
        variacao = 12

        if posicao == "GOL":
            j = _criar_jogador(
                _nome_aleatorio(),
                posicao,
                idade,
                hab=base + random.randint(-5, 5),
                vel=base + random.randint(-variacao, variacao) - 10,
                fin=random.randint(20, 40),
                pas=base + random.randint(-variacao, variacao) - 15,
                defe=base + random.randint(-5, 10),
                fis=base + random.randint(-variacao, variacao),
            )
        elif posicao == "ZAG":
            j = _criar_jogador(
                _nome_aleatorio(),
                posicao,
                idade,
                hab=base + random.randint(-variacao, variacao) - 5,
                vel=base + random.randint(-variacao, variacao) - 10,
                fin=random.randint(25, 50),
                pas=base + random.randint(-variacao, variacao) - 10,
                defe=base + random.randint(-5, 10),
                fis=base + random.randint(-5, 10),
            )
        elif posicao == "LAT":
            j = _criar_jogador(
                _nome_aleatorio(),
                posicao,
                idade,
                hab=base + random.randint(-variacao, variacao),
                vel=base + random.randint(-5, 10),
                fin=base + random.randint(-variacao, variacao) - 10,
                pas=base + random.randint(-5, 10),
                defe=base + random.randint(-variacao, variacao),
                fis=base + random.randint(-5, 10),
            )
        elif posicao == "VOL":
            j = _criar_jogador(
                _nome_aleatorio(),
                posicao,
                idade,
                hab=base + random.randint(-variacao, variacao),
                vel=base + random.randint(-variacao, variacao) - 5,
                fin=base + random.randint(-variacao, variacao) - 15,
                pas=base + random.randint(-5, 10),
                defe=base + random.randint(-5, 10),
                fis=base + random.randint(-5, 10),
            )
        elif posicao == "MEI":
            j = _criar_jogador(
                _nome_aleatorio(),
                posicao,
                idade,
                hab=base + random.randint(-5, 10),
                vel=base + random.randint(-variacao, variacao),
                fin=base + random.randint(-variacao, variacao),
                pas=base + random.randint(-5, 10),
                defe=base + random.randint(-variacao, variacao) - 15,
                fis=base + random.randint(-variacao, variacao),
            )
        else:  # ATA
            j = _criar_jogador(
                _nome_aleatorio(),
                posicao,
                idade,
                hab=base + random.randint(-5, 10),
                vel=base + random.randint(-5, 10),
                fin=base + random.randint(-5, 10),
                pas=base + random.randint(-variacao, variacao) - 5,
                defe=random.randint(15, 35),
                fis=base + random.randint(-variacao, variacao),
            )

        # Clampar valores entre 1 e 99
        for attr in [
            "habilidade",
            "velocidade",
            "finalizacao",
            "passe",
            "defesa",
            "fisico",
        ]:
            setattr(j, attr, max(1, min(99, getattr(j, attr))))

        j.salario = j._calcular_salario()
        j.valor_mercado = j._calcular_valor()
        jogadores.append(j)

    return jogadores


def _gerar_elenco(forca_min: int, forca_max: int) -> list[Jogador]:
    """Gera um elenco completo."""
    elenco = []
    elenco += _gerar_jogadores_posicao("GOL", 3, forca_min, forca_max)
    elenco += _gerar_jogadores_posicao("ZAG", 4, forca_min, forca_max)
    elenco += _gerar_jogadores_posicao("LAT", 4, forca_min, forca_max)
    elenco += _gerar_jogadores_posicao("VOL", 3, forca_min, forca_max)
    elenco += _gerar_jogadores_posicao("MEI", 4, forca_min, forca_max)
    elenco += _gerar_jogadores_posicao("ATA", 4, forca_min, forca_max)
    return elenco



# ============================================================
# Consultas ao banco (as fichas vivem em game.clubes)
# ============================================================
def buscar_clube(sigla: str) -> Clube | None:
    """Busca a ficha de um clube pela sigla (ex: 'FLA')."""
    alvo = str(sigla).upper()
    for c in TIMES_DATA:
        if c.sigla == alvo:
            return c
    return None


def resumo_banco() -> str:
    """Texto-resumo do banco de clubes (útil para debug/telas)."""
    linhas = [f"Banco de dados: {TOTAL_TIMES} clubes"]
    for div in DIVISOES:
        clubes = clubes_por_divisao(div)
        linhas.append(f"  {NOMES_DIVISAO[div]}: {len(clubes)} clubes")
    return "\n".join(linhas)


# ============================================================
# Criação dos times
# ============================================================
def criar_times(
    quantidade: int | None = 20,
    divisao: str | None = None,
    aleatorio: bool = False,
    semente: int | None = None,
) -> list[Time]:
    """
    Cria os times do jogo.

    Parâmetros
    ----------
    quantidade:
        Quantos times criar. ``20`` (padrão) mantém o comportamento antigo
        (os 20 clubes da Série A, na mesma ordem). ``None`` devolve o banco
        inteiro (60 clubes).
    divisao:
        Filtra por divisão: ``"A"``, ``"B"`` ou ``"C"``.
    aleatorio:
        Sorteia os clubes em vez de pegar os primeiros da lista.
    semente:
        Semente do sorteio (deixa o resultado reproduzível).

    Exemplos
    --------
    >>> criar_times()                      # 20 clubes da Série A
    >>> criar_times(24)                    # 24 clubes (A + os 4 melhores da B)
    >>> criar_times(divisao="B")           # só a Série B
    >>> criar_times(None)                  # todos os 156 clubes
    >>> criar_times(32, aleatorio=True, semente=7)
    """
    global _jogador_id
    _jogador_id = 0

    # 1) seleciona a fatia do banco
    if divisao is not None:
        selecao = clubes_por_divisao(divisao)
    else:
        selecao = list(TIMES_DATA)

    if quantidade is not None:
        if not isinstance(quantidade, int) or isinstance(quantidade, bool):
            raise TypeError("quantidade deve ser um int (ou None)")
        if quantidade <= 0:
            raise ValueError("quantidade deve ser maior que zero")
        if quantidade > len(selecao):
            raise ValueError(
                f"O banco só tem {len(selecao)} clubes"
                + (f" na divisão {divisao}" if divisao else "")
                + f", mas foram pedidos {quantidade}."
            )
        if aleatorio:
            selecao = random.Random(semente).sample(selecao, quantidade)
        else:
            selecao = selecao[:quantidade]
    elif aleatorio:
        random.Random(semente).shuffle(selecao)

    # 2) monta os times
    return [_criar_time_de_ficha(clube, i) for i, clube in enumerate(selecao)]


def _criar_time_de_ficha(clube: Clube, id_time: int = 0) -> Time:
    """Monta um Time (com elenco e metadados) a partir de uma ficha."""
    elenco = _gerar_elenco(clube.f_min, clube.f_max)
    time = Time(
        id=id_time,
        nome=clube.nome,
        sigla=clube.sigla,
        cidade=clube.cidade,
        estado=clube.estado,
        escudo_emoji=clube.emoji,
        cor_primaria=clube.cor1,
        cor_secundaria=clube.cor2,
        jogadores=elenco,
        financas=clube.financas,
        torcida=clube.torcida,
        reputacao=clube.reputacao,
    )
    # Metadados da ficha do clube (campos da dataclass Time)
    time.divisao = clube.divisao
    time.estadio = clube.estadio
    time.capacidade = clube.capacidade
    time.fundacao = clube.fundacao
    time.rival = clube.rival
    time.origem = "banco"

    time.auto_escalar()
    return time


def criar_times_por_nome(nomes: list[str]) -> list[Time]:
    """
    Cria apenas os clubes pedidos (pelo nome), sem instanciar o banco inteiro.

    Ignora nomes desconhecidos — use ``nomes_conhecidos()`` para validar antes.
    """
    fichas = {c.nome: c for c in TIMES_DATA}
    times = []
    for i, nome in enumerate(nomes):
        ficha = fichas.get(nome)
        if ficha:
            times.append(_criar_time_de_ficha(ficha, i))
    return times


def nomes_conhecidos() -> list[str]:
    """Nomes de todos os clubes do banco, na ordem (Série A, B, C)."""
    return [c.nome for c in TIMES_DATA]


def criar_todas_divisoes() -> dict[str, list[Time]]:
    """
    Cria os times separados por divisão.

    Retorna ``{"A": [...], "B": [...], "C": [...]}`` — os IDs de jogador
    são reiniciados a cada divisão, então os IDs se repetem entre elas.
    """
    return {div: criar_times(None, divisao=div) for div in DIVISOES}
