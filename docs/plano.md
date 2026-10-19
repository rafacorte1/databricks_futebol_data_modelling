# Plano aprovado: duas opções de dataset

Destino: pasta local indicada pelo usuário. Temporadas completas: 2021–2025.
1. Preservar CSV histórico original; filtrar por season, nunca pelo ano da data.
2. Normalizar partidas e clubes reais, mantendo identificador original e procedência.
3. Gerar Faker pt_BR com seed 42: 20 clubes fictícios fixos, 20 estádios,
   600 jogadores por temporada, calendário de turno e returno, eventos e receitas.
4. Validar 380 partidas/ano, 20 clubes/ano, 38 jogos/clube, confrontos únicos,
   chaves estrangeiras, capacidade dos estádios e gols dos eventos.
5. Documentar reprodução, dicionário, limitações e uso futuro no Databricks.

Geração local autorizada. Nenhum recurso Databricks será criado nesta etapa.
