"""Efeitos sonoros do jogo, gerados em código (sem arquivo de áudio no repo).

O único som hoje é o do gol: uma torcida que explode junto com uma trompa,
sintetizada aqui mesmo com a biblioteca padrão (`wave` + `math`). Sai como
`data:` URI para entrar num `<audio autoplay>` dentro do HTML do painel ao vivo
— o Streamlit não deixa rodar JavaScript, então essa é a forma de tocar som.

Tudo é determinístico (o ruído usa `random.Random` com semente fixa), então o
mesmo WAV é gerado em qualquer máquina — o que também deixa os testes simples.
"""

import base64
import io
import math
import random
import sys
import wave
from array import array
from functools import lru_cache

#: Taxa de amostragem do WAV. 22 kHz é suficiente para torcida e trompa e
#: mantém o data URI pequeno (é embutido no HTML a cada gol).
TAXA = 22_050

#: Duração do som de gol, em segundos.
DURACAO_GOL = 1.35

#: Semente do ruído da torcida (determinístico de propósito).
SEMENTE_RUIDO = 2026

#: Prefixo do data URI.
PREFIXO_WAV = "data:audio/wav;base64,"


def _para_wav(amostras: list[float], taxa: int = TAXA) -> bytes:
    """Converte amostras em -1.0..1.0 para um WAV mono de 16 bits."""
    quadros = array(
        "h",
        (int(max(-1.0, min(1.0, a)) * 32_767) for a in amostras),
    )
    if sys.byteorder == "big":  # WAV é little-endian
        quadros.byteswap()
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as arquivo:
        arquivo.setnchannels(1)
        arquivo.setsampwidth(2)
        arquivo.setframerate(taxa)
        arquivo.writeframes(quadros.tobytes())
    return buffer.getvalue()


def _normalizar(amostras: list[float], pico: float = 0.92) -> list[float]:
    """Escala as amostras para o pico pedido (evita estouro/clipping)."""
    maior = max((abs(a) for a in amostras), default=0.0)
    if maior <= 0:
        return amostras
    fator = pico / maior
    return [a * fator for a in amostras]


def _amostras_do_gol(taxa: int = TAXA, duracao: float = DURACAO_GOL) -> list[float]:
    """Torcida explodindo + trompa de estádio, no estilo do Brasfoot."""
    total = int(taxa * duracao)
    rng = random.Random(SEMENTE_RUIDO)
    amostras: list[float] = []
    ruido = 0.0

    for i in range(total):
        t = i / taxa

        # Torcida: ruído branco filtrado (passa-baixa simples), subindo rápido
        # e caindo devagar — o "Uhhh!" que acompanha o gol.
        ruido = ruido * 0.86 + rng.uniform(-1.0, 1.0) * 0.14
        env_torcida = min(1.0, t / 0.12) * math.exp(-max(0.0, t - 0.25) * 1.9)
        torcida = ruido * env_torcida * 0.9

        # Trompa: acorde com vibrato, segurando quase até o fim.
        env_trompa = min(1.0, t / 0.05)
        if t > 0.85:
            env_trompa *= max(0.0, 1.0 - (t - 0.85) / 0.45)
        vibrato = 1.0 + 0.01 * math.sin(2.0 * math.pi * 6.5 * t)
        trompa = (
            0.55 * math.sin(2.0 * math.pi * 196.00 * vibrato * t)  # G3
            + 0.35 * math.sin(2.0 * math.pi * 293.66 * vibrato * t)  # D4
            + 0.22 * math.sin(2.0 * math.pi * 392.00 * vibrato * t)  # G4
        )
        trompa *= env_trompa * 0.32

        amostras.append(torcida + trompa)

    return _normalizar(amostras)


@lru_cache(maxsize=1)
def som_gol_wav() -> bytes:
    """WAV do gol (em bytes). Gerado uma vez por processo."""
    return _para_wav(_amostras_do_gol())


@lru_cache(maxsize=1)
def som_gol_uri() -> str:
    """O mesmo WAV como `data:audio/wav;base64,…` para usar no HTML."""
    return PREFIXO_WAV + base64.b64encode(som_gol_wav()).decode("ascii")


def caixa_de_som(uri: str, minuto: int) -> str:
    """`<audio autoplay>` escondido, com id único por minuto.

    O id muda a cada gol para o Streamlit recriar o elemento e o navegador
    tocar o som de novo (um `<audio>` igual, já tocado, não repetiria).
    """
    if not uri:
        return ""
    return (
        f"<audio id='som-gol-{minuto}' autoplay='autoplay' preload='auto' "
        "style='display:none' aria-hidden='true'>"
        f"<source src='{uri}' type='audio/wav'>"
        "</audio>"
    )
