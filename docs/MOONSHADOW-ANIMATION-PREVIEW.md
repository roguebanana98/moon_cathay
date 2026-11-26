# Model 11 animation trial

User requested an animation preview to inspect errors. This is a separate
Blender test, not a game animation export or deployment.

Scene: `build/moonshadow-animation-preview/alchemist-11-animation-review-v2.blend`
Source: tracked `assets/working/moonshadow-assassin/alchemist-11-working.blend`
(source SHA256 remains `4ec5b0d4fe5597b0a97f7e111836460b6cd1ab76acb625d136a3706ebfaa0d25`).

Eight native Khainite sword/handbow clips are retargeted from humanoid01d onto
the original humanoid01e rig. Rest-orientation correction and target bind lengths
are used; geometry, weights, rest bind and hidden mesh states are preserved.
Semantic aliases map differently named head, eyelid, shoulder and skirt bones.
Unmatched native target bones follow their parent hierarchy. This is not cloth
simulation. Horizontal root motion is suppressed only for stationary inspection.

| Timeline frames | Motion |
| --- | --- |
| 1-55 | Stand |
| 56-142 | Walk, three cycles |
| 143-199 | Run, three cycles |
| 200-240 | Dagger attack 1 |
| 241-301 | Dagger attack 3 |
| 302-338 | Jump attack |
| 339-393 | Aim handbow |
| 394-442 | Fire handbow |

The active master action plays all eight segments. Press Space to pause/resume.
Timeline markers identify each segment; individual `MW 01` through `MW 08`
actions are also saved with fake users for separate inspection in Action Editor.
All used textures are packed. Source working model and its Git version are not
overwritten. No automatic Git upload of the new trial scene has been performed.

Checks verify finite evaluated mesh vertices, real displacement over sampled
frames for all eight motions and dagger/handbow anchor alignment with target hand
bones. Actual Blender playback was observed changing frames and poses. This
does not prove engine lookup or in-game compatibility.

Visual issues remain: the long robe panels/cape swing sideways and intersect the
legs/body in the transferred poses, including the run; standing panels also need
review. Shoulder/skirt mappings, fingers/grip and shooting alignment remain visual
QA. This trial is deliberately not marked clean or ready for game integration.

Tools: `Prepare-Moonshadow-Animation-Preview.py` extracts eight native clips;
`Build-Moonshadow-Animation-Preview.py` bakes target actions and produces
`animation-preview.json`. The first unaliased scene is superseded by v2.
