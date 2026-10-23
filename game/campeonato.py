"""
Gerenciamento do campeonato (Brasileirão).
"""

import random
from collections.abc import Callable

from game import rotina
from game.jogo_engine import MatchEngine
from game.modelos import Jogador, Noticia, Partida, Time


class League:
    """Gerencia o campeonato."""

    def __init__(self, times: list[Time]):
        if len(times) < 2:
            raise ValueError("É preciso de ao menos 2 times para montar o campeonato.")

        self.times = times
        self.rodada_atual = 0
        self.total_rodadas = (len(times) - 1) * 2  # Turno e returno
        self.calendario: list[list[tuple[str, str]]] = []
        self.resultados: dict[int, list[Partida]] = {}
        self.noticias: list[Noticia] = []
        self.engine = MatchEngine()
        self.temporada = 2026
        self.campeonato_encerrado = False

        self._gerar_calendario()

    def _gerar_calendario(self):
        """Gera o calendário completo do campeonato."""
        nomes = [t.nome for t in self.times]
        n = len(nomes)
        self.calendario = []

        # Algoritmo round-robin
        times_cal = nomes[:]
        if n % 2 == 1:
            times_cal.append("BYE")
            n += 1

        fixo = times_cal[0]
        rotativos = times_cal[1:]

        # Primeiro turno
        for rodada_idx in range(n - 1):
            jogos = []
            atual = [fixo] + rotativos
            for i in range(n // 2):
                casa = atual[i]
                fora = atual[n - 1 - i]
                if casa != "BYE" and fora != "BYE":
                    if rodada_idx % 2 == 0:
                        jogos.append((casa, fora))
                    else:
                        jogos.append((fora, casa))
            self.calendario.append(jogos)

            # Rotacionar
            rotativos = [rotativos[-1]] + rotativos[:-1]

        # Segundo turno (invertido)
        primeiro_turno = self.calendario[:]
        for jogos in primeiro_turno:
            jogos_invertidos = [(fora, casa) for casa, fora in jogos]
            self.calendario.append(jogos_invertidos)

        # Embaralhar ordem dos jogos em cada rodada
        for jogos in self.calendario:
            random.shuffle(jogos)

        self.total_rodadas = len(self.calendario)

    def _get_time_por_nome(self, nome: str) -> Time:
        for t in self.times:
            if t.nome == nome:
                return t
        raise ValueError(f"Time '{nome}' não encontrado!")

    def simular_rodada(
        self,
        time_jogador: str,
        progresso: Callable[[float, str], None] | None = None,
    ) -> list[Partida]:
        """Simula todos os jogos da rodada atual (avisa o progresso jogo a jogo)."""
        if self.rodada_atual >= self.total_rodadas:
            self.campeonato_encerrado = True
            return []

        jogos = self.calendario[self.rodada_atual]
        resultados = []

        total = max(1, len(jogos))
        for indice, (casa_nome, fora_nome) in enumerate(jogos, start=1):
            if progresso is not None:
                progresso(
                    indice / total,
                    f"{casa_nome} x {fora_nome}",
                )
            time_casa = self._get_time_por_nome(casa_nome)
            time_fora = self._get_time_por_nome(fora_nome)

            partida = self.engine.simular(
                time_casa,
                time_fora,
                self.rodada_atual + 1,
                is_player_home=(casa_nome == time_jogador),
                is_player_away=(fora_nome == time_jogador),
            )
            resultados.append(partida)

            # Gerar notícias
            if partida.gols_casa >= 4 or partida.gols_fora >= 4:
                goleada_time = (
                    casa_nome if partida.gols_casa > partida.gols_fora else fora_nome
                )
                self.noticias.append(
                    Noticia(
                        titulo=f"🔥 Goleada do {goleada_time}!",
                        texto=f"{partida.resultado_str} - Show na rodada {self.rodada_atual + 1}!",
                        rodada=self.rodada_atual + 1,
                        tipo="resultado",
                    )
                )

        self.resultados[self.rodada_atual + 1] = resultados
        self.rodada_atual += 1

        # Recuperar energia e tratar lesões/suspensões
        self._entre_rodadas()

        if self.rodada_atual >= self.total_rodadas:
            self.campeonato_encerrado = True
            campeao = self.classificacao[0]
            self.noticias.append(
                Noticia(
                    titulo=f"🏆 {campeao.nome} É CAMPEÃO BRASILEIRO {self.temporada}!",
                    texto=f"{campeao.nome} conquista o título com {campeao.pontos} pontos!",
                    rodada=self.rodada_atual,
                    tipo="geral",
                )
            )

        return resultados

    def _entre_rodadas(self):
        """Processa eventos entre rodadas (energia, lesões, suspensões, salários)."""
        rotina.entre_rodadas(
            self.times, self.rodada_atual, self.engine.RODADAS_POR_MES
        )

    @property
    def classificacao(self) -> list[Time]:
        """Retorna a classificação ordenada."""
        # critérios do Brasileirão: pontos, vitórias, saldo, gols pró
        return sorted(
            self.times,
            key=lambda t: (t.pontos, t.vitorias, t.saldo_gols, t.gols_pro),
            reverse=True,
        )

    def artilharia(self, top: int = 15) -> list[tuple[Jogador, str]]:
        """Retorna os artilheiros do campeonato como (jogador, sigla do time)."""
        todos_jogadores = []
        for time in self.times:
            for j in time.jogadores:
                if j.gols > 0:
                    todos_jogadores.append((j, time.sigla))

        todos_jogadores.sort(key=lambda x: x[0].gols, reverse=True)
        return todos_jogadores[:top]

    def jogo_do_jogador(self, time_jogador: str, rodada: int) -> Partida | None:
        """Retorna a partida do jogador em uma rodada."""
        if rodada in self.resultados:
            for p in self.resultados[rodada]:
                if time_jogador in (p.time_casa, p.time_fora):
                    return p
        return None

    def proximo_adversario(self, time_jogador: str) -> str:
        """Retorna o próximo adversário."""
        if self.rodada_atual >= self.total_rodadas:
            return "Campeonato encerrado"
        jogos = self.calendario[self.rodada_atual]
        for casa, fora in jogos:
            if casa == time_jogador:
                return f"vs {fora} (Casa)"
            elif fora == time_jogador:
                return f"vs {casa} (Fora)"
        return "Folga"
