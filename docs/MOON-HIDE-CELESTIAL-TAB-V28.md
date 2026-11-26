# Hide the empty Celestial General tab - private v28

User clarified that Celestial General is an empty recruitment tab, not a source of recruitable lords. The native Yin/Yang subtype permissions were already disabled for Agents of the Moon. The category itself remains in the native campaign panel.

The patch hides only that category button while the local player is cr_cth_agents_of_the_moon. Native category records and UI layout files are not modified globally. Assault and Bastion remain available; if the hidden native category was selected by default, its selection switches to Assault (Bastion fallback). An existing Bastion selection is preserved.

The verified native UI path is character_panel / character_panel_info_holder / lords_and_agents_holder / lord_parent / list_box, populated by CharacterRecruitmentPanelCallback. Buttons match the exact category key or the native localised category label. The lord_parent visibility guard is essential: hero recruitment shares character_panel, so no hiding or simulated lord click occurs while the lord section is hidden. Panel-open population gets bounded delayed refreshes; clicks refresh only while the panel is open for the Moon faction. No continuous polling, character creation, save edits or gameplay stat changes.

## Checks

- Native hierarchy and label IDs read from current ui3.pack character_panel.twui.xml; the source XML is a read-only reference and is not packaged.
- Native get_local_faction_name(true), CharacterRecruitment panel event and UIComponent APIs verified from existing native scripts.
- Lua tests cover exact ID and translated-label fallback, default selection repair, preserving Assault/Bastion and other categories, other-faction boundaries, missing/closed panel and already-open load, and hero-mode safety.
- Packed Lua roundtrip and RPFM diagnostics passed, zero blocking issues.
- v27 added the UI-only script over v26; final v28 adds the lord visibility guard to that script. Every other combined-mod payload is byte-identical. Names, recruitment buildings, hero/lord skills and model fixes remain intact.
- Final active pack mc_moonshadow_heroes_v28_hide_celestial_tab.pack. Previous versions retained disabled; launcher backup and hashes in build/moon-v28-celestial-tab-guard.

The game was not launched and the actual visible tab removal has not been observed. Restart with v28, load the existing campaign and reopen lord recruitment for a live check. Other factions continue to use the native Celestial General category. No new campaign is required by this UI-only patch.

Source: src/script/campaign/mod/mc_moon_hide_celestial_general_tab.lua. Tests: tools/tests/moon-hide-celestial-general-tab.lua. Final build/deploy tools: Hide-Moon-Celestial-Tab-Lord-Guard.py and Deploy-Moon-Celestial-Tab-Guard.py.
