"""
Diagnóstico / calibração do motor.

Roda temporadas inteiras e compara o comportamento do jogo com as metas
(números do Brasileirão real). Não é parte do jogo — é a ferramenta usada
para calibrar as constantes de MatchEngine.

Uso:
    python diagnostico.py
"""

import random
import statistics
import time
from collections.abc import Sequence

from game.banco_dados import criar_times, buscar_clube
from game.campeonato import League

METAS = {
    "gols/jogo": (2.2, 2.7),
    "empates %": (22, 30),
    "mandante %": (42, 50),
    "corr ovr x pts": (0.55, 1.0),
}


def pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys, strict=True))
    den = (sum((a - mx) ** 2 for a in xs) ** 0.5) * (
        sum((b - my) ** 2 for b in ys) ** 0.5
    )
    return num / den if den else 0.0


def spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    def posto(v):
        ordem = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for pos, i in enumerate(ordem):
            r[i] = pos
        return r

    return pearson(posto(xs), posto(ys))


def temporada(n_times: int, semente: int) -> dict[str, float]:
    random.seed(semente)
    times = criar_times(n_times)
    sigla_por_nome = {t.nome: t.sigla for t in times}
    liga = League(times)

    jogos = empates = casa = fora = gols = 0
    publico_acima = 0
    inicio = time.time()

    while not liga.campeonato_encerrado:
        for p in liga.simular_rodada(times[0].nome):
            jogos += 1
            gols += p.gols_casa + p.gols_fora
            if p.gols_casa == p.gols_fora:
                empates += 1
            elif p.gols_casa > p.gols_fora:
                casa += 1
            else:
                fora += 1
            clube = buscar_clube(sigla_por_nome[p.time_casa])
            if clube is not None and p.publico > clube.capacidade:
                publico_acima += 1

    tabela = liga.classificacao
    jogadores = [j for t in times for j in t.jogadores]
    return {
        "jogos": jogos,
        "gols/jogo": gols / jogos,
        "empates %": 100 * empates / jogos,
        "mandante %": 100 * casa / jogos,
        "visitante %": 100 * fora / jogos,
        "corr ovr x pts": spearman(
            [float(t.overall_time) for t in tabela],
            [float(t.pontos) for t in tabela],
        ),
        "caixa negativo": sum(1 for t in times if t.financas < 0),
        "artilheiro": liga.artilharia(1)[0][0].gols if liga.artilharia(1) else 0,
        "energia media": statistics.mean(j.energia for j in jogadores),
        "lesionados": sum(1 for j in jogadores if j.lesionado),
        "publico > capacidade": publico_acima,
        "segundos": time.time() - inicio,
    }


def medir(n_times: int, temporadas: int, semente: int = 1) -> None:
    print(f"\n=== {n_times} clubes, {temporadas} temporada(s) ===")
    acc: dict[str, list[float]] = {}
    for s in range(semente, semente + temporadas):
        r = temporada(n_times, s)
        for k, v in r.items():
            acc.setdefault(k, []).append(v)

    for k, valores in acc.items():
        media = statistics.mean(valores)
        if k in METAS:
            lo, hi = METAS[k]
            ok = "OK " if lo <= media <= hi else "!! "
        else:
            ok = "   "
        sufixo = f"   (meta {METAS[k][0]}–{METAS[k][1]})" if k in METAS else ""
        print(f"  {ok}{k:<22} {media:>8.2f}{sufixo}")


if __name__ == "__main__":
    medir(20, 5, semente=1)
    medir(156, 1, semente=2)
