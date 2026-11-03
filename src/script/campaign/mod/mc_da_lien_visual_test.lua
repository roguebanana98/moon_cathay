-- Private visual test only. Remove this grant path for quest progression.
local faction_key = "cr_cth_agents_of_the_moon"
local subtype = "mc_da_lien"
local region_key = "cr_combi_region_long_vi"
local marker = "mc_da_lien_visual_test_v20_spawned"
local busy = false

local function initialise(character)
    cm:change_character_custom_name(character, "Da Lien", "", "", "")
    cm:set_character_immortality(cm:char_lookup_str(character), true)
end

local function spawn_for_review()
    if cm:get_saved_value("mc_huyen_ve_quests_v25_enabled") then return end
    if busy then return end
    local faction = cm:get_faction(faction_key)
    if not faction or faction:is_null_interface() or not faction:is_human() then return end
    local characters = faction:character_list()
    for i = 0, characters:num_items() - 1 do
        local character = characters:item_at(i)
        if character:character_subtype(subtype) then
            cm:set_saved_value(marker, true)
            initialise(character)
            return
        end
    end
    -- Includes wounded characters: the marker prevents creating another instance.
    if cm:get_saved_value(marker) then return end
    local region = cm:get_region(region_key)
    if not region or region:is_null_interface() or region:owning_faction():name() ~= faction_key then
        out("[mc_da_lien] Waiting for owned Long Vi before visual-test spawn")
        return
    end
    local x, y = cm:find_valid_spawn_location_for_character_from_settlement(faction_key, region_key, false, true)
    if not x or not y or x < 0 or y < 0 then
        out("[mc_da_lien] No valid spawn position near Long Vi; retry next faction turn")
        return
    end
    busy = true
    local character = cm:create_agent(faction_key, "engineer", subtype, x, y, true, true)
    if character and not character:is_null_interface() then
        -- Persist before optional presentation calls so a later error cannot duplicate her.
        cm:set_saved_value(marker, true)
        initialise(character)
        out("[mc_da_lien] Visual-test Hero created near Long Vi")
    end
    busy = false
end

cm:add_first_tick_callback(function() cm:callback(spawn_for_review, 1) end)
core:add_listener("mc_da_lien_visual_test_spawn", "FactionTurnStart",
    function(context) return context:faction():name() == faction_key end,
    spawn_for_review, true)
