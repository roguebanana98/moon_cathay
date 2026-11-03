# Da Lien — revised spell direction, 03/11/2026

The user approved this revised direction and requested integration for testing.
Implemented/deployed in v23; see [current test notes](DA-LIEN-V23-SKILL-TEST.md).
The Metal-heavy v1 spell selection is superseded. Runtime verification is pending.

Use Yin as the main identity, supported by celestial magic from Heavens and two
Life spells for the requested light healing/armour role. This is a deliberately
mixed Legendary Hero kit, not a claim that ordinary human Cathay wizards normally
master all three lores. Any narrative explanation remains to be agreed.

| Native spell | Role |
|---|---|
| Blossom Wind | Early wind attack through infantry formations; starting base spell |
| Storm of Shadows | Slow/control to hold enemies in the damaging spell area |
| Talons of Night | Main advanced AOE spell, matching Yin/night identity |
| Comet of Casandora | Delayed celestial strike against clustered troops |
| Earth Blood | Secondary healing; no resurrection or extra Life Bloom |
| Flesh to Stone | Armour support, replacing Glittering Robe |

Replace Metalshifting with Power of Yin, subject to verifying its actual benefit
and trigger in the mixed kit. Keep caster basics, Hero actions, resistance skills,
Mentor and free immortality from the first draft. Moon Scholar should now support
Yin/Heavens, not Metal. The other unique nodes remain proposals and should be
reviewed for thematic distinction. Do not copy the Yin Lord's red/campaign tree.

Remove Searing Doom, Golden Hounds, Transmutation of Lead, Glittering Robe,
Dwellers Below and Metalshifting from the active proposal. No Metal spells remain.

These are existing native spells with native names/icons/VFX. Moon names or silver
VFX would be additional work, not achieved merely by renaming. In particular,
Comet remains the native celestial impact, not a newly authored moon beam.

V23 recalculates upgrade levels, free starting base spell and point gates: 26
visible nodes and 51 maximum purchased points. Static multi-lore, overcast and
progression checks pass; passive triggers, mana costs and model casting still
need in-game verification.

Native skill keys/icon names are recorded privately in
build/da-lien-skill-design-v2/native-skills.json; icons exported there for private
presentation only. V23 skill-manifest.json records the implemented nodes, source
skill keys and spell set; pack roundtrip and effect-bridge checks pass.
