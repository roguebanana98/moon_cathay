# Campaign loading hang and array-type repair — 2026-10-31

User reproduced a hang while starting a new campaign with each original private
test pack separately. IEE + MIXER without either test pack loads normally. Both
original artifacts must be treated as failed runtime tests, not usable releases.

The observed used_mods.txt and modified.log confirm the province-only pack was
enabled. Its installed hash matches the delivered pack. Lua logs show campaign
scripts loading but contain no explicit diagnostic establishing the hang's cause.
No new crash dump was present. No reason is established to blame load order alone.

## Concrete serialization bug

Build-Province-Candidate.py wrote Moon faction province membership lists using
ESF type byte 0x47 (UINT16_ARRAY), instead of the original UINT32 array family.
EditSF's EsfType enum independently confirms 0x56 = UINT32_BYTE_ARRAY and
0x57 = UINT32_SHORT_ARRAY. The Python inspector erases primitive type information,
so equal decoded numbers passed the previous tests despite the incompatible type.

The builder now emits 0x57 and explicitly asserts UINT32-array family on these
fields. Repair-Province-Array-Types.py patches the archived tested outputs,
changing exactly two decompressed bytes in each. All other campaign payload bytes
are identical. Recompression/reopen checks pass. This is a confirmed format bug
and a strong candidate cause of the hang, not a runtime-confirmed root cause yet.

## Replacement artifacts

User runtime confirmation (2026-10-31): the v2 fix successfully loads a new
campaign. Supplied screenshots show the intended province regrouping and eight
visible Long Vi slots. The user requests normal tier-dependent slot locking;
the current custom chain incorrectly unlocks all seven secondary slots at every
tier. This is a separate follow-up from the resolved loading failure.

- `build/province-array-fix/mc_province_v2_uint32_fix.pack`
- `build/province-array-fix/mc_longvi8_v2_uint32_fix.pack`

Both have validated dependency headers and identical non-startpos gameplay and
localization files compared with their original respective packs. Checksums and
changed-byte offsets are in pack-manifest.json and repair-report.json beside them.
Neither replacement has been deployed or tested in game by the assistant.

Test province_v2 first with both old packs disabled and the same otherwise-working
IEE/MIXER setup. If it loads, test longvi8_v2 instead (never both variants together).
Use a new campaign. Keeping other variables constant isolates the serialization
repair. If the hang remains, isolate DB changes versus startpos and investigate
province/AI state consistency; do not claim the issue is resolved.
