"""Som de gol: WAV sintetizado em código e embutido como data URI."""

import io
import wave

from ui.sons import (
    DURACAO_GOL,
    PREFIXO_WAV,
    TAXA,
    caixa_de_som,
    som_gol_uri,
    som_gol_wav,
)


def _abrir(wav: bytes) -> wave.Wave_read:
    return wave.open(io.BytesIO(wav), "rb")


def test_wav_do_gol_e_valido():
    wav = som_gol_wav()
    assert wav[:4] == b"RIFF"
    assert wav[8:12] == b"WAVE"

    with _abrir(wav) as arquivo:
        assert arquivo.getnchannels() == 1
        assert arquivo.getsampwidth() == 2
        assert arquivo.getframerate() == TAXA
        segundos = arquivo.getnframes() / arquivo.getframerate()
        assert abs(segundos - DURACAO_GOL) < 0.05


def test_som_nao_e_silencio_e_nao_estoura():
    with _abrir(som_gol_wav()) as arquivo:
        quadros = arquivo.readframes(arquivo.getnframes())
    amostras = [
        int.from_bytes(quadros[i : i + 2], "little", signed=True)
        for i in range(0, len(quadros), 2)
    ]
    pico = max(abs(a) for a in amostras)
    assert pico > 10_000, "o som precisa ter volume audível"
    assert pico <= 32_767, "não pode estourar (clipping)"


def test_som_e_deterministico():
    assert som_gol_wav() == som_gol_wav()
    assert som_gol_uri() == som_gol_uri()


def test_uri_e_um_data_uri_de_wav():
    uri = som_gol_uri()
    assert uri.startswith(PREFIXO_WAV)
    assert len(uri) > len(PREFIXO_WAV) + 1000


def test_caixa_de_som_toca_automaticamente_e_tem_id_por_minuto():
    uri = som_gol_uri()
    caixa = caixa_de_som(uri, 37)
    assert "<audio" in caixa
    assert "autoplay" in caixa
    assert "som-gol-37" in caixa
    assert "data:audio/wav;base64," in caixa
    # id diferente no minuto seguinte: o navegador recria o elemento e toca de novo
    assert "som-gol-40" in caixa_de_som(uri, 40)


def test_sem_uri_nao_gera_audio():
    assert caixa_de_som("", 10) == ""
