-- ASCII name repair for new campaigns and existing saves. Use the direct-name
-- API so a missing/legacy name localisation key cannot leave the UI blank.
local function repair_huyen_ve_name()
    local faction = cm:get_faction("cr_cth_agents_of_the_moon")
    if not faction or faction:is_null_interface() then return end
    local characters = faction:character_list()
    for i = 0, characters:num_items() - 1 do
        local character = characters:item_at(i)
        local is_huyen_ve = character:character_subtype("mc_moon_warden")
        local is_legacy_leader = character:is_faction_leader()
            and character:get_forename() == "names_name_1376971991"
            and character:get_surname() == "names_name_623106632"
        if is_huyen_ve or is_legacy_leader then
            cm:change_character_custom_name(character,
                "Huyen Ve, Warden of Long Vi", "", "", "")
        end
    end
end

cm:add_first_tick_callback(function()
    repair_huyen_ve_name()
    cm:callback(repair_huyen_ve_name, 0.5)
end)
core:add_listener("mc_huyen_ve_ascii_name_repair", "FactionTurnStart",
    function(context) return context:faction():name() == "cr_cth_agents_of_the_moon" end,
    repair_huyen_ve_name, true)
