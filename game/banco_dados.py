"""
Base de dados com times e jogadores brasileiros.

O banco agora tem 61 clubes divididos em tres divisoes
(Serie A, Serie B e Serie C/regional), cada um com ficha completa:
cidade, estado, escudo, cores, forca do elenco, financas, torcida,
reputacao, estadio, capacidade, ano de fundacao e rival.

Uso rapido
----------
>>> from game.dados import criar_times
>>> times = criar_times()             # 20 clubes (Serie A) - padrao, como antes
>>> times = criar_times(24)           # 24 clubes: os 20 da A + os 4 melhores da B
>>> times = criar_times(divisao="B")  # so a Serie B (20 clubes)
>>> tudo  = criar_times(None)         # todos os 60 clubes
>>> misto = criar_times(32, aleatorio=True, semente=42)
"""

import random
from typing import NamedTuple

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
# Banco de clubes (61 times em 3 divisões)
# ============================================================
class Clube(NamedTuple):
    """Ficha de um clube no banco de dados."""

    nome: str
    sigla: str
    cidade: str
    estado: str
    emoji: str
    cor1: str
    cor2: str
    f_min: int
    f_max: int
    financas: int
    torcida: int
    reputacao: int
    # --- campos novos (não alteram a criação do Time) ---
    divisao: str
    estadio: str
    capacidade: int
    fundacao: int
    rival: str | None = None


