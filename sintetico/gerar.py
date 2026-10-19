"""Gera cinco temporadas inteiramente fictícias, reproduzíveis com Faker pt_BR."""
import csv
from datetime import date, timedelta
import json
import math
from pathlib import Path
import random
from faker import Faker

ROOT = Path(__file__).resolve().parent
SEED = 42

def write_csv(name, rows):
    with (ROOT/'dados'/f'{name}.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def poisson(rng, mean):
    threshold, product, k = math.exp(-mean), 1.0, 0
    while product > threshold:
        k += 1
        product *= rng.random()
    return k - 1

def main():
    rng = random.Random(SEED)
    fake = Faker('pt_BR')
    fake.seed_instance(SEED)
    (ROOT/'dados').mkdir(exist_ok=True)
    clubs, stadiums, players, games, events, memberships = [], [], [], [], [], []
    strengths = {}
    for i in range(1, 21):
        cid, sid = f'S{i:03}', f'E{i:03}'
        clubs.append(dict(clube_id=cid, nome=f'FC {fake.city()} {i:02}', cidade=fake.city(),
                          uf=fake.state_abbr(), estadio_id=sid))
        stadiums.append(dict(estadio_id=sid, nome=f'Arena {fake.last_name()} {i:02}',
                            capacidade=rng.randrange(18000, 65001, 1000)))
        strengths[cid] = rng.lognormvariate(0, 0.22)
    positions = ['goleiro']*3 + ['defensor']*10 + ['meio_campo']*10 + ['atacante']*7
    for year in range(2021, 2026):
        squads = {}
        for club in clubs:
            cid = club['clube_id']
            memberships.append(dict(temporada=year, clube_id=cid))
            squads[cid] = []
            for number, position in enumerate(positions, 1):
                pid = f'J{year}{cid}{number:02}'
                squads[cid].append(pid)
                players.append(dict(jogador_id=pid, temporada=year, clube_id=cid,
                                    nome=fake.name_male(), nascimento=fake.date_between(
                                        start_date=date(year-37, 1, 1), end_date=date(year-18, 1, 1)).isoformat(),
                                    posicao=position, salario_mensal_brl=round(rng.lognormvariate(10.4, 0.8), 2)))
        rotation = list(range(20))
        first_leg = []
        for rd in range(19):
            pairs = [(rotation[i], rotation[-1-i]) for i in range(10)]
            if rd % 2:
                pairs = [(a, h) for h, a in pairs]
            first_leg.append(pairs)
            rotation = [rotation[0], rotation[-1], *rotation[1:-1]]
        for rd in range(38):
            pairs = first_leg[rd % 19]
            if rd >= 19:
                pairs = [(a, h) for h, a in pairs]
            for h, a in pairs:
                home, away = clubs[h]['clube_id'], clubs[a]['clube_id']
                gh = poisson(rng, 1.4*strengths[home]/strengths[away])
                ga = poisson(rng, 1.05*strengths[away]/strengths[home])
                pid = f'S{year}{rd+1:02}{h+1:02}'
                incident = 15 <= rd+1 <= 19 and h < 4
                demand = min(0.98, rng.betavariate(5, 3) * (0.45 if incident else 1))
                capacity = stadiums[h]['capacidade']
                public = int(capacity*demand)
                price = round(45*(1.06**(year-2021))*strengths[home], 2)
                games.append(dict(partida_id=pid, temporada=year, rodada=rd+1,
                                  data=(date(year, 4, 10)+timedelta(days=rd*6)).isoformat(),
                                  mandante_id=home, visitante_id=away, estadio_id=clubs[h]['estadio_id'],
                                  gols_mandante=gh, gols_visitante=ga, publico=public,
                                  ingresso_medio_brl=price, receita_brl=round(public*price, 2),
                                  incidente='interdicao_parcial_simulada' if incident else 'nenhum'))
                match_events = []
                for cid, goals in [(home, gh), (away, ga)]:
                    for _ in range(goals):
                        match_events.append(dict(partida_id=pid, clube_id=cid,
                            jogador_id=rng.choice(squads[cid][3:]), tipo='gol', minuto=rng.randint(1, 90)))
                    for _ in range(poisson(rng, 2.2)):
                        match_events.append(dict(partida_id=pid, clube_id=cid,
                            jogador_id=rng.choice(squads[cid]), tipo='cartao_amarelo', minuto=rng.randint(1, 90)))
                    # Uma substituição por clube: saída e entrada são jogadores distintos.
                    out, incoming = rng.sample(squads[cid][3:], 2)
                    match_events.append(dict(partida_id=pid, clube_id=cid, jogador_id=out,
                        jogador_entrada_id=incoming, tipo='substituicao', minuto=rng.randint(46, 85)))
                for event in sorted(match_events, key=lambda e: e['minuto']):
                    events.append(dict(evento_id=f'EV{len(events)+1:07}', **event))
    for name, rows in [('clubes', clubs), ('estadios', stadiums), ('jogadores', players),
                       ('partidas', games), ('participacoes', memberships)]:
        write_csv(name, rows)
    with (ROOT/'dados/eventos_partida.jsonl').open('w', encoding='utf-8') as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False)+'\n')
    (ROOT/'manifesto.json').write_text(json.dumps(dict(seed=SEED, locale='pt_BR',
        temporadas=list(range(2021, 2026)), clubes=len(clubs), jogadores=len(players),
        partidas=len(games), eventos=len(events), natureza='Inteiramente fictício'),
        ensure_ascii=False, indent=2)+'\n')
    print(f'Sintético: {len(games)} partidas, {len(players)} jogadores, {len(events)} eventos')

if __name__ == '__main__':
    main()
