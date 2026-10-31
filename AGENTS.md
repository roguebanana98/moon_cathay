# Project constraints

## User-authorized exceptions (2026-10-31)

- Campaign scope expanded specifically to regroup Primal Labyrinth (Long Vi capital,
  Leilou) and Paradise Spires (Dai Loa capital, Avauka, Preenn).
- User explicitly approved installing EditSF 1.3.0 under local tooling and packaging
  derived IEE startpos plus the two province-related DB tables in a private local
  test pack. This is an exception to the third-party bundling prohibition below
  only for this ignored local test artifact; no third-party content enters Git/src.
- Deployment to game/Workshop, gameplay launch and public redistribution are not
  included in those approvals. Preserve original dependency packs and live saves.
- User additionally requested 8 total building slots at Long Vi, preserving its
  existing buildings including the port, and approved a separate current WH3
  RPFM schema in local tooling. The private test pack may include the scoped
  building definitions and localization required for that change.

## General constraints

- Phase 1 only until the user explicitly expands scope. Do not change gameplay/campaign.
- Never write to game installation or Workshop paths. Reference packs are read-only inputs.
- Do not install/update software or schemas without user permission.
- All extraction goes to ignored `reference/local/`. Never bundle or commit third-party assets.
- Only authored source may enter `src/`. Keep source, reference, build, and dist separate.
- Use verified paths in ignored `config/local.json`; do not guess tool commands or Lua APIs.
- Any future runtime claim must distinguish static startpos, frontend placeholders, MCT options, and a live save.
- Re-check dependency hashes after Steam updates. Validate schema before importing changed DB tables.
- No publishing or gameplay launch is part of Phase 1.
