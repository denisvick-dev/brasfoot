# Finanças, rotina e diretoria

## Caixa e extrato

Todo dinheiro que entra ou sai do clube passa por `game/financas.registrar()`,
que atualiza `Time.financas` e grava uma linha no extrato do clube:

```python
{
    "rodada": 12,
    "tipo": "bilheteria",
    "descricao": "Bilheteria x Vasco (31.204 pagantes)",
    "valor": 1_972_000,
}
```

O extrato guarda os últimos 400 lançamentos (`financas.LIMITE_EXTRATO`) e é uma
lista de dicionários de propósito: vai e volta do JSON em
`game/persistencia.py` sem conversão especial.

Tipos de lançamento: `bilheteria`, `tv`, `patrocinio`, `salarios`,
`transferencia`, `premiacao`, `estadio` e `outros`.

## De onde vem e para onde vai o dinheiro

| Lançamento | Quando acontece | Valor |
| --- | --- | --- |
| Bilheteria | cada jogo em casa, no motor | público × ingresso (R$ 40–90) |
| Cota de TV do jogo | cada jogo em casa, no motor | torcida × R$ 12.000 |
| Cota de TV da rodada | toda rodada, para todos | Série A 450 mil · B 260 mil · C 190 mil · D 120 mil |
| Patrocínio | a cada 6 rodadas | A 3 mi · B 900 mil · C 350 mil · D 120 mil |
| Folha salarial | a cada 6 rodadas | soma dos salários do elenco |
| Transferências | compra (despesa) e venda (receita) | preço negociado |
| Premiação | fim da temporada | posição na divisão + copa + supercopa |

A cota de TV por rodada existe para o clube pequeno não fechar a temporada no
vermelho: na Série D, a bilheteria e a cota por jogo em casa não pagam a folha.
Com os valores atuais, uma temporada completa de 156 clubes termina sem nenhum
clube no negativo (mediana em torno de R$ 3 mi; Série A entre R$ 90 e 100 mi,
Série D entre R$ 2 e 3 mi).

Valores em constantes no topo de `game/rotina.py` (`COTA_TV_RODADA`,
`PATROCINIO_MES`) e em `game/financas.py` (`_PREMIOS`, `_PREMIO_MINIMO`).

## Rotina entre rodadas

`game/rotina.py` roda ao fim de **toda** rodada — tanto na temporada completa
(`Piramide`) quanto no campeonato avulso (`League`):

1. **Energia**: recupera de 12 a 26 pontos por jogador.
2. **Lesão**: 22% de chance de cura por rodada (volta com 60 de energia).
3. **Suspensão**: desconta um jogo; ao zerar, o jogador volta e o contador de
   amarelos é limpo. O motor grava `jogos_suspenso = 2` no cartão, então o
   jogador desfalca exatamente o jogo seguinte.
4. **Renda fixa**: cota de TV da rodada e, a cada 6 rodadas, patrocínio.
5. **Folha salarial**: paga a cada 6 rodadas.
6. **Escalação automática** dos clubes da CPU, já considerando energia.

Antes essa rotina existia só dentro de `League`; na pirâmide (jogo principal) a
energia nunca voltava, as lesões não saravam e os salários não eram cobrados.

## Objetivo da diretoria

`game/diretoria.py` define a meta de cada série, no estilo Brasfoot:

| Série | Meta |
| --- | --- |
| A | terminar entre os 6 primeiros |
| B | subir para a Série A (top 4) |
| C | subir para a Série B (top 4) |
| D | terminar entre os 8 primeiros da chave |

A situação (`Meta encaminhada`, `Em risco`, `Abaixo do esperado`) aparece no
painel e na tela de finanças, com cor própria.

## Tela de finanças

`ui/financas.py`, no menu lateral em **💰 Finanças**:

- caixa, folha salarial, receitas e saldo do ano;
- alerta quando o caixa fica negativo;
- objetivo da diretoria com a posição atual;
- resumo por tipo de lançamento;
- extrato com os 25 lançamentos mais recentes.
