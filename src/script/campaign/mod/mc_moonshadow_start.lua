-- Da Anh is a new-campaign reward; loading an older save never creates a copy.
local F = "cr_cth_agents_of_the_moon"
local S = "mc_da_anh"
local KEY = "mc_da_anh_start_v1_created"

local function spawn()
    if not cm:is_new_game() or cm:get_saved_value(KEY) then return end
    local campaign = cm:get_campaign_name()
    if campaign ~= "main_warhammer" and campaign ~= "cr_combi_expanded" then return end
    local faction = cm:get_faction(F)
    if not faction or faction:is_null_interface() then return end
    local lord
    local chars = faction:character_list()
    for i = 0, chars:num_items() - 1 do
        local c = chars:item_at(i)
        -- Wounded characters count too: never replace an existing Da Anh.
        if c:character_subtype(S) then cm:set_saved_value(KEY, true); return end
        if c:character_subtype("mc_moon_warden") and not c:is_wounded() and
           c:has_military_force() then lord = c end
    end
    if not lord then return end
    local x, y = cm:find_valid_spawn_location_for_character_from_position(F,
        lord:logical_position_x(), lord:logical_position_y(), true, 2)
    if not x or not y or x <= 0 or y <= 0 then
        out("[mc_moonshadow] No valid land beside Huyen Ve; Da Anh not created")
        return
    end
    local hero = cm:create_agent(F, "spy", S, x, y, true, true)
    if not hero or hero:is_null_interface() then return end
    -- Persist immediately, before presentation calls, to prevent duplicates.
    cm:set_saved_value(KEY, true)
    cm:set_saved_value("mc_da_anh_start_v1_cqi", hero:command_queue_index())
    cm:change_character_custom_name(hero, "Da Anh, The Moon's Hidden Blade", "", "", "")
    local lookup = cm:char_lookup_str(hero)
    cm:set_character_unique(lookup, true)
    cm:set_character_immortality(lookup, true)
    out("[mc_moonshadow] Da Anh ready beside Huyen Ve")
end

cm:add_first_tick_callback(function()
    if cm:is_new_game() then
        -- Existing pre-first-tick placement has already moved Huyen Ve to Long Vi.
        cm:callback(spawn, 0.2)
        cm:callback(spawn, 1)
    end
end)
