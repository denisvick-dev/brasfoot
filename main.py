"""
Demo: roda uma temporada inteira no terminal.

Uso:
    python main.py            # Brasileirão com 20 clubes (Série A)
    python main.py 24         # 24 clubes
    python main.py 61         # banco inteiro (61 clubes)
    python main.py 20 7       # 20 clubes, semente 7 (reproduzível)
"""

import random
import sys
import time

from game.banco_dados import criar_times, resumo_banco
from game.campeonato import League
from game.mercado import Market


def linha(tam: int = 78) -> str:
    return "-" * tam


def main():
    qtd = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    semente = int(sys.argv[2]) if len(sys.argv) > 2 else 42

    random.seed(semente)

    print(resumo_banco())
    print(linha())

    times = criar_times(qtd)
    time_jogador = times[0].nome
    print(f"Temporada com {len(times)} clubes | seu time: {time_jogador}")
    print(linha())

    liga = League(times)
    print(f"Rodadas: {liga.total_rodadas} | jogos/rodada: {len(liga.calendario[0])}")

    inicio = time.time()
    total_gols = 0
    total_jogos = 0
    vitorias_casa = 0
    empates = 0
    while not liga.campeonato_encerrado:
        for p in liga.simular_rodada(time_jogador):
            total_gols += p.gols_casa + p.gols_fora
            total_jogos += 1
            if p.gols_casa > p.gols_fora:
                vitorias_casa += 1
            elif p.gols_casa == p.gols_fora:
                empates += 1
    duracao = time.time() - inicio

    print(f"Simulação concluída em {duracao:.2f}s ({total_jogos} partidas)")
    print(f"Gols/jogo ......... {total_gols / total_jogos:.2f}")
    print(f"Vitórias mandante . {100 * vitorias_casa / total_jogos:.1f}%")
    print(f"Empates ........... {100 * empates / total_jogos:.1f}%")
    print(linha())

    # Classificação
    print(f"{'#':>2} {'TIME':<16} {'P':>3} {'J':>3} {'V':>3} {'E':>3} {'D':>3} "
          f"{'GP':>4} {'GC':>4} {'SG':>4} {'OVR':>4} {'CAIXA (R$)':>14}")
    for i, t in enumerate(liga.classificacao, 1):
        marca = " <<" if t.nome == time_jogador else ""
        print(f"{i:>2} {t.nome:<16} {t.pontos:>3} {t.jogos_campeonato:>3} "
              f"{t.vitorias:>3} {t.empates:>3} {t.derrotas:>3} "
              f"{t.gols_pro:>4} {t.gols_contra:>4} {t.saldo_gols:>4} "
              f"{t.overall_time:>4} {t.financas:>14,}{marca}")

    print(linha())
    print("Artilharia:")
    for i, (j, sigla) in enumerate(liga.artilharia(10), 1):
        print(f"  {i:>2}. {j.nome:<22} {sigla}  {j.gols} gols "
              f"({j.assistencias} assist, {j.jogos} jogos)")

    mercado = Market(times)
    print(linha())
    print(f"Mercado: {len(mercado.ofertas_disponiveis)} jogadores disponíveis")
    livre = mercado.gerar_jogador_livre()
    print(f"Jogador livre gerado: {livre.nome} ({livre.posicao}, "
          f"ovr {livre.overall}, R$ {livre.valor_mercado:,})")

    print(linha())
    print(f"Notícias geradas: {len(liga.noticias)}")
    for n in liga.noticias[-3:]:
        print(f"  [{n.tipo}] {n.titulo}")


if __name__ == "__main__":
    main()
