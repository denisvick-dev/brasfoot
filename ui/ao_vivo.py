"""Rodada "ao vivo": relógio de 0' a 90'+ e placares aparecendo no tempo certo.

O motor simula a rodada inteira em milissegundos. Para o jogo parecer Brasfoot,
a tela **rejoga** o resultado guardado: cada partida já traz a lista de gols com
minuto (`Partida.gols`), então dá para desenhar o placar de cada jogo aos poucos,
como se o árbitro estivesse apitando naquele instante.

Tudo aqui é função pura (sem Streamlit), para os testes conferirem o quadro de
cada minuto sem precisar abrir a interface.
"""

from game.modelos import Gol, Partida
from ui.sons import caixa_de_som

#: Duração total do relógio, em segundos, por opção de velocidade.
VELOCIDADES: dict[str, float] = {
    "⏩ Rápida": 2.0,
    "▶️ Normal": 5.0,
    "🐢 Detalhada": 10.0,
}

VELOCIDADE_PADRAO = "▶️ Normal"

#: De quantos em quantos minutos o relógio avança (3' por quadro ≈ 31 quadros).
PASSO_MINUTOS = 3

#: Fim do tempo regulamentar; o que passar disso vira acréscimo ("90+2'").
MINUTO_REGULAMENTAR = 90

#: Por quantos minutos de jogo o gol continua piscando em vermelho na tela.
JANELA_FLASH = 3


def minuto_final(placares: dict[str, list[Partida]]) -> int:
    """Último minuto que precisa aparecer no relógio (respeita os acréscimos)."""
    ultimo = MINUTO_REGULAMENTAR
    for partidas in placares.values():
        for partida in partidas:
            for gol in partida.gols:
                ultimo = max(ultimo, gol.minuto)
    return ultimo


def passos(final: int, passo: int = PASSO_MINUTOS) -> list[int]:
    """Minutos mostrados na animação: 0, 3, 6, … e o último minuto exato."""
    if final <= 0:
        return [0]
    lista = list(range(0, final + 1, max(1, passo)))
    if lista[-1] != final:
        lista.append(final)
    return lista


def relogio(minuto: int) -> str:
    """Texto do relógio: `45'` no tempo normal, `90+2'` nos acréscimos."""
    if minuto > MINUTO_REGULAMENTAR:
        return f"{MINUTO_REGULAMENTAR}+{minuto - MINUTO_REGULAMENTAR}'"
    return f"{minuto}'"


def quadro(
    placares: dict[str, list[Partida]], minuto: int
) -> dict[str, list[tuple[Partida, int, int]]]:
    """Placar de cada jogo considerando só os gols até `minuto`.

    O jogo só "existe" depois do apito inicial: antes do minuto 1 nenhum placar
    aparece — igual ao Brasfoot, em que a rodada começa zerada.
    """
    resultado: dict[str, list[tuple[Partida, int, int]]] = {}
    for rotulo, partidas in placares.items():
        linhas = [(p, *p.placar_ate(minuto)) for p in partidas if p.jogada]
        if linhas:
            resultado[rotulo] = linhas
    return resultado


def gols_do_minuto(placares: dict[str, list[Partida]], minuto: int) -> list[Gol]:
    """Gols marcados exatamente no minuto atual (para destacar na tela)."""
    return [
        gol
        for partidas in placares.values()
        for partida in partidas
        for gol in partida.gols
        if gol.minuto == minuto
    ]


def gols_entre(placares: dict[str, list[Partida]], inicio: int, fim: int) -> list[Gol]:
    """Gols marcados no intervalo `(inicio, fim]` — um "quadro" da animação."""
    return [
        gol
        for partidas in placares.values()
        for partida in partidas
        for gol in partida.gols
        if inicio < gol.minuto <= fim
    ]


def gol_recente(partida: Partida, minuto: int, janela: int = JANELA_FLASH) -> bool:
    """True se a partida marcou gol nos últimos `janela` minutos de jogo.

    A janela é inclusiva (`minuto - janela <= gol <= minuto`) para o lance ficar
    aceso também no quadro seguinte ao gol.
    """
    return any(minuto - janela <= gol.minuto <= minuto for gol in partida.gols)


def tem_gol_recente(
    placares: dict[str, list[Partida]], minuto: int, janela: int = JANELA_FLASH
) -> bool:
    """True se algum jogo da rodada marcou gol agora (liga o pisca do painel)."""
    return any(
        gol_recente(partida, minuto, janela)
        for partidas in placares.values()
        for partida in partidas
    )


