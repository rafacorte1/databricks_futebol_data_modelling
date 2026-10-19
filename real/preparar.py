"""Normaliza o snapshot histórico; --atualizar baixa nova cópia da fonte."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
URL = 'https://raw.githubusercontent.com/williamorim/brasileirao/main/data-raw/csv/matches.csv'

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--atualizar', action='store_true')
    args = parser.parse_args()
    raw = ROOT/'brutos/matches.csv'
    if args.atualizar:
        with urlopen(URL, timeout=60) as response:
            payload = response.read()
    else:
        payload = raw.read_bytes()
    rows = [r for r in csv.DictReader(io.StringIO(payload.decode('utf-8-sig')))
            if r['season'] in {str(y) for y in range(2021, 2026)}]
    names = sorted({r[k] for r in rows for k in ('home', 'away')})
    ids = {name: f'R{i:03}' for i, name in enumerate(names, 1)}
    games = []
    for r in rows:
        home, away = map(int, r['score'].split('x'))
        datetime.strptime(r['date'], '%Y-%m-%d')
        games.append(dict(partida_id=f"R{r['id_match']}", id_fonte=r['id_match'],
                          temporada=int(r['season']), data=r['date'],
                          mandante_id=ids[r['home']], visitante_id=ids[r['away']],
                          gols_mandante=home, gols_visitante=away))
    for year in range(2021, 2026):
        season = [g for g in games if g['temporada'] == year]
        pairs = {(g['mandante_id'], g['visitante_id']) for g in season}
        if len(season) != 380 or len(pairs) != 380:
            raise ValueError(f'Temporada {year} incompleta ou duplicada')
    if args.atualizar:
        raw.write_bytes(payload)
    write_csv(ROOT/'dados/clubes.csv', [dict(clube_id=ids[n], nome=n) for n in names])
    write_csv(ROOT/'dados/partidas.csv', games)
    write_csv(ROOT/'dados/participacoes.csv', [dict(temporada=y, clube_id=ids[n])
              for y in range(2021, 2026) for n in sorted({r[k] for r in rows
              if r['season'] == str(y) for k in ('home', 'away')})])
    manifest = dict(fonte=URL, repositorio='https://github.com/williamorim/brasileirao',
                    processado_em_utc=datetime.now(timezone.utc).isoformat(),
                    sha256_bruto=hashlib.sha256(payload).hexdigest(),
                    temporadas=list(range(2021, 2026)), partidas=len(games), clubes=len(names),
                    observacao='Fonte comunitária; resultados não auditados contra súmulas oficiais.')
    (ROOT/'manifesto.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(f'Real: {len(games)} partidas, {len(names)} clubes')

if __name__ == '__main__':
    main()
