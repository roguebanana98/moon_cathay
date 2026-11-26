# Divine Wing Guard — editable checkpoint

Open `divine-wing-guard-working.blend` in Blender 5.2.2 or a compatible newer
version. The file is tracked through Git LFS; after cloning, run `git lfs pull`
if it is still a small text pointer rather than the 36,903,322-byte Blender file.

This is the full scene saved from the user's live animation review on
26 November 2026, at frame 496. It includes Jade Warriors armour/head/sword/shield,
white feathered wings derived from Angels of Warhammer, the original hidden donor,
both native preview rigs, eight timeline stages, materials and 32 packed images.
There are no linked libraries or external image dependencies. Use Space/Play to
start playback; it does not automatically start when opening the file.

SHA256: `3a649c18551828fd16510a4e7f0ee8ceb76bedc606f25e4d5bc257eca98b0711`.
See `checkpoint.json` for portable paths, stages, provenance and limitations.

**Blender preview only, not integrated into the game.** The two rigs have not
been converted to a single game export rig. Folded feathers may overlap the
shoulders/head, and the airborne attack retains spear choreography while holding
the current sword. Flight altitude and the review montage are Blender presentation
data, not exported game animations.

Continue from this file, saving edits as a new working version. Do not run the
generators over user edits. Older paths under `build/` are local working/backup
paths and need not exist in a clone. Do not append all objects into a fresh scene:
open the full file to preserve donor/rig/studio visibility flags.

The user explicitly requested this scoped editable-model Git backup, including
packed textures. Extracted native/Workshop inputs, caches and game packs remain
outside Git. The backup does not authorize game integration or establish runtime
compatibility. Detailed notes: `docs/DIVINE-WING-GUARD-ANIMATION-REVIEW.md`.
