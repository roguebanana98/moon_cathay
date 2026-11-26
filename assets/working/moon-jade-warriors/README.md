# Moon Jade Warriors — approved editable checkpoints

These files are stored directly in ordinary Git; no LFS download is needed for
the Jade models or mod pack. These are complete, byte-identical saved scenes,
including packed textures; open the full file in Blender 5.2.2 or compatible newer
Blender. Do not append every object into a fresh scene or regenerate over edits.

- **moon-jade-warriors-working.blend** — authoritative seven-variant family,
  approved body05/equipment and original DEER head options01–07; head07's hidden
  upper scalp tucked under the helmet. Eight-stage native animation montage
  remains on the seven native humanoid01e rigs.
- **moon-jade-warrior-animation-review.blend** — exact single-character scene
  reviewed before the family was assembled. Space starts/pauses the timeline.
- **moon-jade-exported-assets-review.blend** — actual exported RMV2/DDS assets
  reimported for verification, all seven heads preserved with one visible.
  Preserve visibility flags. This is a separate export review, not the main
  appearance-editing checkpoint.

`checkpoint.json` records exact byte counts and SHA256 values. Read-only reopening
results are in `reports/portable-scenes.json`; other reports are portable copies
using `PROJECT_ROOT`/`GAME_ROOT` placeholders. Previews and user reference images
are included beside the scenes. The pack itself is stored directly in Git at
`releases/moon-jade-warriors-reskin-v1/mc_moon_jade_warriors_reskin_v1.pack`.

The user explicitly requested backing up current source, models and mod to Git
on 26 November 2026, then requested avoiding unnecessary LFS use. This is a scoped exception for these authored checkpoints
and the resulting reskin pack. Raw native/Workshop extraction, machine config,
temporary bake caches and unrelated build history remain outside Git.

The built mod is installed locally but was not enabled in the launcher or tested
inside the game. It changes only Moon's sword-and-shield Jade Warriors and needs
IEE; the DEER24 source pack is not required by the built mod. Native stats and
animation profiles are unchanged. The Blender montage is presentation data;
never export it as a replacement native game animation. See
`docs/MOON-JADE-WARRIOR-APPROVED-RESKIN.md` for design and validation limits.
