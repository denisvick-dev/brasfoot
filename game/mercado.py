"""
Mercado de transferências.
"""

import random

from game import financas
from game.banco_dados import _next_id, _nome_aleatorio
from game.modelos import Jogador, Time


class Market:
    """Gerencia o mercado de transferências."""

    def __init__(self, times: list[Time]):
        self.times = times
        self.ofertas_disponiveis: list[tuple[Jogador, Time, int]] = []
        self._gerar_ofertas()

    def _gerar_ofertas(self):
        """Gera jogadores disponíveis para compra."""
        self.ofertas_disponiveis = []
        for time in self.times:
            # Cada time pode disponibilizar 1-3 jogadores
            reservas = time.reservas
            if reservas:
                qtd = random.randint(1, min(3, len(reservas)))
                disponiveis = random.sample(reservas, qtd)
                for j in disponiveis:
                    preco = int(j.valor_mercado * random.uniform(0.8, 1.5))
                    self.ofertas_disponiveis.append((j, time, preco))

    def comprar_jogador(
        self, jogador: Jogador, time_vendedor: Time, time_comprador: Time, preco: int
    ) -> tuple[bool, str]:
        """Realiza a compra de um jogador."""
        if time_comprador.financas < preco:
            return False, "❌ Dinheiro insuficiente!"

        if len(time_comprador.jogadores) >= 30:
            return False, "❌ Elenco lotado! (máximo 30 jogadores)"

        # Transferir
        financas.registrar(
            time_comprador,
            0,
            "transferencia",
            f"Contratação de {jogador.nome}",
            -preco,
        )
        financas.registrar(
            time_vendedor, 0, "transferencia", f"Venda de {jogador.nome}", preco
        )

        time_vendedor.jogadores.remove(jogador)
        jogador.titular = False
        time_comprador.jogadores.append(jogador)
        time_comprador.auto_escalar()
        time_vendedor.auto_escalar()

        # Remover da lista de ofertas
        self.ofertas_disponiveis = [
            (j, t, p) for j, t, p in self.ofertas_disponiveis if j.id != jogador.id
        ]

        return True, f"✅ {jogador.nome} contratado por R$ {preco:,.0f}!"

    def vender_jogador(self, jogador: Jogador, time_jogador: Time) -> tuple[bool, str]:
        """Vende um jogador do time do jogador."""
        if len(time_jogador.jogadores) <= 16:
            return False, "❌ Elenco muito pequeno para vender!"

        # Precisa existir um clube comprador antes de mexer no elenco
        outros = [t for t in self.times if t is not time_jogador]
        if not outros:
            return False, "❌ Não há outro clube para receber o jogador!"

        preco = int(jogador.valor_mercado * random.uniform(0.6, 1.1))
        time_jogador.jogadores.remove(jogador)

        destino = random.choice(outros)
        jogador.titular = False
        destino.jogadores.append(jogador)
        financas.registrar(
            time_jogador, 0, "transferencia", f"Venda de {jogador.nome}", preco
        )
        financas.registrar(
            destino, 0, "transferencia", f"Contratação de {jogador.nome}", -preco
        )
        destino.auto_escalar()
        time_jogador.auto_escalar()

        return (
            True,
            f"✅ {jogador.nome} vendido para {destino.nome} por R$ {preco:,.0f}!",
        )

    def atualizar_mercado(self):
        """Atualiza ofertas do mercado."""
        self._gerar_ofertas()

    def gerar_jogador_livre(self) -> Jogador:
        """Gera um jogador livre no mercado (sem time)."""
        posicoes = ["GOL", "ZAG", "LAT", "VOL", "MEI", "ATA"]
        posicao = random.choice(posicoes)
        idade = random.randint(18, 34)
        base = random.randint(35, 70)
        v = 12

        j = Jogador(
            id=_next_id(),
            nome=_nome_aleatorio(),
            posicao=posicao,
            idade=idade,
            habilidade=max(1, min(99, base + random.randint(-v, v))),
            velocidade=max(1, min(99, base + random.randint(-v, v))),
            finalizacao=max(1, min(99, base + random.randint(-v, v))),
            passe=max(1, min(99, base + random.randint(-v, v))),
            defesa=max(1, min(99, base + random.randint(-v, v))),
            fisico=max(1, min(99, base + random.randint(-v, v))),
        )
        return j
