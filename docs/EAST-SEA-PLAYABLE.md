# East Sea Charter — playable campaign

User request, 2026-11-18: make East Sea Charter selectable and playable.

New pack: `edh_east_sea_charter_playable_v5.pack`, replacing v4 locally. Choose
Immortal Empires Expanded, then The Empire, then Heinrich von Adlerhorst / East
Sea Charter. Start a new campaign to use the existing Dai Loa + Preenn setup;
Sariwa starts independently beside Heinrich's army. This does not change an
existing save's player faction.

The registered MIXER character ID `186992224` belongs to the original faction
slot `mixer_emp_vaults_gigasdongo`. The frontend script calls MIXER's supported
enable, major-faction, lord-name and starting-unit-preview functions. Marking
the faction major prevents the minor-faction visibility preference hiding it.
No global helper or other faction is overridden. Original frontend party key
and `startpos_map=default` remain the registered values. Heinrich's existing
portrait and subtype replace the dummy faction leader presentation. The native
Karl Franz selection scene/movie is temporarily reused; a bespoke scene showing
the exact custom mesh is not authored. Campaign/battle model stays unchanged.

Three additive payloads: one frontend Lua, one scoped frontend leader DB row,
one localization file. Every v4 payload, including startpos, campaign startup,
skills, models, Sariwa and refuge/homecoming events, is byte-identical. The
separate `edh_heinrich_sariwa_v4.pack` remains required and enabled.

Validation uses actual installed MIXER helper/frontend library functions under
a standalone Lua host, checking ID mapping, visible major status, correct name,
unit preview, repeated callbacks and preservation of every other hidden faction.
DB/loc roundtrip is lossless; dependency fingerprints match the reviewed v4
installation. RPFM has no unexpected diagnostics. Reports and launcher rollback
backup are in `build/east-sea-playable/`; deployment.json is authoritative.

No game was launched and no saves changed. Actual selection, human-faction
initialization and extended campaign play remain unverified in game, as requested.
The earlier updated-IEE/startpos compatibility limitation recorded in
`EAST-SEA-REFUGE.md` remains; this frontend extension does not rebase startpos.
