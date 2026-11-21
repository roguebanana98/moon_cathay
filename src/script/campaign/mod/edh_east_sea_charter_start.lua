-- A separate Empire faction using a landless MIXER slot, never the Moon faction.
-- Engine ownership transfer updates province managers, garrisons and conversion.
local F = "mixer_emp_vaults_gigasdongo"
local MOON = "cr_cth_agents_of_the_moon"
local CAPITAL = "cr_combi_region_dai_loa"
local SECOND = "cr_combi_region_preenn"
local MOON_CAPITAL = "cr_combi_region_long_vi"
local KEY = "edh_east_sea_charter_start_v1"

cm:add_pre_first_tick_callback(function()
    if not cm:is_new_game() or cm:get_saved_value(KEY) then return end
    local campaign = cm:get_campaign_name()
    if campaign ~= "main_warhammer" and campaign ~= "cr_combi_expanded" then return end
    local faction = cm:get_faction(F)
    local moon = cm:get_faction(MOON)
    local capital = cm:get_region(CAPITAL)
    local second = cm:get_region(SECOND)
    local moon_capital = cm:get_region(MOON_CAPITAL)
    local function valid(v) return v and not v:is_null_interface() end
    if not valid(faction) or not valid(moon) or not valid(capital) or
       not valid(second) or not valid(moon_capital) then return end
    -- Do not take over a slot another mod has already activated, or seize cities
    -- reassigned by another start-position setup. Preflight both before mutation.
    if faction:region_list():num_items() ~= 0 or
       faction:subculture() ~= "wh_main_sc_emp_empire" or
       capital:is_abandoned() or second:is_abandoned() or
       capital:owning_faction():name() ~= MOON or
       second:owning_faction():name() ~= MOON or
       moon_capital:is_abandoned() or moon_capital:owning_faction():name() ~= MOON then
        out("[edh_east_sea_charter] Start preconditions failed; territory unchanged")
        return
    end
    local x, y = cm:find_valid_spawn_location_for_character_from_settlement(F, CAPITAL, false, true, 2)
    if not x or not y or x <= 0 or y <= 0 then
        out("[edh_east_sea_charter] No valid starting army location; territory unchanged")
        return
    end
    local commander = nil
    local characters = faction:character_list()
    for i = 0, characters:num_items() - 1 do
        local character = characters:item_at(i)
        if not character:character_subtype("edh_heinrich_cb") or
           not character:has_military_force() or commander then
            out("[edh_east_sea_charter] Slot does not contain its one starting Heinrich; unchanged")
            return
        end
        commander = character
    end
    if not commander then return end
    local lookup = cm:char_lookup_str(commander)
    -- Position the existing, native Empire General before changing any owner.
    if cm:teleport_to(lookup, x, y) == false then return end
    cm:transfer_region_to_faction(CAPITAL, F)
    cm:transfer_region_to_faction(SECOND, F)
    if capital:owning_faction():name() ~= F or second:owning_faction():name() ~= F then
        out("[edh_east_sea_charter] ERROR: engine did not confirm both transfers")
        return
    end
    cm:change_home_region_of_faction(faction, capital)
    cm:change_home_region_of_faction(moon, moon_capital)
    cm:make_diplomacy_available(F, MOON)
    cm:change_character_custom_name(commander, "Heinrich von Adlerhorst", "", "", "")
    cm:set_character_unique(lookup, true)
    cm:set_character_immortality(lookup, true)
    local units = {"wh_main_emp_inf_swordsmen", "wh_main_emp_inf_swordsmen",
        "wh_main_emp_inf_spearmen_1", "wh_main_emp_inf_spearmen_1",
        "wh_main_emp_inf_crossbowmen", "wh_main_emp_inf_crossbowmen"}
    for i = 1, #units do cm:grant_unit_to_character(lookup, units[i]) end
    cm:set_saved_value(KEY, true)
    out("[edh_east_sea_charter] READY: Dai Loa + Preenn; Heinrich faction leader repositioned")
end)

-- This temporary start reward is independent on the map, not embedded in the army.
local HERO_KEY = "edh_sariwa_start_v1_created"
local function spawn_starting_sariwa()
    if not cm:is_new_game() or cm:get_saved_value(HERO_KEY) or not cm:get_saved_value(KEY) then return end
    local faction = cm:get_faction(F)
    if not faction or faction:is_null_interface() or not faction:has_faction_leader() then return end
    local characters = faction:character_list()
    for i = 0, characters:num_items() - 1 do
        if characters:item_at(i):character_subtype("edh_sariwa") then
            cm:set_saved_value(HERO_KEY, true)
            return
        end
    end
    local lord = faction:faction_leader()
    if lord:is_null_interface() or not lord:character_subtype("edh_heinrich_cb") or
       lord:is_wounded() or not lord:has_military_force() then return end
    local x, y = cm:find_valid_spawn_location_for_character_from_position(F,
        lord:logical_position_x(), lord:logical_position_y(), true, 2)
    if not x or not y or x <= 0 or y <= 0 then
        out("[edh_east_sea_charter] ERROR: no valid land beside Heinrich for Sariwa")
        return
    end
    local hero = cm:create_agent(F, "wizard", "edh_sariwa", x, y, true, true)
    if not hero or hero:is_null_interface() then return end
    -- Persist before presentation calls; never create a second or wounded copy.
    cm:set_saved_value(HERO_KEY, true)
    cm:set_saved_value("edh_sariwa_start_v1_cqi", hero:command_queue_index())
    cm:change_character_custom_name(hero, "Sariwa", "", "", "")
    local lookup = cm:char_lookup_str(hero)
    cm:set_character_unique(lookup, true)
    cm:set_character_immortality(lookup, true)
    out("[edh_east_sea_charter] SARIWA READY: independent at " .. tostring(x) .. ", " .. tostring(y))
end
cm:add_first_tick_callback(function()
    if cm:is_new_game() then cm:callback(spawn_starting_sariwa, 0.1) end
end)
