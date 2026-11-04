import csv
from pathlib import Path
R=Path(__file__).resolve().parent/'reference/db'
def read(t):
    p=R/(t+'_tables/data__.tsv')
    if not p.exists():return []
    with p.open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE);next(r);return list(r)
for t in ['main_units','unit_variants','variants','units_custom_battle_permissions','battle_set_piece_armies_characters','land_units_to_unit_abilites_junctions','special_ability_groups_to_units_junctions']:
    rows=[r for r in read(t) if 'wh_main_brt_cha_damsel_0' in r.values()]
    print('\nTABLE',t,*rows[:8],sep='\n')
for t in ['unit_abilities','effect_bonus_value_unit_ability_junctions']:
    print('\nTABLE',t,*[r for r in read(t) if any('greater_arcane_conduit' in v for v in r.values())][:3],sep='\n')
