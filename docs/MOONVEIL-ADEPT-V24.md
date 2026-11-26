# Moonveil Adept - private v24

Creates one ordinary, repeatable support hero replacing Alchemist recruitment for Agents of the Moon only. Existing Alchemists and other factions are not rewritten. It shares the native engineer/Alchemist capacity and all original Alchemist recruitment-building availability (seven native building rows, owner-scoped to the Moon faction), with no new building or extra cap. A private recruitment category displays Moonveil Adept.

## Kit and balance

Native Lore of Light, original English spell names, six spells and Exorcism passive, with native costs, cooldowns, overcasts, icons and VFX. Spell nodes and prerequisites come from the Empire Light Wizard. The native hidden starting Shem's Burning Gaze, Evasion, Earthing, Magical Reserves and Arcane Conduit are retained.

Campaign actions and generic/innate/resistance nodes come from Alchemist: Increase Mobility, Boost Income, Damage Building, Assassinate, Hinder Replenishment and Specialist. Personal metallurgy, alchemical enhancement and army metallurgy branches are omitted. No custom spell/ability/phase/effect mechanics are authored. Hero stats, costs, unit caps, mounts and recruitment-level behaviour use native Alchemist values. It stays a fragile support caster rather than receiving source-mod unit stats.

Warhorse and Sky Lantern use native Alchemist battle profiles, native mounted-unit stats and private mount grants with the original level6/14 criteria. Private ancillaries point to the new hero units, never the native Alchemist body. Campaign override mappings are scoped to these units; Sky Lantern receives an override matching the Alchemist campaign profile to the existing native Sky Lantern rider set.

## Appearance

Model source: local Workshop3836052402, @taolu_cth_esoteric_masters.pack. Only graphics are copied; source regiment stats/skills/units are not integrated. Four appearance families: source Air/white (visually gold-toned), Earth/black, Water/blue and Fire/red. Original eight body choices and two head choices per family remain in nested VMDs; body/head palette choices stay coherent. All40 source WSModels retain their four LODs and geometry/DDS bytes. Every material reference is privately namespaced, with complete LOD material coverage. Original visible clothing and skin are preserved; native limb-stump option slots are omitted from the source regiment definitions.

Four campaign art sets/uniforms and portrait settings give recruit appearance variety. The combined default VMD includes the four coherent appearance families. Custom Battle's explicit hero character uses the first source appearance, with both native mount selectors. New 2D portraits, unit card and minspec portraits are rendered from the packaged graphics.

## Validation and deployment

- All40 WSModels checked for native humanoid01e, four LODs and full material coverage.
- Four representative body/head pairs, nine native stand/movement/melee/cast/rider clips and three sample frames each:108 finite, deforming pose samples; no importer warnings. All four idle body/head renders inspected. Source texture/material colours remain unchanged.
- Exact native Alchemist land/main unit stat/cost equality (only identifiers/descriptions/UI group differ). Shared cap and faction-only replacement permission checked.
- Complete native Light skill tree/starting spell and reachable prerequisites; no Metal spell or metallurgy skills.
- Hero caste/UI parent heroes_agents and general_unit=false for foot/horse/lantern; native Light CB group and spell preset, two mount selectors.
- Every v23 payload preserved byte-for-byte; additive tables/graphics only. RPFM roundtrip succeeded, zero blocking diagnostics.
- Combined v24 installed/enabled; v23 retained disabled, launcher backup in build/moonveil-v24. No saves, native packs or Workshop files modified. No Git/public upload.

The game was not launched. Campaign recruitment/pool refresh, spell VFX, complete mount/crew clipping and existing-save behaviour remain unverified in-game. The Blender pose check covers riders, not a full assembled mount simulation. The source model mod is not required at runtime; native game assets are referenced directly.

Build/report folder: build/moonveil-v24. Scripts: Prepare-Moonveil-Adept-Models.py, Review-Moonveil-Adept-Models.py, Build-Moonveil-Adept-Pack.py, Deploy-Moonveil-Adept.py. Source manifest: src/campaign/moonveil-adept.json.
