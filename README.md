# Brasileirão: datasets para estudos de engenharia de dados

Duas opções independentes para as temporadas completas **2021 a 2025** da Série A.
Os dados já estão criados e podem ser utilizados sem executar os scripts.

| Pasta | Natureza | Partidas | Outros dados |
|---|---|---:|---|
| `sintetico/dados/` | Faker pt_BR, seed 42 | 1.900 | 20 clubes, 20 estádios, 3.000 jogadores por temporada e 17.073 eventos |
| `real/dados/` | Resultados históricos de fonte pública comunitária | 1.900 | 29 clubes distintos e 100 participações clube/temporada |

Os 3.000 registros sintéticos de jogadores representam **600 em cada uma das cinco temporadas**, com identificadores próprios. Não representam 3.000 atletas por ano.

## Reproduzir

Python 3.10 ou superior. Execução verificada localmente com Python 3.14.

```bash
cd /Users/rafaelcorte/Documents/databricks_futebol
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python sintetico/gerar.py
python real/preparar.py
python -m unittest discover -s tests -v
```

Os scripts sobrescrevem apenas os respectivos arquivos gerados. A geração sintética é
reproduzível com a mesma versão de Python e Faker; a normalização real usa o snapshot
local e não precisa de rede. Para baixar nova versão explicitamente:

```bash
python real/preparar.py --atualizar
```

Os IDs de clubes reais são atribuídos por ordem alfabética dentro deste recorte;
revise mudanças de nomes antes de usar uma atualização em cargas incrementais.
O manifesto registra URL, SHA-256 do bruto e horário do processamento, não o horário
em que cada resultado foi publicado. O snapshot integral inclui anos fora do recorte;
use `real/dados/` para trabalhar somente com 2021–2025.

## Fonte histórica

- Projeto: https://github.com/williamorim/brasileirao
- CSV: https://raw.githubusercontent.com/williamorim/brasileirao/main/data-raw/csv/matches.csv
- Acesso inicial: 19/10/2026.
- O projeto atribui os dados de 2020–2025 ao globoesporte.globo.com.
- Licença publicada pela fonte preservada em `real/LICENCA_FONTE.md`.

Trata-se de uma compilação comunitária, sem auditoria contra súmulas oficiais da CBF.
Validamos estrutura e completude (380 jogos/ano); isso não comprova cada placar.
Não há nessa fonte jogadores, estádios, público, receita, rodadas ou eventos.
Esses campos não foram inventados no dataset real. A filtragem usa **temporada**,
não o ano civil da data, evitando misturar campeonatos com jogos adiados.

## Hipóteses da simulação

Todos os clubes, atletas, estádios, datas e resultados são fictícios. Os anos 2021–2025
são rótulos de temporadas simuladas, não uma reconstrução dos campeonatos reais.
Os mesmos 20 clubes participam dos cinco anos; não há acesso/rebaixamento ou transferências.
Datas seguem calendário simplificado a cada seis dias. Não se simula a pandemia de 2021.
Cidade e UF são valores Faker independentes e não constituem geografia oficial.
Os elencos são renovados por temporada. Eventos não modelam escalações completas,
acréscimos, segundo amarelo ou regras de elegibilidade em campo.

Gols usam distribuição de Poisson com forças diferentes por clube e vantagem do
mandante; salários usam distribuição lognormal. A ocupação varia e há uma
**interdição parcial simulada** para quatro clubes nas rodadas 15–19 de cada ano,
reduzindo a demanda e a receita. O preço cresce 6% por temporada.
A receita é simplificada: público multiplicado pelo ingresso médio, sem despesas.

## Estudar no Databricks

Arquivos CSV usam UTF-8, vírgula, cabeçalho, datas ISO `yyyy-MM-dd` e ponto decimal.
Eventos usam JSON Lines (um objeto por linha). Não há dependência de Spark para gerar
esta amostra local, que tem menos de 30 mil registros no total.

1. Defina seu workspace, catálogo e schema quando iniciar a etapa no Databricks.
2. Envie os arquivos para um Volume autorizado e preserve os brutos na camada Bronze.
3. Na Silver, aplique tipos explícitos e valide as chaves descritas no dicionário.
4. Na Gold, calcule classificação por temporada, gols e desempenho em casa/fora.
5. Com a base sintética, analise ocupação e receita antes/durante/depois da interdição.

Para dinheiro, use `DECIMAL(14,2)` ao tipar no Spark. Use `DATE` para datas,
`INT` para temporada, rodada, gols e público, e `STRING` para identificadores.
Mantenha a origem (`real` ou `sintetico`) nas futuras tabelas para impedir mistura.
Nenhum perfil Databricks foi selecionado e nenhum recurso remoto foi criado.

[Dicionário de dados](docs/dicionario.md) · [Plano](docs/plano.md)

Repositório remoto configurado: https://github.com/rafacorte1/databricks_futebol_data_modelling
O repositório reúne datasets, scripts de reprodução, testes e documentação.
