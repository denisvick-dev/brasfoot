"""
Fichas dos clubes do futebol brasileiro (pirâmide 2026).

Uma ficha (``Clube``) tem tudo que o jogo usa para montar um ``Time``:
cidade, estado, escudo, cores, faixa de força do elenco, finanças, torcida,
reputação e os dados de apresentação (divisão, estádio, capacidade, fundação
e rival).

O banco cobre as quatro divisões da temporada 2026:

* **Série A** — 20 clubes
* **Série B** — 20 clubes
* **Série C** — 20 clubes
* **Série D** — 96 clubes (os 96 classificados da edição 2026)

Os escudos de cada clube ficam em ``assets/escudos`` (veja ``game.escudos``).

Total: 156 clubes. As faixas de força e reputação descem degrau a degrau
(com pequenas sobreposições na fronteira: o clube recém-rebaixado costuma ser
mais forte que o recém-promovido).

Uso
---
>>> from game.clubes import TIMES_DATA, clubes_por_divisao
>>> len(TIMES_DATA)                            # 156
>>> len(clubes_por_divisao("D"))               # 96
>>> TIMES_DATA[0].nome                         # 'Flamengo'
"""

from typing import NamedTuple


class Clube(NamedTuple):
    """Ficha de um clube no banco de dados."""

    nome: str
    sigla: str
    cidade: str
    estado: str
    emoji: str
    cor1: str
    cor2: str
    f_min: int          # força mínima do elenco gerado
    f_max: int          # força máxima do elenco gerado
    financas: int       # caixa inicial (R$)
    torcida: int        # 1 a 100 (peso de torcida)
    reputacao: int      # 1 a 100
    # --- dados de apresentação ---
    divisao: str        # "A" | "B" | "C" | "D"
    estadio: str
    capacidade: int
    fundacao: int
    rival: str | None = None


