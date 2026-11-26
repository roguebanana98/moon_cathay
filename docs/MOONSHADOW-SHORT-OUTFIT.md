# Model 11 short outfit trial

User requested removing robe tails on 2026-11-21. Separate local preview:
`build/alchemist-11-short-outfit/alchemist-11-short-outfit-animation.blend`.

Source is the live full-scene snapshot `before-short-live.blend`, preserving
per-view-layer hidden parts and the existing animation timeline. Whole disconnected
cape and skirt components below the waist were removed from a copy of the main
body mesh; no cut crosses a connected torso component. Original mesh retained as
hidden `BACKUP | Model 11 original long outfit` (also disabled for rendering).
To restore, hide `Model 11 | Short outfit`, then unhide the backup in the viewport
and enable its render visibility.

Upper body, hood, belt, existing legs/boots, weapon attachments, rig and animation
actions retained. Removing the skirt exposes the original bare upper thighs;
this trial does not add trousers or repaint skin. Packed textures retained.
Opened and visually inspected the separate Blender scene at standing frame 1.
Animation cleanup and engine export remain pending; this is not game deployment.

Component selection and face accounting: `short-outfit-report.json` beside the
scene. Reproduction script: `tools/Preview-Alchemist-11-Short-Outfit.py`.
Tracked portable checkpoint and original animation review were not overwritten.