def ultimo_gol(partida: Partida, minuto: int) -> Gol | None:
    """Gol mais recente da partida até o minuto (None se ainda não teve)."""
    gols = partida.gols_ate(minuto)
    return gols[-1] if gols else None


def total_de_jogos(placares: dict[str, list[Partida]]) -> int:
    return sum(len(partidas) for partidas in placares.values())


def linha_placar(
    partida: Partida,
    casa: int,
    fora: int,
    destaque: bool = False,
    gol: bool = False,
) -> str:
    """Uma linha de placar parcial (reaproveita o CSS `.placar-linha`)."""
    classes = ["placar-linha"]
    if destaque:
        classes.append("destaque")
    if gol:
        classes.append("gol-agora")
    classe = " ".join(classes)
    return (
        f"<div class='{classe}'>"
        f"<span class='pc-time'>{partida.time_casa}</span>"
        f"<span class='pc-score'>{casa}<i>x</i>{fora}</span>"
        f"<span class='pc-time right'>{partida.time_fora}</span>"
        "</div>"
    )


def html_ao_vivo(
    placares: dict[str, list[Partida]],
    minuto: int,
    *,
    meu_time: str = "",
    rodada: int = 0,
    sorteio: int | None = None,
    final: int | None = None,
    som: str = "",
) -> str:
    """Painel da rodada em andamento: relógio, jogo do clube e demais jogos.

    `som` é o data URI do WAV de gol: quando vem preenchido (o chamador só
    preenche no quadro em que saiu gol), o painel toca o som e pisca em vermelho.
    """
    final = minuto_final(placares) if final is None else final
    piscando = tem_gol_recente(placares, minuto)
    chip = f"<span class='av-chip'>🎲 Sorteio #{sorteio:06x}</span>" if sorteio else ""
    kicker = f"Rodada {rodada} · {total_de_jogos(placares)} jogos" if rodada else ""
    bipe = caixa_de_som(som, minuto)
    partes = [
        bipe,
        f"<div class='ao-vivo{' gol-agora' if piscando else ''}'>",
        "<div class='av-topo'>",
        f"<span class='av-relogio'>{relogio(minuto)}</span>",
        f"<span class='av-legenda'>{kicker}</span>",
        "<span class='av-fim'></span>",
        chip,
        "</div>",
    ]

    destaque = _jogo_do_clube(placares, meu_time, minuto)
    blocos = _blocos(placares, minuto, meu_time)
    corpo = ([destaque] if destaque else []) + blocos
    if corpo:
        partes.append(f"<div class='av-corpo'>{''.join(corpo)}</div>")
    partes.append("</div>")
    return "".join(partes)


def _jogo_do_clube(
    placares: dict[str, list[Partida]], meu_time: str, minuto: int
) -> str:
    """Cartão grande do jogo do clube do jogador (se ele joga nesta rodada)."""
    if not meu_time:
        return ""
    for partidas in placares.values():
        for partida in partidas:
            if meu_time not in (partida.time_casa, partida.time_fora):
                continue
            casa, fora = partida.placar_ate(minuto)
            gol = ultimo_gol(partida, minuto)
            agora = gol_recente(partida, minuto)
            evento = (
                f"⚽ {gol.minuto}' {gol.jogador}"
                + (f" (assist: {gol.assistencia})" if gol.assistencia else "")
                if gol
                else "⏳ Bola rolando..."
            )
            if agora:
                evento = f"⚽ <b>GOOOL!</b> {evento}"
            return (
                f"<div class='av-destaque{' gol-agora' if agora else ''}'>"
                f"<div class='av-placar'>{casa}<i>x</i>{fora}</div>"
                f"<div class='av-times'>{partida.time_casa} · {partida.time_fora}</div>"
                f"<div class='av-evento'>{evento}</div>"
                "</div>"
            )
    return ""


def _blocos(
    placares: dict[str, list[Partida]], minuto: int, meu_time: str
) -> list[str]:
    """Blocos por competição com os demais jogos da rodada."""
    blocos: list[str] = []
    for rotulo, partidas in placares.items():
        linhas = []
        for partida in partidas:
            if meu_time and meu_time in (partida.time_casa, partida.time_fora):
                continue
            casa, fora = partida.placar_ate(minuto)
            linhas.append(
                linha_placar(partida, casa, fora, gol=gol_recente(partida, minuto))
            )
        if linhas:
            blocos.append(
                f"<div class='placar-bloco'><h4>{rotulo}"
                f"<span>{len(linhas)} jogos</span></h4>{''.join(linhas)}</div>"
            )
    if not blocos:
        return []
    return [f"<div class='av-lista'>{''.join(blocos)}</div>"]
