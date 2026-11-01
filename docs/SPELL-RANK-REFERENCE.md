# Spell progression reference audit — 2026-11-01

Read directly from the locally extracted vanilla DB under
reference/local/lord-vanilla/db. This is an audit of this installed-data snapshot,
not a claim about every Lord, future patches or all mod overrides.

Joined character_skill_node_sets -> character_skill_node_set_items ->
character_skill_nodes -> character_skills, plus character_skill_level_details,
character_skill_node_links and character_skill_level_to_effects_junctions.

## Observed examples

| Lord | Spell | Observed progression |
|---|---|---|
| Cathay Yang Shugengan | Dragon's Breath | Visible first spell node has zero points on creation; hidden starting skill enables base Breath/Jade Shield. Visible skill rank field is 0; no per-level rank override found. |
| Cathay Zhao Ming | Dragon's Breath | Hidden starting skill enables base Breath/Plague of Rust. Visible Breath node requires the opening Plague of Rust node, not a fixed character-level 6 gate. |
| Cathay Miao Ying | Earth Blood | Hidden starting skill enables base Earth Blood/Storm of Shadows; visible Earth Blood upgrade is an opening spell node. No fixed level-8 gate found. |
| High Elves Alarielle | Earth Blood | Starting hidden skill; visible upgrade has no rank override in the audited tables. |
| High Elves Life Archmage | Earth Blood | Starting hidden spell-enabling skill; visible upgrade lies in the early Life branch. |
| Bretonnia Life Prophetess | Earth Blood | Hidden starting spell grant; visible node requires Awakening of the Wood. No per-level hard rank gate found. |
| High Elves Fire Archmage | Flame Storm | Requires Potential Energy; this gate has required_num_parents=4 from the earlier spell group. No fixed 12/16 gate on Flame Storm. |
| Dark Elves Fire Supreme Sorceress | Flame Storm | Requires Evasion; gate threshold four, same native-style upper/lower branch progression. |

All named visible spell skill records have unlocked_at_rank=0 and no relevant
character_skill_level_details rows in this snapshot. This does NOT mean they
are all available immediately: links and investment thresholds still apply.
Hidden base-spell enablement is not equivalent to a free point in the visible
upgrade skill. Moon Warden's requested two visible starting investments are
therefore more generous than the observed native base-spell grants.

## Implication for Moon Warden

V10's 6/8/12/16 rank locks were bespoke proposals, not extracted vanilla ranks.
For native-like progression, allow early investment in the two starter spells
and gate Flame Storm by earlier spell investment/an intermediate gate. The
three-spell compact row lacks a full native first spell group; copying a four-
point gate without checking available ranks would be inappropriate. If retaining
hard level gates for a compact tree, label them as custom balance, not vanilla.

No pack changed during this reference audit. V10 remains the current build until
the progression design is changed explicitly. Preserve the user-requested
starting visible level 1 Earth Blood and Dragon's Breath in any revision.