TIMES_DATA: list[Clube] = [
    # ============================================================
    # SÉRIE A (20 clubes) — elite do Brasileirão
    # ============================================================
    Clube(
        "Flamengo", "FLA", "Rio de Janeiro", "RJ", "🔴⚫", "#C62828", "#212121",
        70, 90, 50_000_000, 95, 95,
        "A", "Maracanã", 78_838, 1895, "FLU",
    ),
    Clube(
        "Palmeiras", "PAL", "São Paulo", "SP", "🟢⚪", "#2E7D32", "#FFFFFF",
        70, 90, 45_000_000, 85, 93,
        "A", "Allianz Parque", 43_713, 1914, "COR",
    ),
    Clube(
        "Corinthians", "COR", "São Paulo", "SP", "⚫⚪", "#212121", "#FFFFFF",
        60, 82, 30_000_000, 90, 85,
        "A", "Neo Química Arena", 49_205, 1910, "SAO",
    ),
    Clube(
        "São Paulo", "SAO", "São Paulo", "SP", "🔴⚪⚫", "#C62828", "#FFFFFF",
        62, 83, 32_000_000, 82, 85,
        "A", "Morumbi", 66_795, 1930, "COR",
    ),
    Clube(
        "Fluminense", "FLU", "Rio de Janeiro", "RJ", "🟢🔴⚪", "#1B5E20", "#C62828",
        62, 83, 25_000_000, 55, 82,
        "A", "Maracanã", 78_838, 1902, "BOT",
    ),
    Clube(
        "Atlético-MG", "CAM", "Belo Horizonte", "MG", "⚫⚪", "#212121", "#FFFFFF",
        65, 85, 35_000_000, 75, 87,
        "A", "Arena MRV", 44_892, 1908, "CRU",
    ),
    Clube(
        "Internacional", "INT", "Porto Alegre", "RS", "🔴⚪", "#C62828", "#FFFFFF",
        60, 82, 28_000_000, 78, 83,
        "A", "Beira-Rio", 49_055, 1909, "GRE",
    ),
    Clube(
        "Grêmio", "GRE", "Porto Alegre", "RS", "🔵⚫⚪", "#1565C0", "#212121",
        60, 82, 28_000_000, 78, 83,
        "A", "Arena do Grêmio", 55_662, 1903, "INT",
    ),
    Clube(
        "Santos", "SAN", "Santos", "SP", "⚪⚫", "#FFFFFF", "#212121",
        55, 78, 18_000_000, 65, 78,
        "A", "Vila Belmiro", 16_798, 1912, "COR",
    ),
    Clube(
        "Botafogo", "BOT", "Rio de Janeiro", "RJ", "⚫⚪", "#212121", "#FFFFFF",
        65, 85, 35_000_000, 50, 82,
        "A", "Nilton Santos", 46_831, 1904, "FLU",
    ),
    Clube(
        "Vasco", "VAS", "Rio de Janeiro", "RJ", "⚫⚪", "#212121", "#FFFFFF",
        55, 78, 15_000_000, 70, 75,
        "A", "São Januário", 24_584, 1898, "FLU",
    ),
    Clube(
        "Cruzeiro", "CRU", "Belo Horizonte", "MG", "🔵⚪", "#1565C0", "#FFFFFF",
        60, 80, 25_000_000, 72, 80,
        "A", "Mineirão", 61_846, 1921, "CAM",
    ),
    Clube(
        "Athletico-PR", "CAP", "Curitiba", "PR", "🔴⚫", "#C62828", "#212121",
        58, 80, 22_000_000, 35, 78,
        "A", "Arena da Baixada", 42_372, 1924, "CFC",
    ),
    Clube(
        "Bahia", "BAH", "Salvador", "BA", "🔵🔴⚪", "#1565C0", "#C62828",
        55, 78, 15_000_000, 50, 72,
        "A", "Arena Fonte Nova", 47_907, 1931, "VIT",
    ),
    Clube(
        "Coritiba", "CFC", "Curitiba", "PR", "🟢⚪", "#2E7D32", "#FFFFFF",
        50, 74, 10_000_000, 28, 64,
        "A", "Couto Pereira", 40_502, 1909, "LON",
    ),
    Clube(
        "Bragantino", "RBB", "Bragança Paulista", "SP", "⚪🔴", "#FFFFFF", "#E53935",
        55, 76, 16_000_000, 18, 68,
        "A", "Cícero de Souza Marques", 17_724, 1928, "SAN",
    ),
    Clube(
        "Chapecoense", "CHA", "Chapecó", "SC", "🟢⚪", "#2E7D32", "#FFFFFF",
        50, 74, 9_000_000, 24, 63,
        "A", "Arena Condá", 20_089, 1973, "AVA",
    ),
    Clube(
        "Mirassol", "MIR", "Mirassol", "SP", "🟡🟢", "#F9A825", "#2E7D32",
        50, 74, 8_000_000, 14, 62,
        "A", "Maiorzão", 15_000, 1925, "NOV",
    ),
    Clube(
        "Remo", "REM", "Belém", "PA", "🔵⚪", "#1565C0", "#FFFFFF",
        50, 74, 9_000_000, 30, 64,
        "A", "Baenão", 14_000, 1905, "PAY",
    ),
    Clube(
        "Vitória", "VIT", "Salvador", "BA", "🔴⚫", "#C62828", "#212121",
        50, 74, 10_000_000, 30, 65,
        "A", "Barradão", 30_000, 1899, "BAH",
    ),

    # ============================================================
    # SÉRIE B (20 clubes)
    # ============================================================
    Clube(
        "América-MG", "AMG", "Belo Horizonte", "MG", "🟢⚪", "#2E7D32", "#FFFFFF",
        42, 68, 6_000_000, 18, 50,
        "B", "Independência", 23_018, 1912, "ATH",
    ),
    Clube(
        "Athletic Club", "ATH", "São João del-Rei", "MG", "⚫⚪", "#212121", "#FFFFFF",
        40, 65, 5_000_000, 8, 48,
        "B", "João Marques de Oliveira", 5_000, 1909, "TOM",
    ),
    Clube(
        "Atlético-GO", "ACG", "Goiânia", "GO", "🔴⚫", "#C62828", "#212121",
        42, 68, 7_000_000, 20, 55,
        "B", "Antônio Accioly", 12_500, 1937, "GOI",
    ),
    Clube(
        "Avaí", "AVA", "Florianópolis", "SC", "🔵🟡", "#1565C0", "#F9A825",
        42, 68, 6_000_000, 18, 52,
        "B", "Ressacada", 17_800, 1923, "CHA",
    ),
    Clube(
        "Botafogo-SP", "BSP", "Ribeirão Preto", "SP", "🔴⚫", "#C62828", "#212121",
        40, 66, 5_000_000, 14, 50,
        "B", "Santa Cruz", 29_292, 1918, "ITU",
    ),
    Clube(
        "Ceará", "CEA", "Fortaleza", "CE", "⚫⚪", "#212121", "#FFFFFF",
        52, 76, 12_000_000, 30, 70,
        "B", "Castelão", 63_903, 1914, "FOR",
    ),
    Clube(
        "CRB", "CRB", "Maceió", "AL", "🔴⚪", "#C62828", "#FFFFFF",
        45, 70, 8_000_000, 22, 56,
        "B", "Rei Pelé", 17_126, 1912, "CSA",
    ),
    Clube(
        "Criciúma", "CRI", "Criciúma", "SC", "🟡⚫", "#F9A825", "#212121",
        45, 70, 8_000_000, 20, 56,
        "B", "Heriberto Hülse", 19_225, 1947, "FIG",
    ),
    Clube(
        "Cuiabá", "CUI", "Cuiabá", "MT", "🟢🟡", "#2E7D32", "#F9A825",
        45, 70, 8_000_000, 15, 55,
        "B", "Arena Pantanal", 44_097, 2001, "LUV",
    ),
    Clube(
        "Fortaleza", "FOR", "Fortaleza", "CE", "🔵🔴⚪", "#1565C0", "#C62828",
        54, 78, 15_000_000, 34, 72,
        "B", "Castelão", 63_903, 1918, "CEA",
    ),
    Clube(
        "Goiás", "GOI", "Goiânia", "GO", "🟢⚪", "#2E7D32", "#FFFFFF",
        45, 70, 8_000_000, 25, 55,
        "B", "Serrinha", 14_525, 1943, "ACG",
    ),
    Clube(
        "Juventude", "JUV", "Caxias do Sul", "RS", "🟢⚪", "#2E7D32", "#FFFFFF",
        42, 68, 6_000_000, 12, 50,
        "B", "Alfredo Jaconi", 19_924, 1913, "CAX",
    ),
    Clube(
        "Londrina", "LON", "Londrina", "PR", "🔵⚪", "#1565C0", "#FFFFFF",
        40, 66, 5_000_000, 12, 48,
        "B", "Estádio do Café", 31_000, 1956, "OPE",
    ),
    Clube(
        "Novorizontino", "NOV", "Novo Horizonte", "SP", "🟡⚫", "#F9A825", "#212121",
        42, 68, 5_000_000, 8, 52,
        "B", "Jorge Ismael de Biasi", 16_000, 1973, "MIR",
    ),
    Clube(
        "Náutico", "NAU", "Recife", "PE", "🔴⚪", "#C62828", "#FFFFFF",
        42, 68, 6_000_000, 20, 55,
        "B", "Aflitos", 19_650, 1901, "STC",
    ),
    Clube(
        "Operário-PR", "OPE", "Ponta Grossa", "PR", "⚫⚪", "#212121", "#FFFFFF",
        40, 65, 4_000_000, 10, 48,
        "B", "Germano Krüger", 10_000, 1912, "LON",
    ),
    Clube(
        "Ponte Preta", "PON", "Campinas", "SP", "⚫⚪", "#212121", "#FFFFFF",
        42, 68, 6_000_000, 18, 55,
        "B", "Moisés Lucarelli", 17_728, 1900, "GUA",
    ),
    Clube(
        "Sport", "SPT", "Recife", "PE", "🔴⚫", "#C62828", "#212121",
        48, 72, 11_000_000, 28, 66,
        "B", "Ilha do Retiro", 26_418, 1905, "STC",
    ),
    Clube(
        "São Bernardo", "SBR", "São Bernardo do Campo", "SP", "🟡⚫", "#F9A825", "#212121",
        38, 62, 3_000_000, 5, 45,
        "B", "1º de Maio", 15_000, 2004, "INL",
    ),
    Clube(
        "Vila Nova", "VIL", "Goiânia", "GO", "🔴⚪", "#C62828", "#FFFFFF",
        40, 66, 5_000_000, 18, 52,
        "B", "Serra Dourada", 42_000, 1943, "GOI",
    ),

    # ============================================================
    # SÉRIE C (20 clubes)
    # ============================================================
    Clube(
        "Amazonas FC", "AMA", "Manaus", "AM", "🟢🟡", "#2E7D32", "#F9A825",
        38, 62, 3_000_000, 12, 50,
        "C", "Arena da Amazônia", 44_000, 2019, "MAN",
    ),
    Clube(
        "Anápolis", "ANA", "Anápolis", "GO", "🔵⚪", "#1565C0", "#FFFFFF",
        36, 60, 2_000_000, 10, 48,
        "C", "Jonas Duarte", 15_000, 1947, "VIL",
    ),
    Clube(
        "Barra-SC", "BAR", "Itajaí", "SC", "🔵⚪", "#1565C0", "#FFFFFF",
        34, 58, 1_500_000, 6, 45,
        "C", "Arena Barra", 6_000, 2013, "JOI",
    ),
    Clube(
        "Botafogo-PB", "BPB", "João Pessoa", "PB", "⚫⚪", "#212121", "#FFFFFF",
        38, 60, 3_000_000, 20, 55,
        "C", "Almeidão", 25_000, 1932, "TRZ",
    ),
    Clube(
        "Brusque", "BRU", "Brusque", "SC", "🟡⚫", "#F9A825", "#212121",
        38, 60, 3_000_000, 12, 52,
        "C", "Augusto Bauer", 5_000, 1987, "AVA",
    ),
    Clube(
        "Caxias", "CAX", "Caxias do Sul", "RS", "🔵⚪", "#1565C0", "#FFFFFF",
        38, 60, 2_000_000, 10, 50,
        "C", "Centenário", 22_132, 1935, "YPI",
    ),
    Clube(
        "Confiança", "CON", "Aracaju", "SE", "🔵⚪", "#1565C0", "#FFFFFF",
        36, 58, 2_000_000, 15, 52,
        "C", "Batistão", 15_575, 1946, "ITA",
    ),
    Clube(
        "Ferroviária", "FER", "Araraquara", "SP", "🔴⚫", "#C62828", "#212121",
        38, 60, 3_000_000, 10, 52,
        "C", "Fonte Luminosa", 20_000, 1950, "NOV",
    ),
    Clube(
        "Figueirense", "FIG", "Florianópolis", "SC", "⚫⚪", "#212121", "#FFFFFF",
        38, 62, 3_000_000, 18, 55,
        "C", "Orlando Scarpelli", 19_584, 1921, "AVA",
    ),
    Clube(
        "Floresta", "FLO", "Fortaleza", "CE", "🟢⚪", "#2E7D32", "#FFFFFF",
        34, 56, 1_500_000, 5, 45,
        "C", "Presidente Vargas", 20_000, 2016, "ATC",
    ),
    Clube(
        "Guarani", "GUA", "Campinas", "SP", "🟢⚪", "#2E7D32", "#FFFFFF",
        38, 62, 4_000_000, 20, 56,
        "C", "Brinco de Ouro", 29_130, 1911, "PON",
    ),
    Clube(
        "Inter de Limeira", "INL", "Limeira", "SP", "⚫⚪", "#212121", "#FFFFFF",
        34, 56, 1_500_000, 8, 46,
        "C", "Limeirão", 18_000, 1947, "SBR",
    ),
    Clube(
        "Itabaiana", "ITA", "Itabaiana", "SE", "🔴⚪", "#C62828", "#FFFFFF",
        34, 56, 1_200_000, 8, 46,
        "C", "Etelvino Mendonça", 11_000, 1946, "SER",
    ),
    Clube(
        "Ituano", "ITU", "Itu", "SP", "🔴⚫", "#C62828", "#212121",
        38, 60, 3_000_000, 10, 50,
        "C", "Novelli Júnior", 18_560, 1947, "BSP",
    ),
    Clube(
        "Maranhão", "MAC", "São Luís", "MA", "🔴⚪", "#C62828", "#FFFFFF",
        34, 56, 1_200_000, 8, 46,
        "C", "Castelão", 40_000, 1932, "MOT",
    ),
    Clube(
        "Maringá", "MGA", "Maringá", "PR", "🟢⚪", "#2E7D32", "#FFFFFF",
        36, 58, 2_000_000, 10, 48,
        "C", "Willie Davids", 21_000, 2010, "LON",
    ),
    Clube(
        "Paysandu", "PAY", "Belém", "PA", "🔵⚪", "#1565C0", "#FFFFFF",
        40, 62, 4_000_000, 30, 58,
        "C", "Curuzu", 16_200, 1914, "REM",
    ),
    Clube(
        "Santa Cruz", "STA", "Recife", "PE", "🔴⚫", "#C62828", "#212121",
        42, 64, 5_000_000, 35, 62,
        "C", "Arruda", 60_344, 1914, "SPT",
    ),
    Clube(
        "Volta Redonda", "VRE", "Volta Redonda", "RJ", "🟡⚫", "#F9A825", "#212121",
        36, 58, 2_000_000, 8, 48,
        "C", "Raulino de Oliveira", 18_250, 1976, "AMR",
    ),
    Clube(
        "Ypiranga-RS", "YPI", "Erechim", "RS", "🟢⚪", "#2E7D32", "#FFFFFF",
        38, 60, 2_500_000, 10, 50,
        "C", "Colosso da Lagoa", 22_000, 1924, "CAX",
    ),

    # ============================================================
    # SÉRIE D (96 clubes) — fase nacional
    # ============================================================
    Clube(
        "ABC", "ABC", "Natal", "RN", "⚫⚪", "#212121", "#FFFFFF",
        36, 58, 2_500_000, 20, 52,
        "D", "Frasqueirão", 18_000, 1915, "ARN",
    ),
    Clube(
        "ABECAT", "ABE", "Ouvidor", "GO", "🟠⚫", "#E64A19", "#1A1A1A",
        26, 46, 400_000, 2, 36,
        "D", "Estádio Municipal de Ouvidor", 5_000, 2019, "GOA",
    ),
    Clube(
        "Altos", "ALT", "Altos", "PI", "🟢⚪", "#2E7D32", "#FFFFFF",
        32, 52, 1_000_000, 5, 44,
        "D", "Felipe Raulino", 4_000, 2013, "PIA",
    ),
    Clube(
        "America-RJ", "AME", "Rio de Janeiro", "RJ", "🔴⚪", "#C8102E", "#FFFFFF",
        30, 52, 1_000_000, 12, 46,
        "D", "Edson Passos", 13_000, 1904, "MAD",
    ),
    Clube(
        "América-RN", "ARN", "Natal", "RN", "🟢🔴", "#2E7D32", "#C62828",
        34, 56, 1_800_000, 12, 48,
        "D", "Arena das Dunas", 32_000, 1915, "ABC",
    ),
    Clube(
        "Aparecidense", "APD", "Aparecida de Goiânia", "GO", "🟡🔵", "#D9B44A", "#1B3A6B",
        32, 52, 1_000_000, 5, 44,
        "D", "Annibal Batista de Toledo", 8_000, 1985, "CRAC",
    ),
    Clube(
        "Araguaína", "ARA", "Araguaína", "TO", "🔴⚪", "#C62828", "#FFFFFF",
        26, 46, 400_000, 3, 36,
        "D", "Mirandão", 10_000, 1979, "TOC",
    ),
    Clube(
        "ASA", "ASA", "Arapiraca", "AL", "⚫⚪", "#212121", "#FFFFFF",
        32, 54, 1_200_000, 8, 46,
        "D", "Coaracy da Mata Fonseca", 17_500, 1952, "CSA",
    ),
    Clube(
        "Atlético-CE", "ATC", "Fortaleza", "CE", "🔴⚫", "#C8102E", "#212121",
        30, 52, 900_000, 5, 44,
        "D", "Presidente Vargas", 20_000, 1997, "FLO",
    ),
    Clube(
        "Atlético de Alagoinhas", "AAL", "Alagoinhas", "BA", "🔴⚫", "#C62828", "#212121",
        30, 50, 800_000, 4, 42,
        "D", "Carneirão", 12_000, 1970, "JZE",
    ),
    Clube(
        "Azuriz", "AZU", "Pato Branco", "PR", "🔵⚪", "#1565C0", "#FFFFFF",
        28, 48, 500_000, 3, 38,
        "D", "Os Pioneiros", 15_000, 2017, "SJP",
    ),
    Clube(
        "Betim", "BET", "Betim", "MG", "🔵⚪", "#1565C0", "#FFFFFF",
        28, 48, 600_000, 3, 38,
        "D", "Estádio Municipal de Betim", 10_000, 2011, "DGV",
    ),
    Clube(
        "Blumenau", "BLU", "Blumenau", "SC", "🟢🔴", "#0F6B3E", "#7A1230",
        28, 48, 500_000, 3, 38,
        "D", "Estádio Municipal de Blumenau", 8_000, 2020, "MDI",
    ),
    Clube(
        "Brasil de Pelotas", "BRS", "Pelotas", "RS", "🟡⚫", "#F9A825", "#212121",
        32, 54, 1_500_000, 8, 46,
        "D", "Bento Freitas", 18_000, 1911, "JUV",
    ),
    Clube(
        "Brasiliense", "BSE", "Taguatinga", "DF", "🟡⚫", "#F4C300", "#212121",
        30, 50, 1_000_000, 5, 44,
        "D", "Serejão", 30_000, 2000, "GAM",
    ),
    Clube(
        "Capital", "CPT", "Brasília", "DF", "🔵⚪", "#1565C0", "#FFFFFF",
        26, 46, 400_000, 2, 36,
        "D", "Estádio JK", 8_000, 2005, "CEI",
    ),
    Clube(
        "Ceilândia", "CEI", "Ceilândia", "DF", "⚫⚪", "#212121", "#FFFFFF",
        28, 48, 500_000, 3, 40,
        "D", "Abadião", 5_000, 1974, "GAM",
    ),
    Clube(
        "Central", "CEN", "Caruaru", "PE", "⚫⚪", "#212121", "#FFFFFF",
        32, 54, 1_200_000, 8, 46,
        "D", "Lacerdão", 19_000, 1919, "RET",
    ),
    Clube(
        "Cianorte", "CIA", "Cianorte", "PR", "🟢⚪", "#2E7D32", "#FFFFFF",
        30, 50, 800_000, 4, 42,
        "D", "Albino Turbay", 4_000, 2002, "FCC",
    ),
    Clube(
        "CRAC", "CRAC", "Catalão", "GO", "🔵⚪", "#1E88E5", "#FFFFFF",
        28, 48, 700_000, 4, 40,
        "D", "Genervino da Fonseca", 12_000, 1937, "APD",
    ),
    Clube(
        "CSA", "CSA", "Maceió", "AL", "🔵⚪", "#1565C0", "#FFFFFF",
        36, 58, 2_500_000, 18, 52,
        "D", "Rei Pelé", 17_126, 1913, "CRB",
    ),
    Clube(
        "CSE", "CSE", "Palmeira dos Índios", "AL", "🟢🔴", "#0E7A3F", "#C62828",
        26, 46, 400_000, 3, 38,
        "D", "Juca Sampaio", 8_000, 1918, "ASA",
    ),
    Clube(
        "Decisão", "DEC", "Recife", "PE", "🔵⚪", "#1B2A6B", "#FFFFFF",
        26, 46, 300_000, 2, 36,
        "D", "Estádio Municipal do Recife", 5_000, 2019, "MAG",
    ),
    Clube(
        "Democrata GV", "DGV", "Governador Valadares", "MG", "⚫⚪", "#212121", "#FFFFFF",
        28, 48, 500_000, 4, 40,
        "D", "Mamudão", 8_000, 1914, "POU",
    ),
    Clube(
        "FC Cascavel", "FCC", "Cascavel", "PR", "🟡⚫", "#F5C518", "#212121",
        30, 50, 900_000, 5, 44,
        "D", "Olímpico Regional", 25_000, 2007, "CIA",
    ),
    Clube(
        "Ferroviário", "FER", "Fortaleza", "CE", "🔴⚫", "#C8102E", "#212121",
        34, 56, 2_000_000, 10, 48,
        "D", "Elzir Cabral", 8_000, 1933, "FLO",
    ),
    Clube(
        "Fluminense-PI", "FPI", "Teresina", "PI", "🔴⚪", "#C62828", "#FFFFFF",
        26, 46, 400_000, 3, 38,
        "D", "Albertão", 44_000, 1937, "PNB",
    ),
    Clube(
        "Galvez", "GAL", "Rio Branco", "AC", "🟡⚫", "#F5C518", "#212121",
        26, 46, 400_000, 2, 36,
        "D", "Arena da Floresta", 20_000, 2011, "HUM",
    ),
    Clube(
        "Gama", "GAM", "Gama", "DF", "🟢⚪", "#2E7D32", "#FFFFFF",
        30, 52, 1_000_000, 6, 44,
        "D", "Bezerrão", 20_000, 1975, "BSE",
    ),
    Clube(
        "GAS", "GAS", "Boa Vista", "RR", "🔴⚪", "#C62828", "#FFFFFF",
        24, 44, 200_000, 1, 34,
        "D", "Canarinho", 4_000, 1978, "MOR",
    ),
    Clube(
        "Goiatuba", "GTB", "Goiatuba", "GO", "🔵⚪", "#1565C0", "#FFFFFF",
        26, 46, 400_000, 2, 36,
        "D", "Divino Garcia Rosa", 3_000, 1975, "ABE",
    ),
    Clube(
        "Guaporé", "GPR", "Rolim de Moura", "RO", "🟠🟢", "#E8730C", "#1E7A3F",
        24, 44, 200_000, 1, 34,
        "D", "Estádio Municipal de Rolim de Moura", 5_000, 1994, "PVH",
    ),
    Clube(
        "Guarany de Bagé", "GBA", "Bagé", "RS", "🔴⚪", "#C8102E", "#FFFFFF",
        28, 48, 600_000, 5, 40,
        "D", "Estrela d'Alva", 12_000, 1907, "SJO",
    ),
    Clube(
        "Humaitá-AC", "HUM", "Rio Branco", "AC", "🟢🔴", "#0E7A3F", "#C8102E",
        26, 46, 400_000, 2, 36,
        "D", "Arena da Floresta", 20_000, 2003, "GAL",
    ),
    Clube(
        "IAPE", "IAPE", "São Luís", "MA", "🔵🟡", "#1B3A8B", "#F5C518",
        26, 46, 400_000, 2, 36,
        "D", "Nhozinho Santos", 12_000, 2018, "IMP",
    ),
    Clube(
        "Iguatu", "IGU", "Iguatu", "CE", "🔵⚪", "#1E88E5", "#FFFFFF",
        28, 48, 600_000, 4, 40,
        "D", "Morenão", 6_000, 2010, "MCN",
    ),
    Clube(
        "Imperatriz", "IMP", "Imperatriz", "MA", "🔴⚪", "#C62828", "#FFFFFF",
        28, 50, 700_000, 4, 42,
        "D", "Frei Epifânio", 12_000, 1964, "MOT",
    ),
    Clube(
        "Independência", "IND", "Rio Branco", "AC", "🔴🟢", "#C62828", "#0E7A3F",
        26, 46, 400_000, 2, 36,
        "D", "Arena da Floresta", 20_000, 1946, "GAL",
    ),
    Clube(
        "Inhumas", "INH", "Inhumas", "GO", "🔴⚪", "#7A1B2E", "#FFFFFF",
        24, 44, 200_000, 2, 34,
        "D", "Estádio Zico Brandão", 4_380, 1944, "ABE",
    ),
    Clube(
        "Jacuipense", "JAC", "Riachão do Jacuípe", "BA", "🔵⚪", "#1565C0", "#FFFFFF",
        28, 48, 600_000, 4, 40,
        "D", "Valfredão", 5_000, 1997, "JZE",
    ),
    Clube(
        "Joinville", "JOI", "Joinville", "SC", "🔴⚫", "#C62828", "#212121",
        32, 54, 1_500_000, 10, 46,
        "D", "Arena Joinville", 22_400, 1976, "BAR",
    ),
    Clube(
        "Juazeirense", "JZE", "Juazeiro", "BA", "🔵⚪", "#1565C0", "#FFFFFF",
        30, 50, 800_000, 5, 42,
        "D", "Adauto Moraes", 6_000, 2006, "AAL",
    ),
    Clube(
        "Lagarto", "LAG", "Lagarto", "SE", "🟢⚪", "#0E7A3F", "#FFFFFF",
        26, 46, 400_000, 3, 38,
        "D", "Barretão", 8_000, 2010, "SER",
    ),
    Clube(
        "Laguna", "LGN", "Natal", "RN", "🔵⚪", "#1565C0", "#FFFFFF",
        24, 44, 300_000, 2, 34,
        "D", "Estádio Municipal de Natal", 5_000, 2019, "ARN",
    ),
    Clube(
        "Luverdense", "LUV", "Lucas do Rio Verde", "MT", "🟢⚪", "#2E7D32", "#FFFFFF",
        30, 50, 900_000, 5, 42,
        "D", "Passo das Emas", 10_000, 2004, "UNI",
    ),
    Clube(
        "Madureira", "MAD", "Rio de Janeiro", "RJ", "🔵🔴", "#1565C0", "#C62828",
        28, 50, 800_000, 8, 44,
        "D", "Conselheiro Galvão", 5_000, 1914, "AMR",
    ),
    Clube(
        "Maguary", "MAG", "Recife", "PE", "🔵⚪", "#1565C0", "#FFFFFF",
        24, 44, 300_000, 2, 34,
        "D", "Estádio Municipal do Recife", 6_000, 2008, "DEC",
    ),
    Clube(
        "Manauara", "MNR", "Manaus", "AM", "🟡⚫", "#F9A825", "#212121",
        28, 48, 700_000, 4, 40,
        "D", "Arena da Amazônia", 44_000, 2020, "NAC",
    ),
    Clube(
        "Manaus", "MAN", "Manaus", "AM", "🟢⚪", "#2E7D32", "#FFFFFF",
        34, 56, 2_000_000, 8, 48,
        "D", "Arena da Amazônia", 44_000, 2013, "NAC",
    ),
    Clube(
        "Maracanã", "MCN", "Maracanaú", "CE", "🔵⚪", "#1565C0", "#FFFFFF",
        26, 46, 400_000, 3, 38,
        "D", "Estádio Municipal de Maracanaú", 8_000, 2001, "IGU",
    ),
    Clube(
        "Marcílio Dias", "MDI", "Itajaí", "SC", "🔵🔴", "#17337E", "#C8102E",
        28, 48, 600_000, 4, 40,
        "D", "Hercílio Luz", 8_000, 1919, "BLU",
    ),
    Clube(
        "Maricá", "MRC", "Maricá", "RJ", "🟡⚫", "#F9A825", "#212121",
        26, 46, 500_000, 3, 38,
        "D", "Estádio Municipal de Maricá", 8_000, 2021, "SCR",
    ),
    Clube(
        "Mixto", "MIX", "Cuiabá", "MT", "⚫⚪", "#212121", "#FFFFFF",
        26, 48, 500_000, 4, 40,
        "D", "Dutrinha", 4_000, 1934, "LUV",
    ),
    Clube(
        "Monte Roraima", "MOR", "Boa Vista", "RR", "🟢🟡", "#0E7A3F", "#F5C518",
        24, 44, 200_000, 1, 34,
        "D", "Canarinho", 4_000, 2016, "GAS",
    ),
    Clube(
        "Moto Club", "MOT", "São Luís", "MA", "🔴⚫", "#C8102E", "#212121",
        30, 52, 1_000_000, 8, 46,
        "D", "Nhozinho Santos", 12_000, 1937, "SAM",
    ),
    Clube(
        "Nacional", "NAC", "Manaus", "AM", "🔵⚪", "#1565C0", "#FFFFFF",
        30, 52, 1_200_000, 8, 46,
        "D", "Arena da Amazônia", 44_000, 1913, "MAN",
    ),
    Clube(
        "Noroeste", "NOR", "Bauru", "SP", "🔴⚪", "#C62828", "#FFFFFF",
        30, 52, 900_000, 6, 44,
        "D", "Alfredo de Castilho", 18_000, 1911, "XVP",
    ),
    Clube(
        "Nova Iguaçu", "NIG", "Nova Iguaçu", "RJ", "🟢⚪", "#2E7D32", "#FFFFFF",
        28, 48, 700_000, 5, 42,
        "D", "Laranjão", 5_000, 1991, "PRJ",
    ),
    Clube(
        "Operário-MS", "OMS", "Campo Grande", "MS", "🔵⚪", "#1565C0", "#FFFFFF",
        28, 50, 700_000, 4, 42,
        "D", "Morenão", 44_000, 1948, "PAN",
    ),
    Clube(
        "Operário Várzea-grandense", "OPV", "Várzea Grande", "MT", "🟡⚫", "#F9A825", "#212121",
        26, 46, 400_000, 3, 38,
        "D", "Dito Souza", 4_000, 1947, "PRI",
    ),
    Clube(
        "Oratório", "ORA", "Macapá", "AP", "🔵⚪", "#1B3A8B", "#FFFFFF",
        24, 44, 300_000, 2, 34,
        "D", "Zerão", 10_000, 2020, "TRM",
    ),
    Clube(
        "Pantanal", "PAN", "Campo Grande", "MS", "🟢⚪", "#2E7D32", "#FFFFFF",
        24, 44, 300_000, 2, 34,
        "D", "Morenão", 44_000, 2021, "OPM",
    ),
    Clube(
        "Parnahyba", "PNB", "Parnaíba", "PI", "🔵⚪", "#1B3A8B", "#FFFFFF",
        26, 46, 500_000, 3, 38,
        "D", "Pedro Alelaf", 4_000, 1913, "FLP",
    ),
    Clube(
        "Piauí", "PIA", "Teresina", "PI", "🔴⚪", "#C62828", "#FFFFFF",
        28, 48, 600_000, 4, 40,
        "D", "Albertão", 44_000, 1948, "FLP",
    ),
    Clube(
        "Porto-BA", "PBA", "Porto Seguro", "BA", "🟢⚪", "#2E7D32", "#FFFFFF",
        24, 44, 300_000, 2, 34,
        "D", "Estádio Municipal de Porto Seguro", 5_000, 2010, "JAC",
    ),
    Clube(
        "Porto Velho", "PVL", "Porto Velho", "RO", "🟢⚪", "#2E7D32", "#FFFFFF",
        26, 46, 400_000, 3, 38,
        "D", "Aluizão", 5_000, 2019, "GPR",
    ),
    Clube(
        "Portuguesa", "POR", "São Paulo", "SP", "🔴⚪", "#C62828", "#FFFFFF",
        34, 56, 2_500_000, 12, 50,
        "D", "Canindé", 21_000, 1920, "BSP",
    ),
    Clube(
        "Portuguesa-RJ", "PRJ", "Rio de Janeiro", "RJ", "🔴⚪", "#C62828", "#FFFFFF",
        28, 48, 700_000, 5, 42,
        "D", "Laranjeiras", 8_000, 1924, "NIG",
    ),
    Clube(
        "Pouso Alegre", "POU", "Pouso Alegre", "MG", "🔴⚫", "#C8102E", "#212121",
        28, 48, 600_000, 4, 40,
        "D", "Manduzão", 10_000, 1991, "DGV",
    ),
    Clube(
        "Primavera-MT", "PRI", "Primavera do Leste", "MT", "🔴⚪", "#C62828", "#FFFFFF",
        26, 46, 500_000, 3, 38,
        "D", "Estádio Municipal de Primavera do Leste", 8_000, 1998, "OPV",
    ),
    Clube(
        "Real Noroeste", "RNO", "Águia Branca", "ES", "🟢🟡", "#0E7A3F", "#F5C518",
        26, 46, 400_000, 2, 36,
        "D", "José Olímpio da Rocha", 3_000, 2008, "VES",
    ),
    Clube(
        "Retrô", "RET", "Camaragibe", "PE", "🔴⚫", "#C62828", "#212121",
        32, 54, 1_500_000, 8, 46,
        "D", "Arena de Pernambuco", 46_000, 2016, "CEN",
    ),
    Clube(
        "Rio Branco-ES", "RBE", "Vitória", "ES", "🔴⚪", "#C62828", "#FFFFFF",
        28, 48, 700_000, 4, 42,
        "D", "Kleber Andrade", 21_000, 1913, "VES",
    ),
    Clube(
        "Sampaio Corrêa-MA", "SAM", "São Luís", "MA", "🟡🔴", "#FFC107", "#C62828",
        34, 56, 2_000_000, 12, 50,
        "D", "Castelão", 40_000, 1923, "MOT",
    ),
    Clube(
        "Sampaio Corrêa-RJ", "SCR", "Saquarema", "RJ", "🔴⚫", "#C62828", "#212121",
        26, 46, 400_000, 3, 38,
        "D", "Estádio Municipal de Saquarema", 5_000, 1956, "MRC",
    ),
    Clube(
        "Santa Catarina", "SCT", "Rio do Sul", "SC", "🔵⚪", "#1565C0", "#FFFFFF",
        24, 44, 300_000, 2, 34,
        "D", "Estádio Municipal de Rio do Sul", 5_000, 2012, "BLU",
    ),
    Clube(
        "Sergipe", "SER", "Aracaju", "SE", "🔴⚪", "#C8102E", "#FFFFFF",
        32, 54, 1_200_000, 8, 46,
        "D", "Batistão", 15_575, 1909, "ITA",
    ),
    Clube(
        "Serra Branca", "SBR", "Serra Branca", "PB", "🟢🔵", "#0E7A3F", "#1B3A8B",
        24, 44, 300_000, 2, 34,
        "D", "Estádio Municipal de Serra Branca", 3_000, 2010, "SOU",
    ),
    Clube(
        "Sousa", "SOU", "Sousa", "PB", "🟢⚪", "#2E7D32", "#FFFFFF",
        26, 46, 500_000, 3, 40,
        "D", "Marizão", 9_000, 1957, "TRZ",
    ),
    Clube(
        "São Joseense", "SJP", "São José dos Pinhais", "PR", "🔵🟡", "#1B3A8B", "#F5C518",
        26, 46, 400_000, 3, 38,
        "D", "Estádio do Pinhão", 5_000, 2000, "AZU",
    ),
    Clube(
        "São José-RS", "SJO", "Porto Alegre", "RS", "🔵⚪", "#1565C0", "#FFFFFF",
        28, 48, 700_000, 4, 40,
        "D", "Passo d'Areia", 15_000, 1913, "GBA",
    ),
    Clube(
        "São Luiz", "SLU", "Ijuí", "RS", "🔴⚪", "#C62828", "#FFFFFF",
        28, 48, 600_000, 4, 40,
        "D", "19 de Outubro", 6_000, 1913, "GBA",
    ),
    Clube(
        "São Raimundo-RR", "SRR", "Boa Vista", "RR", "🔵⚪", "#1565C0", "#FFFFFF",
        26, 46, 400_000, 2, 36,
        "D", "Canarinho", 4_000, 1963, "GAS",
    ),
    Clube(
        "Tirol", "TIR", "Fortaleza", "CE", "🟡🔵", "#F9A825", "#1565C0",
        24, 44, 300_000, 2, 34,
        "D", "Presidente Vargas", 20_000, 2018, "MCN",
    ),
    Clube(
        "Tocantinópolis", "TOC", "Tocantinópolis", "TO", "🔵⚪", "#1565C0", "#FFFFFF",
        26, 46, 400_000, 2, 38,
        "D", "Ribeirão", 5_000, 1974, "ARA",
    ),
    Clube(
        "Tombense", "TOM", "Tombos", "MG", "🟢⚪", "#2E7D32", "#FFFFFF",
        34, 56, 2_000_000, 6, 48,
        "D", "Almeidão", 3_000, 1914, "ATH",
    ),
    Clube(
        "Trem", "TRM", "Macapá", "AP", "🔴⚫", "#C62828", "#212121",
        26, 46, 400_000, 3, 38,
        "D", "Zerão", 10_000, 1947, "ORA",
    ),
    Clube(
        "Treze", "TRZ", "Campina Grande", "PB", "⚫⚪", "#212121", "#FFFFFF",
        32, 54, 1_500_000, 12, 46,
        "D", "Amigão", 25_000, 1925, "SOU",
    ),
    Clube(
        "Tuna Luso", "TLB", "Belém", "PA", "🔵⚪", "#1565C0", "#FFFFFF",
        28, 48, 700_000, 5, 42,
        "D", "Francisco Vasques", 5_000, 1903, "AGM",
    ),
    Clube(
        "Uberlândia", "UBE", "Uberlândia", "MG", "🟢⚪", "#2E7D32", "#FFFFFF",
        30, 52, 1_200_000, 8, 46,
        "D", "Parque do Sabiá", 45_000, 1949, "TOM",
    ),
    Clube(
        "União Rondonópolis", "UNI", "Rondonópolis", "MT", "🔴⚪", "#C8102E", "#FFFFFF",
        28, 48, 700_000, 4, 42,
        "D", "Caldeirão", 19_000, 1957, "LUV",
    ),
    Clube(
        "Velo Clube", "VEL", "Rio Claro", "SP", "🟢🔴", "#0E7A3F", "#C8102E",
        28, 48, 700_000, 4, 42,
        "D", "Benitão", 8_000, 1910, "NOR",
    ),
    Clube(
        "Vitória-ES", "VES", "Vitória", "ES", "🔵⚪", "#1B3A8B", "#FFFFFF",
        26, 46, 400_000, 3, 38,
        "D", "Salvador Costa", 3_000, 1903, "RNO",
    ),
    Clube(
        "XV de Piracicaba", "XVP", "Piracicaba", "SP", "⚫⚪", "#212121", "#FFFFFF",
        30, 52, 1_000_000, 6, 44,
        "D", "Barão de Serra Negra", 18_000, 1913, "NOR",
    ),
    Clube(
        "Água Santa", "AGS", "Diadema", "SP", "🔵⚪", "#1565C0", "#FFFFFF",
        32, 52, 1_200_000, 5, 44,
        "D", "Arena Inamar", 10_000, 1981, "NOR",
    ),
    Clube(
        "Águia de Marabá", "AGM", "Marabá", "PA", "🔵⚪", "#1565C0", "#FFFFFF",
        30, 50, 800_000, 4, 42,
        "D", "Zinho de Oliveira", 5_000, 1982, "TUN",
    ),
]

DIVISOES = ("A", "B", "C", "D")
NOMES_DIVISAO = {"A": "Série A", "B": "Série B", "C": "Série C", "D": "Série D"}
TOTAL_TIMES = len(TIMES_DATA)


def clubes_por_divisao(divisao: str) -> list[Clube]:
    """Fichas de uma divisão: 'A', 'B', 'C' ou 'D'."""
    div = str(divisao).upper()
    if div not in DIVISOES:
        raise ValueError(f"Divisão inválida: {divisao!r}. Use uma de {DIVISOES}.")
    return [c for c in TIMES_DATA if c.divisao == div]
