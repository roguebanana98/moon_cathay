# Assassin appearance saved for later

User requested saving the current model on 2026-11-21. The actual live Blender
scene, including user changes since generation, was saved with File > Save and
the save notification/clean title verified. A byte-identical checkpoint and SHA256
are recorded in `build/alchemist-11-khainite-weapons/resume-latest.json`.

Working file:
`build/alchemist-11-khainite-weapons/alchemist-11-khainite-dagger-and-handbow-v3.blend`

- More Alchemists variant 11, native humanoid01e body/rig.
- Reversible black clothing shader, preserved red/gold ornament and grey hood.
- Native Khainite dagger in right hand, native handbow in left hand.
- Current user-edited pose/view, attachment placement, materials and hidden parts
  are saved. Original textures/source Workshop and native packs remain untouched.
- Native Khainite stand action belongs only to a hidden reference rig used for
  grip alignment. It is NOT a target animation integration or retarget result.
- No export/deployment, no runtime animation or gameplay claims.

Resume from saved v3 or its immutable checkpoint. Do not rerun the appearance or
weapon generator over this working file: it predates the user's latest manual
changes. Open the full scene instead of appending all objects, because append
does not preserve per-view-layer hide flags. Older weapon v1/v2 scenes contain
superseded attachment/visibility states and must not be used as the working base.

The user asked to keep the sample for later; this is not approval to replace the
currently deployed native temporary hero appearance. Animation, any final texture
bake and game integration still await the user's next request.
