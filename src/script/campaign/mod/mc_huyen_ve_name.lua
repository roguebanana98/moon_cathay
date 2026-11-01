-- Apply the authored identity on both new campaigns and loaded saves.
-- Keep the full name in one component so culture-specific ordering cannot reverse it.
cm:add_first_tick_callback(function()
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
            cm:change_character_localised_name(character,
                "names_name_mc_moon_warden", "", "", "")
        end
    end
end)
