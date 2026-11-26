# Moon recruitment and Vietnamese names - private v26

## Recruitment

Disables original wh3_main_cth_astromancer and wh3_main_cth_alchemist recruitment for cr_cth_agents_of_the_moon only. Moon casters, Moonveil Adept and other replacements remain available. This does not delete already recruited characters or change other factions. Existing subtype definitions, unit stats, skill trees and capacity effects are preserved.

Moonshadow Assassin availability AND its original +1 capacity move from all three Celestial Tower levels to wh3_main_cth_jade_barracks_2 and wh3_main_cth_jade_barracks_3. Tier1 does not enable the hero. Upgrading2->3 retains +1 per building rather than stacking. Effects retain mc_moonshadow_owner context, original scope, damaged/ruined behaviour and values. No native building costs, garrisons or unit permissions change; the three Moon casters still recruit through their original tower chain.

## Authored name bank

Source JSON: src/data/agents-of-the-moon-vietnamese-names.json. CSV export: src/data/agents-of-the-moon-vietnamese-names.csv. Stable record IDs, type, gender, frequency and ASCII text are included.50 surnames,152 male given names,283 female given names,14 unisex given names:499 records and22,450 possible distinct surname/given-name combinations. All full combinations fit below32 characters.

Examples: Nguyen Minh Duc; Tran Ngoc Lan; Le Khanh. Compound given names already include a Vietnamese middle-name component where appropriate. The name group uses family_name before forename, including native default/cn/kr/zh display-order variants. No accents or non-ASCII punctuation are used. IDs are in private1986120000/1000/2000/3000 blocks; keep existing IDs stable and append unused ones when extending.

The faction's name_group changes to names_mc_agents_of_the_moon_vietnamese. Its actual current IEE faction row was freshly extracted and checked against all active pack faction tables; only one active source defined this faction. Every faction field other than name_group is retained, including flags, colours, unit/ship-name groups and military group. Native Cathay name records are not globally changed.

Eight authored regular subtypes explicitly use the group: Assault General, Bastion General, Pyromancer, Tidecaller, Astral Weaver, Moonveil Adept, Moonshadow Assassin and integrated Ordnance Master. Native human subtypes with blank name-group overrides inherit the faction group. Native nonhuman subtypes with their own explicit group (e.g. Tigermen) keep that group. Legendary/fixed characters such as Huyen Ve and Da Anh remain unchanged.

The group applies when the game generates new names. Existing characters, pre-generated recruitment-pool entries, manual names from Custom Lord Creation and fixed names are not retroactively overwritten. Pool refresh/new recruitment or a fresh campaign is appropriate for testing; no live save migration or forced renaming script is shipped.

## Validation and deployment

- ASCII/format/uniqueness/frequency/stable-ID checks, native/base ID collision checks, JSON/CSV equality and display-length bounds.
- Exactly two barracks levels with original +1 capacity/availability and no tower Assassin effects; owner context preserved.
- Disabled native wizard/engineer subtypes only; replacement permissions remain unchanged.
- Exact equality of all faction fields except name_group and all subtype fields except names_group. No models, scripts, skill payloads or previous bug fixes changed.
- New/changed DB/localization tables roundtripped through RPFM; zero blocking diagnostics.
- Combined v26 installed/enabled, previous v25 retained disabled and launcher backed up. No saves, native or Workshop files modified; no Git/public upload.

No game was launched; recruitment and generated-name appearance are not runtime verified. Restart with mc_moonshadow_heroes_v26_recruitment_names.pack enabled when testing. The v25 Assault appearance repair and every previous combined-mod feature are retained.

Reports: build/moon-v26-recruitment-names. Tools: Create-Moon-Vietnamese-Name-Data.py (one-time authoring/export; refuses to overwrite JSON), Build-Moon-Recruitment-Vietnamese-Names.py, Deploy-Moon-Recruitment-Vietnamese-Names.py.
