# Dicionário de dados

Chaves indicadas como PK são únicas no arquivo. FK referencia arquivo da mesma opção.
Valores monetários são reais brasileiros (BRL). Campos são obrigatórios, exceto
`jogador_entrada_id`, presente somente nos eventos de substituição.

## Comum às duas opções

| Arquivo | Grão e campos |
|---|---|
| clubes.csv | Um clube. `clube_id` STRING PK; `nome` STRING. |
| participacoes.csv | Clube em temporada. PK composta: `temporada` INT + `clube_id` STRING FK clubes. |
| partidas.csv | Uma partida. `partida_id` STRING PK; `temporada` INT; `data` DATE; `mandante_id`, `visitante_id` STRING FK clubes; `gols_mandante`, `gols_visitante` INT não negativos. |

Cada opção tem seus próprios IDs. Use participacoes para saber quem disputou cada ano.
Não faça joins entre IDs das duas opções.

## Campos adicionais: real

- `partidas.id_fonte`: identificador original da partida no snapshot, armazenado como STRING.
- A base não fornece número da rodada; a ordem cronológica não é tratada como rodada.
- O nome de cada clube é preservado conforme a fonte.

## Campos adicionais: sintético

| Arquivo | Campos |
|---|---|
| clubes.csv | `cidade`, `uf` STRING gerados independentemente; `estadio_id` STRING FK estadios. |
| estadios.csv | `estadio_id` STRING PK; `nome` STRING; `capacidade` INT. |
| jogadores.csv | `jogador_id` STRING PK; `temporada` INT; `clube_id` STRING FK clubes; `nome` STRING; `nascimento` DATE; `posicao` STRING (goleiro, defensor, meio_campo, atacante); `salario_mensal_brl` DECIMAL(14,2). |
| partidas.csv | `rodada` INT 1–38; `estadio_id` STRING FK estadios; `publico` INT; `ingresso_medio_brl`, `receita_brl` DECIMAL(14,2); `incidente` STRING (nenhum, interdicao_parcial_simulada). |
| eventos_partida.jsonl | `evento_id` STRING PK; `partida_id` STRING FK partidas; `clube_id` STRING FK clubes; `jogador_id` STRING FK jogadores; `tipo` STRING (gol, cartao_amarelo, substituicao); `minuto` INT; `jogador_entrada_id` STRING FK jogadores somente em substituições. |

Em substituições, `jogador_id` é quem sai e `jogador_entrada_id` quem entra.
Jogadores referenciados pertencem ao clube e à temporada da partida.
Não há gols contra nesta simulação; cada gol é creditado ao clube do autor.

## Verificações executáveis

`python -m unittest discover -s tests -v` verifica em ambas as opções:
1. Cinco temporadas com 380 partidas cada e IDs únicos.
2. Vinte clubes por ano, 38 partidas por clube, um jogo por par ordenado.
3. Referências de clubes e placares não negativos.
4. Na simulação, identidade e vínculo dos jogadores dos eventos, gols iguais
   ao placar e público menor ou igual à capacidade do estádio.

O manifesto de cada opção registra contagens. O real contém também o hash do bruto.
