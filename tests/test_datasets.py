import collections
import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

def read(kind, table):
    with (ROOT / kind / 'dados' / f'{table}.csv').open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))

class DatasetTests(unittest.TestCase):
    def test_five_complete_seasons(self):
        for kind in ['real', 'sintetico']:
            games = read(kind, 'partidas')
            self.assertEqual(collections.Counter(g['temporada'] for g in games),
                             {str(y): 380 for y in range(2021, 2026)})
            self.assertEqual(len({g['partida_id'] for g in games}), 1900)
            clubs = {c['clube_id'] for c in read(kind, 'clubes')}
            for year in range(2021, 2026):
                season = [g for g in games if g['temporada'] == str(year)]
                pairs = {(g['mandante_id'], g['visitante_id']) for g in season}
                self.assertEqual(len(pairs), 380)
                counts = collections.Counter()
                for g in season:
                    self.assertNotEqual(g['mandante_id'], g['visitante_id'])
                    self.assertTrue({g['mandante_id'], g['visitante_id']} <= clubs)
                    self.assertGreaterEqual(int(g['gols_mandante']), 0)
                    self.assertGreaterEqual(int(g['gols_visitante']), 0)
                    counts.update([g['mandante_id'], g['visitante_id']])
                self.assertEqual(len(counts), 20)
                self.assertEqual(set(counts.values()), {38})

    def test_synthetic_events_and_capacity(self):
        games = {g['partida_id']: g for g in read('sintetico', 'partidas')}
        players = {p['jogador_id']: p for p in read('sintetico', 'jogadores')}
        self.assertEqual(len(players), 3000)
        stadiums = {s['estadio_id']: s for s in read('sintetico', 'estadios')}
        goals = collections.Counter()
        with (ROOT/'sintetico/dados/eventos_partida.jsonl').open() as f:
            events = [json.loads(line) for line in f]
        self.assertEqual(len({e['evento_id'] for e in events}), len(events))
        for e in events:
            g = games[e['partida_id']]
            p = players[e['jogador_id']]
            self.assertEqual(p['temporada'], g['temporada'])
            self.assertEqual(p['clube_id'], e['clube_id'])
            self.assertIn(e['clube_id'], [g['mandante_id'], g['visitante_id']])
            if e['tipo'] == 'gol':
                goals[e['partida_id'], e['clube_id']] += 1
        for g in games.values():
            self.assertLessEqual(int(g['publico']), int(stadiums[g['estadio_id']]['capacidade']))
            for role in ['mandante', 'visitante']:
                self.assertEqual(goals[g['partida_id'], g[f'{role}_id']], int(g[f'gols_{role}']))

if __name__ == '__main__':
    unittest.main()
