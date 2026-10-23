"""
Finanças do clube: extrato, resumo e premiação.

Todo dinheiro que entra ou sai passa por :func:`registrar`, que atualiza o
caixa (``Time.financas``) e guarda uma linha no extrato do clube. Assim o
painel consegue mostrar de onde veio (e para onde foi) o dinheiro da
temporada, como no Brasfoot.

O extrato é uma lista de dicionários — simples o bastante para ir e voltar do
JSON em ``game/persistencia.py`` sem conversão especial.
"""

from __future__ import annotations

from game.modelos import Time

# Quantos lançamentos ficam guardados por clube (os mais antigos caem fora).
LIMITE_EXTRATO = 400

TIPOS: dict[str, str] = {
    "bilheteria": "🎟️ Bilheteria",
    "tv": "📺 Cota de TV",
    "patrocinio": "🤝 Patrocínio",
    "salarios": "💼 Salários",
    "transferencia": "🔁 Transferências",
    "premiacao": "🏆 Premiação",
    "estadio": "🏟️ Estádio",
    "outros": "• Outros",
}

# Quanto cada divisão paga por posição (1º, 2º, 3º …). As demais posições
# recebem o valor mínimo da tabela.
_PREMIOS: dict[str, tuple[int, ...]] = {
    "A": (60_000_000, 35_000_000, 25_000_000, 18_000_000),
    "B": (20_000_000, 12_000_000, 8_000_000, 5_000_000),
    "C": (8_000_000, 5_000_000, 3_000_000, 2_000_000),
    "D": (3_000_000, 2_000_000, 1_200_000, 800_000),
}
_PREMIO_MINIMO = {"A": 8_000_000, "B": 2_500_000, "C": 900_000, "D": 300_000}
_PREMIO_COPA = (30_000_000, 12_000_000)


def registrar(time: Time, rodada: int, tipo: str, descricao: str, valor: int) -> None:
    """Lança uma receita (valor > 0) ou despesa (valor < 0) no clube."""
    if tipo not in TIPOS:
        tipo = "outros"
    valor = int(valor)
    time.financas += valor
    time.extrato.append(
        {
            "rodada": int(rodada),
            "tipo": tipo,
            "descricao": descricao,
            "valor": valor,
        }
    )
    if len(time.extrato) > LIMITE_EXTRATO:
        del time.extrato[:-LIMITE_EXTRATO]


def receitas(time: Time, rodada_minima: int = 0) -> int:
    """Total de receitas do extrato (a partir de ``rodada_minima``)."""
    return sum(
        e["valor"]
        for e in time.extrato
        if e["valor"] > 0 and e["rodada"] >= rodada_minima
    )


def despesas(time: Time, rodada_minima: int = 0) -> int:
    """Total de despesas do extrato (em módulo)."""
    return -sum(
        e["valor"]
        for e in time.extrato
        if e["valor"] < 0 and e["rodada"] >= rodada_minima
    )


def resumo(time: Time) -> dict[str, int]:
    """Saldo por tipo de lançamento, do maior para o menor."""
    totais: dict[str, int] = {}
    for lancamento in time.extrato:
        tipo = lancamento["tipo"]
        totais[tipo] = totais.get(tipo, 0) + lancamento["valor"]
    return dict(sorted(totais.items(), key=lambda item: abs(item[1]), reverse=True))


def ultimos(time: Time, quantidade: int = 20) -> list[dict]:
    """Os lançamentos mais recentes, do mais novo para o mais antigo."""
    return list(reversed(time.extrato[-quantidade:]))


def premio_temporada(divisao: str, posicao: int, total_times: int) -> int:
    """Premiação de fim de temporada pela posição na divisão."""
    divisao = (divisao or "A").upper()
    tabela = _PREMIOS.get(divisao, _PREMIOS["A"])
    minimo = _PREMIO_MINIMO.get(divisao, _PREMIO_MINIMO["A"])
    if posicao <= 0 or posicao > total_times:
        return 0
    if posicao <= len(tabela):
        return tabela[posicao - 1]
    return minimo


def premio_copa(fase: str) -> int:
    """Premiação da Copa do Brasil: campeão e vice."""
    fase = (fase or "").lower()
    if "campe" in fase and "vice" not in fase:
        return _PREMIO_COPA[0]
    if "vice" in fase or "final" in fase:
        return _PREMIO_COPA[1]
    return 0