TIMES_DATA: list[Clube] = [
    # ============================================================
    # SÉRIE A (20 clubes) — ordem e valores idênticos à versão anterior
    # ============================================================
    Clube("Flamengo", "FLA", "Rio de Janeiro", "RJ", "🔴⚫", "#C62828", "#212121",
          70, 90, 50_000_000, 95, 95, "A", "Maracanã", 78_838, 1895, "FLU"),
    Clube("Palmeiras", "PAL", "São Paulo", "SP", "🟢⚪", "#2E7D32", "#FFFFFF",
          70, 90, 45_000_000, 85, 93, "A", "Allianz Parque", 43_713, 1914, "COR"),
    Clube("Corinthians", "COR", "São Paulo", "SP", "⚫⚪", "#212121", "#FFFFFF",
          60, 82, 30_000_000, 90, 85, "A", "Neo Química Arena", 49_205, 1910, "PAL"),
    Clube("São Paulo", "SAO", "São Paulo", "SP", "🔴⚪⚫", "#C62828", "#FFFFFF",
          62, 83, 32_000_000, 82, 85, "A", "Morumbi", 66_795, 1930, "COR"),
    Clube("Fluminense", "FLU", "Rio de Janeiro", "RJ", "🟢🔴⚪", "#1B5E20", "#C62828",
          62, 83, 25_000_000, 55, 82, "A", "Maracanã", 78_838, 1902, "FLA"),
    Clube("Atlético-MG", "CAM", "Belo Horizonte", "MG", "⚫⚪", "#212121", "#FFFFFF",
          65, 85, 35_000_000, 75, 87, "A", "Arena MRV", 44_892, 1908, "CRU"),
    Clube("Internacional", "INT", "Porto Alegre", "RS", "🔴⚪", "#C62828", "#FFFFFF",
          60, 82, 28_000_000, 78, 83, "A", "Beira-Rio", 49_055, 1909, "GRE"),
    Clube("Grêmio", "GRE", "Porto Alegre", "RS", "🔵⚫⚪", "#1565C0", "#212121",
          60, 82, 28_000_000, 78, 83, "A", "Arena do Grêmio", 55_662, 1903, "INT"),
    Clube("Santos", "SAN", "Santos", "SP", "⚪⚫", "#FFFFFF", "#212121",
          55, 78, 18_000_000, 65, 78, "A", "Vila Belmiro", 16_798, 1912, "COR"),
    Clube("Botafogo", "BOT", "Rio de Janeiro", "RJ", "⚫⚪", "#212121", "#FFFFFF",
          65, 85, 35_000_000, 50, 82, "A", "Nilton Santos", 46_831, 1904, "VAS"),
    Clube("Vasco", "VAS", "Rio de Janeiro", "RJ", "⚫⚪", "#212121", "#FFFFFF",
          55, 78, 15_000_000, 70, 75, "A", "São Januário", 24_584, 1898, "FLA"),
    Clube("Cruzeiro", "CRU", "Belo Horizonte", "MG", "🔵⚪", "#1565C0", "#FFFFFF",
          60, 80, 25_000_000, 72, 80, "A", "Mineirão", 61_846, 1921, "CAM"),
    Clube("Athletico-PR", "CAP", "Curitiba", "PR", "🔴⚫", "#C62828", "#212121",
          58, 80, 22_000_000, 35, 78, "A", "Arena da Baixada", 42_372, 1924, "CFC"),
    Clube("Fortaleza", "FOR", "Fortaleza", "CE", "🔵🔴⚪", "#1565C0", "#C62828",
          58, 80, 18_000_000, 40, 76, "A", "Arena Castelão", 63_903, 1918, "CEA"),
    Clube("Bahia", "BAH", "Salvador", "BA", "🔵🔴⚪", "#1565C0", "#C62828",
          55, 78, 15_000_000, 50, 72, "A", "Arena Fonte Nova", 47_907, 1931, "VIT"),
    Clube("Cuiabá", "CUI", "Cuiabá", "MT", "🟢🟡", "#2E7D32", "#F9A825",
          45, 70, 8_000_000, 15, 55, "A", "Arena Pantanal", 44_097, 2001, None),
    Clube("Goiás", "GOI", "Goiânia", "GO", "🟢⚪", "#2E7D32", "#FFFFFF",
          45, 70, 8_000_000, 25, 55, "A", "Serra Dourada", 42_000, 1943, "VIL"),
    Clube("Coritiba", "CFC", "Curitiba", "PR", "🟢⚪", "#2E7D32", "#FFFFFF",
          45, 70, 8_000_000, 25, 55, "A", "Couto Pereira", 40_502, 1909, "CAP"),
    Clube("Juventude", "JUV", "Caxias do Sul", "RS", "🟢⚪", "#2E7D32", "#FFFFFF",
          42, 68, 6_000_000, 12, 50, "A", "Alfredo Jaconi", 19_924, 1913, "CAX"),
    Clube("América-MG", "AME", "Belo Horizonte", "MG", "🟢⚪", "#2E7D32", "#FFFFFF",
          42, 68, 6_000_000, 18, 50, "A", "Independência", 23_018, 1912, "CAM"),

    # ============================================================
    # SÉRIE B (20 clubes)
    # ============================================================
    Clube("Ceará", "CEA", "Fortaleza", "CE", "⚫⚪", "#212121", "#FFFFFF",
          55, 76, 14_000_000, 55, 72, "B", "Arena Castelão", 63_903, 1914, "FOR"),
    Clube("Sport", "SPO", "Recife", "PE", "🔴⚫", "#C62828", "#212121",
          54, 76, 14_000_000, 60, 72, "B", "Ilha do Retiro", 32_629, 1905, "NAU"),
    Clube("Vitória", "VIT", "Salvador", "BA", "🔴⚫", "#C62828", "#212121",
          54, 76, 13_000_000, 58, 72, "B", "Barradão", 34_535, 1899, "BAH"),
    Clube("Atlético-GO", "ACG", "Goiânia", "GO", "🔴⚫", "#C62828", "#212121",
          53, 75, 12_000_000, 30, 68, "B", "Antônio Accioly", 12_500, 1937, "GOI"),
    Clube("Chapecoense", "CHA", "Chapecó", "SC", "🟢⚪", "#2E7D32", "#FFFFFF",
          50, 72, 10_000_000, 30, 66, "B", "Arena Condá", 22_000, 1973, "AVA"),
    Clube("Ponte Preta", "PTE", "Campinas", "SP", "⚫⚪", "#212121", "#FFFFFF",
          50, 72, 9_000_000, 30, 66, "B", "Moisés Lucarelli", 19_722, 1900, "GUA"),
    Clube("CRB", "CRB", "Maceió", "AL", "🔴⚪", "#C62828", "#FFFFFF",
          50, 71, 9_000_000, 28, 64, "B", "Rei Pelé", 20_801, 1912, "CSA"),
    Clube("Guarani", "GUA", "Campinas", "SP", "🟢⚪", "#2E7D32", "#FFFFFF",
          50, 71, 9_000_000, 28, 66, "B", "Brinco de Ouro", 29_130, 1911, "PTE"),
    Clube("Vila Nova", "VIL", "Goiânia", "GO", "🔴⚪", "#C62828", "#FFFFFF",
          48, 70, 8_000_000, 25, 62, "B", "Serra Dourada", 42_000, 1943, "GOI"),
    Clube("Avaí", "AVA", "Florianópolis", "SC", "🔵⚪", "#1565C0", "#FFFFFF",
          48, 70, 8_000_000, 25, 62, "B", "Ressacada", 17_800, 1923, "FIG"),
    Clube("Mirassol", "MIR", "Mirassol", "SP", "🟡🟢", "#F9A825", "#2E7D32",
          47, 69, 7_000_000, 12, 58, "B", "José Maria de Campos Maia", 15_145, 1925, "NOV"),
    Clube("Criciúma", "CRI", "Criciúma", "SC", "🟡⚫", "#F9A825", "#212121",
          47, 69, 7_000_000, 22, 62, "B", "Heriberto Hülse", 19_300, 1947, "AVA"),
    Clube("Novorizontino", "NOV", "Novo Horizonte", "SP", "🟡⚫", "#F9A825", "#212121",
          46, 68, 6_000_000, 10, 56, "B", "Jorge Ismael de Biasi", 16_000, 1973, "MIR"),
    Clube("Ituano", "ITU", "Itu", "SP", "🔴⚪", "#C62828", "#FFFFFF",
          45, 68, 6_000_000, 10, 56, "B", "Novelli Júnior", 18_400, 1947, "PTE"),
    Clube("Botafogo-SP", "BFC", "Ribeirão Preto", "SP", "🔴⚪", "#C62828", "#FFFFFF",
          45, 68, 6_000_000, 15, 58, "B", "Santa Cruz", 29_292, 1918, None),
    Clube("Sampaio Corrêa", "SAM", "São Luís", "MA", "🔴🟢", "#C62828", "#2E7D32",
          44, 67, 5_000_000, 18, 56, "B", "Castelão", 40_000, 1923, None),
    Clube("Tombense", "TOM", "Tombos", "MG", "🔴⚪", "#C62828", "#FFFFFF",
          42, 66, 4_000_000, 8, 52, "B", "Almeidão", 3_050, 1914, None),
    Clube("Londrina", "LON", "Londrina", "PR", "🔵⚪", "#1565C0", "#FFFFFF",
          42, 66, 4_000_000, 14, 56, "B", "Estádio do Café", 31_000, 1956, None),
    Clube("ABC", "ABC", "Natal", "RN", "⚪🔴", "#FFFFFF", "#C62828",
          42, 65, 4_000_000, 20, 56, "B", "Frasqueirão", 18_000, 1915, None),
    Clube("Brusque", "BRU", "Brusque", "SC", "🔵⚪", "#1565C0", "#FFFFFF",
          40, 64, 3_000_000, 8, 50, "B", "Augusto Bauer", 5_000, 1987, None),

    # ============================================================
    # SÉRIE C / REGIONAIS (20 clubes)
    # ============================================================
    Clube("Náutico", "NAU", "Recife", "PE", "🔴⚪", "#C62828", "#FFFFFF",
          45, 66, 4_000_000, 35, 60, "C", "Aflitos", 22_000, 1901, "SPO"),
    Clube("Santa Cruz", "STC", "Recife", "PE", "🔴⚫", "#C62828", "#212121",
          44, 65, 4_000_000, 40, 60, "C", "Arruda", 60_044, 1914, "SPO"),
    Clube("Paysandu", "PAY", "Belém", "PA", "🔵⚪", "#1565C0", "#FFFFFF",
          44, 65, 4_000_000, 40, 62, "C", "Mangueirão", 45_000, 1914, "REM"),
    Clube("Remo", "REM", "Belém", "PA", "🔵⚪", "#1565C0", "#FFFFFF",
          43, 64, 3_500_000, 38, 60, "C", "Baenão", 13_200, 1905, "PAY"),
    Clube("Figueirense", "FIG", "Florianópolis", "SC", "⚫⚪", "#212121", "#FFFFFF",
          43, 64, 3_500_000, 22, 60, "C", "Orlando Scarpelli", 19_584, 1921, "AVA"),
    Clube("CSA", "CSA", "Maceió", "AL", "🔵⚪", "#1565C0", "#FFFFFF",
          43, 64, 3_500_000, 25, 58, "C", "Rei Pelé", 20_801, 1913, "CRB"),
    Clube("Botafogo-PB", "BPB", "João Pessoa", "PB", "🔴⚫", "#C62828", "#212121",
          42, 63, 3_000_000, 20, 56, "C", "Almeidão", 25_000, 1931, "CMP"),
    Clube("Confiança", "CON", "Aracaju", "SE", "🔵⚪", "#1565C0", "#FFFFFF",
          40, 62, 2_500_000, 15, 54, "C", "Batistão", 15_575, 1936, "SER"),
    Clube("Amazonas", "AMZ", "Manaus", "AM", "🔵⚪", "#1565C0", "#FFFFFF",
          40, 62, 3_000_000, 10, 50, "C", "Arena da Amazônia", 44_000, 2019, "MAN"),
    Clube("Manaus", "MAN", "Manaus", "AM", "🟡🟢", "#F9A825", "#2E7D32",
          40, 62, 2_500_000, 10, 50, "C", "Colina", 10_000, 2013, "AMZ"),
    Clube("Volta Redonda", "VRD", "Volta Redonda", "RJ", "🟡⚫", "#F9A825", "#212121",
          40, 62, 2_500_000, 8, 52, "C", "Raulino de Oliveira", 18_250, 1976, None),
    Clube("Ypiranga-RS", "YPI", "Erechim", "RS", "🟡⚫", "#F9A825", "#212121",
          38, 60, 2_000_000, 8, 50, "C", "Colosso da Lagoa", 22_000, 1924, None),
    Clube("Brasil de Pelotas", "BDP", "Pelotas", "RS", "🟡⚫", "#F9A825", "#212121",
          38, 60, 2_000_000, 12, 54, "C", "Bento Freitas", 18_000, 1911, None),
    Clube("Paraná", "PAR", "Curitiba", "PR", "🔵🔴", "#1565C0", "#C62828",
          38, 60, 2_000_000, 18, 54, "C", "Vila Capanema", 20_000, 1989, "CFC"),
    Clube("Joinville", "JOI", "Joinville", "SC", "🟡⚫", "#F9A825", "#212121",
          38, 60, 2_000_000, 12, 54, "C", "Arena Joinville", 22_400, 1976, None),
    Clube("Ferroviário", "FER", "Fortaleza", "CE", "🔴⚪", "#C62828", "#FFFFFF",
          36, 58, 1_500_000, 10, 48, "C", "Elzir Cabral", 8_000, 1933, "CEA"),
    Clube("Campinense", "CMP", "Campina Grande", "PB", "🔴⚫", "#C62828", "#212121",
          36, 58, 1_500_000, 12, 50, "C", "Amigão", 25_000, 1915, "BPB"),
    Clube("Sergipe", "SER", "Aracaju", "SE", "🔴⚪", "#C62828", "#FFFFFF",
          35, 57, 1_200_000, 10, 48, "C", "Batistão", 15_575, 1909, "CON"),
    Clube("America-RJ", "AMR", "Rio de Janeiro", "RJ", "🔴⚪", "#C62828", "#FFFFFF",
          35, 57, 1_200_000, 15, 55, "C", "Edson Passos", 13_000, 1904, "VAS"),
    Clube("Caxias", "CAX", "Caxias do Sul", "RS", "🔵⚪", "#1565C0", "#FFFFFF",
          38, 60, 2_000_000, 10, 50, "C", "Centenário", 22_132, 1935, "JUV"),
    Clube("Rio Branco-AC", "RBA", "Rio Branco", "AC", "🔴⚪", "#C62828", "#FFFFFF",
          30, 52, 800_000, 6, 40, "C", "Arena da Floresta", 20_000, 1919, None),
]

# Alias legado (a versão antiga guardava essa lista dentro de criar_times)
times_data = TIMES_DATA

DIVISOES = ("A", "B", "C")
NOMES_DIVISAO = {"A": "Série A", "B": "Série B", "C": "Série C"}
TOTAL_TIMES = len(TIMES_DATA)


# ============================================================
# Consultas ao banco
# ============================================================
def clubes_por_divisao(divisao: str) -> list[Clube]:
    """Retorna as fichas (Clube) de uma divisão: 'A', 'B' ou 'C'."""
    div = str(divisao).upper()
    if div not in DIVISOES:
        raise ValueError(
            f"Divisão inválida: {divisao!r}. Use uma de {DIVISOES}."
        )
    return [c for c in TIMES_DATA if c.divisao == div]


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
    >>> criar_times(None)                  # todos os 60 clubes
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
