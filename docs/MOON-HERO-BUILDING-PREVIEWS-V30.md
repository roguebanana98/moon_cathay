# Hero portraits in the building browser - v30

User reports only Moonveil has a hero image next to recruitment buildings in the building browser. V29 already contains the hero portrait/card textures; missing image assets are not the static issue found.

The building browser uses units_custom_battle_permissions for hero previews (see the modding reference: https://tw-modding.com/wiki/Units_custom_battle_permissions_tables). All previous authored permissions target the Cathay MP faction, not the Moon campaign faction; Moonshadow has no permission at all. V30 adds explicit campaign-only permissions for the Moon faction for Moonshadow Assassin, Pyromancer, Astral Weaver, Tidecaller, Ordnance Master and the working Moonveil Adept. Existing MP entries remain unchanged. Moonshadow uses its approved face08 portrait/uniform and receives the same military grouping as the other heroes. No set-piece character is assigned to that campaign-only preview.

These are native data additions, not runtime UI callbacks. Two new payloads are added; every pre-existing v29 payload is byte-identical. Recruitment buildings, availability/cap effects, costs, skills, models, general tabs and all scripts remain unchanged. Da Anh is a unique starting legendary hero, not a building-recruited hero, and is not added as a building unlock.

Validation: all six portraits, unit cards and uniforms resolve within the pack; no duplicate campaign permission keys; RPFM DB roundtrip passed and zero blocking diagnostics. This repairs the identified preview-data gap but visible rendering and whether further recruitment-effect display links are needed remain unverified until tested in-game.

Build: tools/Build-Moon-Hero-Building-Previews.py. Deployment: tools/Deploy-Moon-Hero-Building-Previews.py. Reports: build/moon-v30-building-previews. Current extracted DB reference: reference/local/moon-v30-roundtrip/db. No public redistribution, native/Workshop or save modifications.
