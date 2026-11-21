-- The registered MIXER/IEE slot already exists in frontend and campaign startpos.
-- Enable only its original frontend character ID; never rewrite global helpers.
local FACTION = "mixer_emp_vaults_gigasdongo"
local STARTPOS_ID = "186992224"
local function enable_charter()
    if type(mixer_enable_custom_faction) ~= "function" then
        out("[edh_charter_frontend] MIXER frontend library unavailable")
        return
    end
    if mixer_factions_that_require_other_mods[STARTPOS_ID] == FACTION then
        mixer_enable_custom_faction(STARTPOS_ID)
    end
    mixer_add_faction_to_major_faction_list(FACTION)
    mixer_change_lord_name(STARTPOS_ID, "edh_heinrich_cb")
    mixer_add_starting_unit_list_for_faction(FACTION, {
        "wh_main_emp_inf_swordsmen", "wh_main_emp_inf_spearmen_1",
        "wh_main_emp_inf_crossbowmen"
    })
end
enable_charter()
core:add_ui_created_callback(enable_charter)
