# Da Lien — signature red gem

03/11/2026. Confirmed user requirement: Da Lien has one accompanying magic item,
a red gemstone inspired by the gem on her model's chest. The user subsequently
requested integration: implemented/deployed in v24, runtime pending. See
[current implementation and test notes](DA-LIEN-V24-MOONSTONE.md). The following
sections preserve the original design rationale.

Proposed name: **Crimson Moonstone**. Vietnamese reference: **Huyết Nguyệt Châu**.
Proposed slot: Arcane Item, restricted to Da Lien. Treat the visible chest gem as
its visual identity; no model changes are needed for this concept.

Proposed effects:

- +5 Winds of Magic reserve capacity for the owning army.
- +5% ward save for Da Lien.
- **Moonlit Renewal**: one use per battle, zero Winds cost. Reuse base bound
  Earth Blood behaviour for a small area heal, with no resurrection and the
  normal healing cap. No added Life Bloom or ongoing passive regeneration.

The gem stores moonlight and protects its bearer, with a small emergency heal.
This complements the offensive spell kit while keeping healing a secondary role.
Numbers and ability selection require review and later runtime balance testing.

Acquisition proposal: grant/equip when Da Lien is acquired; no separate quest.
For the current test framework, support the existing Long Vi Hero with an
idempotent grant marker. Also provide Custom Battle equipment access. Do not
repeatedly force-equip after the player has removed it.

Implementation notes for later:

- Subtype whitelist `mc_da_lien`, transferable=false; allow normal unequip/re-equip.
- Avoid the unique_to_world/unique_to_faction flags that previously caused the
  Huyen Ve re-equip issue; subtype restriction plus a grant marker controls access.
- Native effects for reserve capacity and ward save already exist in the local
  DB. Native bound Earth Blood has two uses; a scoped derivative would change it
  to one, rather than changing the shared native spell or Da Lien's learned spell.
- Native artwork for the UI icon, per project preference. A chest-gem crop or
  new artwork would need a separate decision. Do not bundle source-mod assets.
- Check item enabled/disabled effects, army reserve stacking, unique ability
  count, healing cap, Custom Battle selection, existing-save grant and re-equip.

At the original design milestone no pack or gameplay changed. The subsequent
v24 implementation adds the item, ability and grant script while preserving all
v23 payloads, model and portraits. Runtime checks remain pending.
