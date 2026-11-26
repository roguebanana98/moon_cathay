# Moonshadow Assassin: approved body and four faces

The user selected the current edited model 11 as the Moonshadow Assassin body
and requested four appearances using More Alchemists faces **8, 11, 3, 12**, in
that order. These are editable Blender appearances, not four different hero types.

Final resume directory: `build/moonshadow-assassin-final/`. Open
`moonshadow-assassin-final.blend` for the final comparison; the four individual
files below are also copied there. Final hashes: `final-checkpoint.json`.
All Blender windows were saved where modified and closed at the user's request.

Original construction directory: `build/moonshadow-assassin-four-faces/`.

| Appearance | Face source | Editable file |
| --- | --- | --- |
| 01 | 08 | `moonshadow-assassin-face-08.blend` |
| 02 | 11 | `moonshadow-assassin-face-11.blend` |
| 03 | 03 | `moonshadow-assassin-face-03.blend` |
| 04 | 12 | `moonshadow-assassin-face-12.blend` |

`moonshadow-assassin-four-faces.blend` shows all four with labels. Each individual
file opens on its appearance at the origin; other models and original reference
objects remain hidden backups. `approved-body-live.blend` preserves the actual
live user checkpoint before creating variants. Do not rebuild over manual edits.

Shared body retains the black hood, charcoal ornament, original lower skirt,
Death Squad right-hand knife with corrected handle placement, and Khainite left
handbow. The rear cape, center strip, red shoulder plates and two patterned
shoulder ribbons stay absent. Rejected expanded-leg and Death Squad trouser
experiments are not used.

Face meshes and native materials come from the selected More Alchemists variants.
Original facial accessories are retained; disconnected bun/hairpin islands above
1.70 m on faces 3/12 are omitted to fit the common hood. Variant 12's separate
wide neck scarf is also omitted so the shared outfit remains visible. Original
donor objects are preserved hidden in the file.

All donor/target rest bone matrices match within 1e-5. Every appearance has its
own copied native 96-bone rig; head and body modifiers, both weapon constraints
and parents reference that appearance rather than another model. Body geometry
fingerprints match the approved source. Six animation frames per model were
checked for finite face deformation, moving head pose and correct weapon anchors.
The comparison was visually inspected standing and at walk frame 75 in Blender.
Each individual file was reopened: only its model meshes are visible, all used
images packed, no linked libraries. Reports: `four-faces-report.json` and
`reopen-audit.json`.

Existing animation preview problems remain: fingers are not fully closed and
the original lower cloth may clip/expose legs during movement. These checks do
not establish clean full animation or game compatibility. Black/charcoal edits
are shader treatments; texture baking, export/LODs and runtime animation binding
are still needed before game integration. The deployed hero pack still uses its
previous native temporary appearance. No game pack, launcher, tracked portable
checkpoint or Git remote was changed by this appearance task.

Build script: `tools/Build-Moonshadow-Assassin-Four-Faces.py`.
