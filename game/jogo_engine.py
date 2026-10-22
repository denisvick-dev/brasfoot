"""
Motor de simulação de partidas.

Modelo de simulação
-------------------
Cada minuto pode gerar um evento. Quando o evento é uma "chance", a
conversão em gol não é fixa: depende do confronto entre a força de ataque
de quem ataca e a força de defesa de quem defende, com bônus de mando de
campo, moral, energia e tática. Isso faz o overall do elenco realmente
decidir o campeonato (antes a força só sorteava quem atacava e o gol era
uma probabilidade constante).

Os números abaixo foram calibrados para chegar perto do Brasileirão real:
~2,4 gols/jogo, ~45% de vitórias do mandante e ~26% de empates.
"""

import random

from game.modelos import Partida, Time


class MatchEngine:
    """Simula uma partida de futebol."""

    # ---- parâmetros de simulação (tunáveis) -------------------------
    CHANCE_EVENTO = 0.12          # prob. de evento por minuto (~11 por jogo)
    CHANCE_EVENTO_ACRESCIMO = 0.16
    PESOS_EVENTO = {              # chance = finalização (pode virar gol)
        "chance": 58,
        "cartao": 8,
        "falta": 14,
        "escanteio": 20,
    }
    CONVERSAO = 0.74              # × ataque/(ataque+defesa) => ~0,37 se equilibrado
    PROB_GOL_MIN = 0.05
    PROB_GOL_MAX = 0.85

    BONUS_CASA_ATAQUE = 11.0
    BONUS_CASA_DEFESA = 5.0
    BONUS_CASA_GERAL = 11.0   # usado na força geral (posse/volume de jogo)
    PESO_TATICA_ATAQUE = 0.22     # (tatica - 50) * peso
    PESO_TATICA_DEFESA = 0.18     # atacar mais = defender pior

    DESGASTE_MIN, DESGASTE_MAX = 20, 35
    RECUPERACAO_MIN, RECUPERACAO_MAX = 12, 26
    PROB_LESAO = 0.03

    INGRESSO_MIN, INGRESSO_MAX = 40, 90
    COTA_TV_POR_TORCEDOR = 12_000  # renda fixa do mandante por jogo
    RODADAS_POR_MES = 6            # salários pagos a cada 6 rodadas

    def simular(
        self,
        time_casa: Time,
        time_fora: Time,
        rodada: int,
        is_player_home: bool = False,
        is_player_away: bool = False,
    ) -> Partida:
        """Simula uma partida completa."""

        partida = Partida(
            rodada=rodada,
            time_casa=time_casa.nome,
            time_fora=time_fora.nome,
            publico=self._calcular_publico(time_casa),
        )

        # Forças dos times
        forca_casa = self._calcular_forca(time_casa, casa=True)
        forca_fora = self._calcular_forca(time_fora, casa=False)

        # Simular minuto a minuto (simplificado em blocos)
        for minuto in range(1, 91):
            # Chance de evento a cada minuto
            if random.random() < self.CHANCE_EVENTO:
                evento = self._gerar_evento(
                    minuto, time_casa, time_fora, forca_casa, forca_fora, partida
                )
                if evento:
                    partida.eventos.append(evento)

        # Acréscimos
        acrescimos = random.randint(1, 5)
        for minuto in range(90, 90 + acrescimos + 1):
            if random.random() < self.CHANCE_EVENTO_ACRESCIMO:
                evento = self._gerar_evento(
                    minuto, time_casa, time_fora, forca_casa, forca_fora, partida
                )
                if evento:
                    partida.eventos.append(evento)

        partida.jogada = True

        # Atualizar estatísticas dos times
        self._atualizar_stats(time_casa, time_fora, partida)

        # Desgastar jogadores
        self._desgastar_jogadores(time_casa)
        self._desgastar_jogadores(time_fora)

        return partida

    # ---- forças ------------------------------------------------------
    def _calcular_forca(self, time: Time, casa: bool) -> float:
        """Força geral: define quem tem mais a bola (posse/volume de jogo)."""
        base = time.overall_time

        # Bônus mandante
        if casa:
            base += self.BONUS_CASA_GERAL

        # Fator moral
        moral_factor = time.moral_time / 100
        base = base * (0.8 + 0.4 * moral_factor)

        # Fator energia média
        titulares = time.titulares
        if titulares:
            energia_media = sum(j.energia for j in titulares) / len(titulares)
            base = base * (0.7 + 0.3 * (energia_media / 100))

        # Tática
        base += (time.tatica_ofensiva - 50) * 0.05

        return max(1.0, base)

    def _fator_estado(self, time: Time) -> float:
        """Multiplicador de moral + energia do time."""
        moral = 0.85 + 0.30 * (time.moral_time / 100)  # 0,85 a 1,15
        titulares = time.titulares
        if titulares:
            energia_media = sum(j.energia for j in titulares) / len(titulares)
        else:
            energia_media = 100
        energia = 0.70 + 0.30 * (energia_media / 100)  # 0,70 a 1,00
        return moral * energia

    def _forca_ataque(self, time: Time, casa: bool) -> float:
        f = time.forca_ataque * self._fator_estado(time)
        f += (time.tatica_ofensiva - 50) * self.PESO_TATICA_ATAQUE
        if casa:
            f += self.BONUS_CASA_ATAQUE
        return max(1.0, f)

    def _forca_defesa(self, time: Time, casa: bool) -> float:
        f = time.forca_defesa * self._fator_estado(time)
        f -= (time.tatica_ofensiva - 50) * self.PESO_TATICA_DEFESA
        if casa:
            f += self.BONUS_CASA_DEFESA
        return max(1.0, f)

    # ---- eventos -----------------------------------------------------
    def _gerar_evento(
        self,
        minuto: int,
        time_casa: Time,
        time_fora: Time,
        forca_casa: float,
        forca_fora: float,
        partida: Partida,
    ) -> str | None:
        """Gera um evento aleatório durante a partida."""
        total = forca_casa + forca_fora
        prob_casa = forca_casa / total if total > 0 else 0.5

        # Decidir qual time ataca
        atacando_casa = random.random() < prob_casa

        if atacando_casa:
            time_atk = time_casa
            time_def = time_fora
        else:
            time_atk = time_fora
            time_def = time_casa

        tipos = list(self.PESOS_EVENTO)
        pesos = [self.PESOS_EVENTO[t] for t in tipos]
        tipo = random.choices(tipos, weights=pesos, k=1)[0]

        if tipo == "chance":
            return self._evento_chance(
                minuto, time_atk, time_def, partida, casa_ataca=atacando_casa
            )
        elif tipo == "cartao":
            jogadores = time_atk.titulares
            if jogadores:
                jogador = random.choice(jogadores)
                if random.random() < 0.85:
                    jogador.cartoes_amarelos += 1
                    if jogador.cartoes_amarelos >= 3:
                        jogador.suspenso = True
                    return f"🟨 {minuto}' - Cartão amarelo para {jogador.nome} ({time_atk.sigla})"
                else:
                    jogador.cartoes_vermelhos += 1
                    jogador.suspenso = True
                    return f"🟥 {minuto}' - Cartão vermelho! {jogador.nome} ({time_atk.sigla}) expulso!"
        elif tipo == "falta":
            return f"⚠️ {minuto}' - Falta perigosa para {time_atk.sigla}"
        elif tipo == "escanteio":
            return f"🚩 {minuto}' - Escanteio para {time_atk.sigla}"

        return None

    def _evento_chance(
        self,
        minuto: int,
        time_atk: Time,
        time_def: Time,
        partida: Partida,
        casa_ataca: bool,
    ) -> str | None:
        """Uma chance de gol: converte (ou não) conforme ataque x defesa."""
        atk = self._forca_ataque(time_atk, casa=casa_ataca)
        dfs = self._forca_defesa(time_def, casa=not casa_ataca)

        x = atk / (atk + dfs) if (atk + dfs) > 0 else 0.5
        prob_gol = min(self.PROB_GOL_MAX, max(self.PROB_GOL_MIN, self.CONVERSAO * x))

        if random.random() < prob_gol:
            return self._evento_gol(minuto, time_atk, partida)

        # Não converteu: defesa do goleiro ou chance perdida
        goleiros = [j for j in time_def.titulares if j.posicao == "GOL"]
        if goleiros and random.random() < 0.5:
            goleiro = goleiros[0]
            return f"🧤 {minuto}' - Grande defesa de {goleiro.nome} ({time_def.sigla})!"

        atacantes = [
            j for j in time_atk.titulares if j.posicao in ("ATA", "MEI", "LAT")
        ]
        if atacantes:
            jogador = random.choice(atacantes)
            opcoes = [
                f"⚽❌ {minuto}' - {jogador.nome} ({time_atk.sigla}) chuta para fora!",
                f"⚽❌ {minuto}' - {jogador.nome} ({time_atk.sigla}) acerta a trave!",
                f"⚽❌ {minuto}' - {jogador.nome} ({time_atk.sigla}) perde gol incrível!",
            ]
            return random.choice(opcoes)

        return None

    def _evento_gol(
        self, minuto: int, time_atk: Time, partida: Partida
    ) -> str | None:
        """Processa um evento de gol."""
        # Chance real de gol baseada na força
        atacantes = [
            j for j in time_atk.titulares if j.posicao in ("ATA", "MEI", "VOL")
        ]
        meias = [j for j in time_atk.titulares if j.posicao in ("MEI", "LAT", "ATA")]

        if not atacantes:
            atacantes = time_atk.titulares
        if not atacantes:
            return None

        # Peso pela finalização
        pesos = [max(1, j.finalizacao) for j in atacantes]
        goleador = random.choices(atacantes, weights=pesos, k=1)[0]
        goleador.gols += 1
        # (jogos contados em _atualizar_stats, para não duplicar)

        # Assistência
        assist_str = ""
        if meias and random.random() < 0.65:
            assistente = random.choice([m for m in meias if m != goleador] or meias)
            assistente.assistencias += 1
            assist_str = f" (assist: {assistente.nome})"

        if time_atk.nome == partida.time_casa:
            partida.gols_casa += 1
        else:
            partida.gols_fora += 1

        return (
            f"⚽🎉 {minuto}' - GOOOL! {goleador.nome} ({time_atk.sigla})!{assist_str}"
        )

    # ---- apoio -------------------------------------------------------
    def _calcular_publico(self, time_casa: Time) -> int:
        """Calcula o público do jogo, respeitando a capacidade do estádio."""
        base = time_casa.torcida * 500 * random.uniform(0.6, 1.15)

        if time_casa.capacidade > 0:
            teto = time_casa.capacidade * random.uniform(0.55, 1.0)
            base = min(base, teto)

        return max(200, int(base))

    def _atualizar_stats(self, time_casa: Time, time_fora: Time, partida: Partida):
        """Atualiza as estatísticas dos times após a partida."""
        time_casa.jogos_campeonato += 1
        time_fora.jogos_campeonato += 1

        time_casa.gols_pro += partida.gols_casa
        time_casa.gols_contra += partida.gols_fora
        time_fora.gols_pro += partida.gols_fora
        time_fora.gols_contra += partida.gols_casa

        if partida.gols_casa > partida.gols_fora:
            time_casa.pontos += 3
            time_casa.vitorias += 1
            time_fora.derrotas += 1
            time_casa.moral_time = min(100, time_casa.moral_time + 5)
            time_fora.moral_time = max(20, time_fora.moral_time - 5)
        elif partida.gols_casa < partida.gols_fora:
            time_fora.pontos += 3
            time_fora.vitorias += 1
            time_casa.derrotas += 1
            time_fora.moral_time = min(100, time_fora.moral_time + 5)
            time_casa.moral_time = max(20, time_casa.moral_time - 5)
        else:
            time_casa.pontos += 1
            time_fora.pontos += 1
            time_casa.empates += 1
            time_fora.empates += 1

        # Renda: bilheteria + cota de TV (quem joga em casa recebe)
        bilheteria = partida.publico * random.randint(
            self.INGRESSO_MIN, self.INGRESSO_MAX
        )
        cota_tv = time_casa.torcida * self.COTA_TV_POR_TORCEDOR
        time_casa.financas += bilheteria + cota_tv

        # Jogos dos titulares
        for j in time_casa.titulares + time_fora.titulares:
            j.jogos += 1

    def _desgastar_jogadores(self, time: Time):
        """Desgasta os jogadores após o jogo."""
        for j in time.titulares:
            desgaste = random.randint(self.DESGASTE_MIN, self.DESGASTE_MAX)
            j.desgastar(desgaste)

            # Chance de lesão
            if random.random() < self.PROB_LESAO:
                j.lesionado = True
                j.energia = 0
