# Da Anh dagger and handbow - v11

The user approved the corrected Moonshadow animation trial and requested deployment.
Da Anh now uses the approved Celestial Concubines body01/head01, black fitted
clothing, closed charcoal chest panels, plain shoulder plates, Death Squad knife
in the right hand and the original native Khainite handbow in the left hand.
The handbow fitting uses the actual native standing prop/grip frames and target
palm/rest-axis compensation, replacing the previous exported donor's bad offset.

## Installed build

Enabled mc_moonshadow_heroes_v11_da_anh_handbow.pack. V10 retained disabled.
SHA256: 7ed15a7ea89b7cfab44c0096709a7887a872953d4973a985177ff1c9572b40cb.
Authoritative build/da-anh-v11-dagger-handbow/deployment.json and pack-validation.json.
Launcher backed up, unrelated entries and previous pack files unchanged. No saves,
native packs or Workshop packs edited. No game launch and no Git upload.

## Authoring and native export

Approved self-contained source: assets/working/da-anh/da-anh-dagger-handbow-approved.blend.
Its editable source rig remains native humanoid01e (96 bones), with eight retargeted
preview motions and corrected native bow fitting. Old dual-knife checkpoint retained;
assets/working/da-anh/checkpoint.json identifies the current approved source/build.
The source scene's historical integration notes are superseded by this document.

Runtime now uses genuine humanoid01d (83 bones), matching Moonshadow Assassin.
The approved source posed surface and normals were inverse-skinned to the native
bind, rather than merely renaming the skeleton. Hair/accessory weights mapped to
native head/parent bones; weights merged and normalized to four influences.
Native grip overlay was applied during bind fitting. Corrected approved weapon world
transforms were baked into native be_prop_1 (knife) and be_prop_5 (handbow) frames.
Both props are static RMVs attached in the VMD; no Blender constraints are needed
by the game. The authoring source and other Moonshadow models are unchanged.

Native battle lookup: hu1d_elf_sword_and_handbow.
Native campaign lookup: cam_hero_hu1d_elf_sword_and_handbow.
No custom animation database or skeleton lookup is introduced.

Four LOD triangle counts:
- Body: 45182 / 22588 / 11292 / 5642 (seven parts).
- Knife: 454 / 227 / 113 / 56.
- Handbow: 1387 / 693 / 346 / 173.

All DDS references are self-contained. Native DDS bow maps are copied directly;
procedural black cloth is represented by constant PBR maps. Chest panels retain
original cloth colour with neutral fabric material/normal maps. Procedural microbump
is not exported. Rendered cards/portraits use the actual reimported RMV scene.

## Unit configuration and preservation

Restored the pre-melee Da Anh handbow weapon, 50 ammo, ranged unit classification,
skirmish permission, archer categorization and missile value. Existing melee weapon,
combat stats, skills, effects, recruitment/cap and spawn logic remain unchanged.
The v10 turn-one AP fix Lua is byte-identical. Every Moonshadow Assassin appearance
and all skill/localization table payloads remain byte-identical to v10.
The existing custom variant/uniform/portrait lookup keys and campaign art ID remain;
only Da Anh's model/VMD, images, battle/campaign animation and weapon-related DB
fields are changed. Existing ranged skills now have a ranged weapon again.

## Verification and limitations

All three exported RMVs reimported onto the real native rig. Eight native battle
clips and two campaign lookup clips sampled at three frames each (30 pose samples),
with finite geometry and nonzero movement. Verified four LODs, native bone-index
limits, normalized weights, all texture references, table pack roundtrips, unchanged
unrelated rows/payloads, and zero blocking RPFM diagnostics (metadata warnings only).
Native bind fitting preserves the approved reference pose; cloth/finger/hair clipping
in other motions can still need refinement. Actual in-game animation, projectile
muzzle alignment, old-save appearance caching and campaign presentation remain
unverified. Restart/reload campaign to test; do not claim runtime success from these
Blender/static checks alone.
