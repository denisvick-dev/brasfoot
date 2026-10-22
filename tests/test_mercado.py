"""Mercado de transferências."""

from game.mercado import Market


def test_mercado_tem_ofertas(times8):
    mercado = Market(times8)
    assert mercado.ofertas_disponiveis


def test_compra_sem_dinheiro_falha(times8):
    mercado = Market(times8)
    comprador = times8[0]
    comprador.financas = 1
    jogador, vendedor, preco = mercado.ofertas_disponiveis[0]
    ok, mensagem = mercado.comprar_jogador(jogador, vendedor, comprador, preco)
    assert not ok
    assert "insuficiente" in mensagem.lower()


def test_compra_move_jogador_e_debita(times8):
    mercado = Market(times8)
    jogador, vendedor, preco = mercado.ofertas_disponiveis[0]
    comprador = next(t for t in times8 if t is not vendedor)
    comprador.financas = 10_000_000_000
    saldo = comprador.financas
    ok, _ = mercado.comprar_jogador(jogador, vendedor, comprador, preco)
    assert ok
    assert jogador in comprador.jogadores
    assert jogador not in vendedor.jogadores
    assert comprador.financas == saldo - preco


def test_elenco_lotado_bloqueia_compra(times8):
    mercado = Market(times8)
    comprador = times8[0]
    comprador.financas = 10_000_000_000
    comprador.jogadores = comprador.jogadores * 3
    jogador, vendedor, preco = mercado.ofertas_disponiveis[0]
    ok, mensagem = mercado.comprar_jogador(jogador, vendedor, comprador, preco)
    assert not ok
    assert "lotado" in mensagem.lower()
