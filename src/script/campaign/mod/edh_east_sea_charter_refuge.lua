-- Native character reassignment. Never confederates, revives a faction, creates a
-- replacement Heinrich/Sariwa, resets XP/skills, or copies/equips ancillaries.
local HOME = "mixer_emp_vaults_gigasdongo"
local MOON = "cr_cth_agents_of_the_moon"
local START = "edh_east_sea_charter_start_v1"
local PREFIX = "edh_refuge_v1_"
local TYPES = {"edh_heinrich_cb", "edh_sariwa"}
local busy = false

local function valid(v) return v and not v:is_null_interface() end
local function supported()
    local campaign = cm:get_campaign_name()
    return (campaign == "main_warhammer" or campaign == "cr_combi_expanded") and cm:get_saved_value(START)
end
local function remember(character)
    if not valid(character) then return end
    local subtype = character:character_subtype_key()
    if subtype ~= TYPES[1] and subtype ~= TYPES[2] then return end
    local owner = character:faction():name()
    if owner ~= HOME and owner ~= MOON then return end
    local family = character:family_member()
    if not valid(family) then return end
    local fm = family:command_queue_index()
    local known = cm:get_saved_value(PREFIX .. subtype .. "_fm")
    -- Keep the original persistent identity; never adopt a duplicate of it.
    if known and known ~= fm then return end
    cm:set_saved_value(PREFIX .. subtype .. "_fm", fm)
    cm:set_saved_value(PREFIX .. subtype .. "_cqi", character:command_queue_index())
end
local function resolve(subtype)
    local fm = cm:get_saved_value(PREFIX .. subtype .. "_fm")
    if fm then
        local family = cm:get_family_member_by_cqi(fm)
        if valid(family) then
            local character = family:character()
            if valid(character) and character:character_subtype_key() == subtype then
                remember(character)
                return character
            end
        end
    end
    local cqi = cm:get_saved_value(PREFIX .. subtype .. "_cqi")
    if not cqi and subtype == TYPES[2] then cqi = cm:get_saved_value("edh_sariwa_start_v1_cqi") end
    if cqi then
        local character = cm:get_character_by_cqi(cqi)
        if valid(character) and character:character_subtype_key() == subtype then
            remember(character)
            return character
        end
    end
    for _, key in ipairs({HOME, MOON}) do
        local faction = cm:get_faction(key)
        if valid(faction) then
            local characters = faction:character_list()
            for i = 0, characters:num_items() - 1 do
                local character = characters:item_at(i)
                if character:character_subtype_key() == subtype then
                    remember(character)
                    local recorded = cm:get_saved_value(PREFIX .. subtype .. "_fm")
                    if recorded == character:family_member():command_queue_index() then return character end
                end
            end
        end
    end
    -- A temporarily unavailable wounded record stays pending. Do not recreate it.
end

local function move_original(subtype, destination)
    local character = resolve(subtype)
    if not valid(character) then
        -- Faction death can remove wounded characters from character_list. Their
        -- saved family member still identifies the same character-details record.
        local fm = cm:get_saved_value(PREFIX .. subtype .. "_fm")
        local cqi = cm:get_saved_value(PREFIX .. subtype .. "_cqi")
        local family = fm and cm:get_family_member_by_cqi(fm)
        if not valid(family) or not cqi then return false end
        local details = family:character_details()
        if not valid(details) then return false end
        local owner = details:faction():name()
        if owner == destination:name() then return true end
        local source = destination:name() == HOME and MOON or HOME
        if owner ~= source then return false end
        cm:reassign_character(cqi, destination:command_queue_index())
        -- Confirm through the persistent record even if no map interface exists.
        return family:character_details():faction():name() == destination:name()
    end
    local owner = character:faction():name()
    if owner == destination:name() then
        if subtype == TYPES[2] and not character:is_wounded() then
            local embedded = character:embedded_in_military_force()
            if valid(embedded) and embedded:faction():name() ~= destination:name() then return false end
        end
        return true
    end
    local source = destination:name() == HOME and MOON or HOME
    if owner ~= source then return false end -- Respect third-party confederation/ownership.

    -- Return only Heinrich, not the host faction's army. Raw native replacement
    -- keeps that force and its troops; unlike CUS we do not reassign his items.
    if subtype == TYPES[1] and not character:is_wounded() and character:has_military_force() then
        -- FactionDeath may fire before the defeated army has finished cleanup.
        -- Never create a replacement general in that dying faction/army.
        if source == HOME then return false end
        local force = character:military_force()
        local new_general = cm:replace_general_in_force(force, "wh3_main_cth_lord_magistrate")
        if not valid(new_general) then return false end
        character = resolve(subtype)
        if not valid(character) or character:has_military_force() then return false end
    end

    -- Same family member/character, including convalescing characters. No healing,
    -- kill, rank grants, skill reset, or ancillary inventory reconstruction.
    local cqi = character:command_queue_index()
    cm:reassign_character(cqi, destination:command_queue_index())
    character = resolve(subtype)
    if not valid(character) or character:faction():name() ~= destination:name() then return false end

    -- Independent, active Heroes travel to their new faction. Wounded characters
    -- keep native recovery/pool state; a Lord is recruited through the usual UI.
    if subtype == TYPES[2] and not character:is_wounded() then
        local embedded = character:embedded_in_military_force()
        if valid(embedded) then return false end
        if destination:has_home_region() then
            local x, y = cm:find_valid_spawn_location_for_character_from_settlement(
                destination:name(), destination:home_region():name(), false, true, 3)
            if x and y and x > 0 and y > 0 then cm:teleport_to(cm:char_lookup_str(character), x, y) end
        end
    end
    return true
end

local function process()
    if not supported() then return end
    local home, moon = cm:get_faction(HOME), cm:get_faction(MOON)
    if not valid(home) or not valid(moon) then return end
    -- Cache both identities while they are on-map, before faction-death cleanup.
    for _, subtype in ipairs(TYPES) do resolve(subtype) end
    local phase = cm:get_saved_value(PREFIX .. "phase") or "home"
    local destination
    if home:is_dead() then
        if phase == "home" or phase == "to_home" then
            phase = "to_moon"
            cm:set_saved_value(PREFIX .. "phase", phase)
        end
        if phase == "moon" or moon:is_dead() then return end
        destination = moon
    else
        if phase == "home" then return end
        if phase ~= "to_home" then
            phase = "to_home"
            cm:set_saved_value(PREFIX .. "phase", phase)
        end
        destination = home
    end
    local complete = true
    for _, subtype in ipairs(TYPES) do
        -- Do not short-circuit: either character can transfer while the other is
        -- temporarily unavailable. The journal is completed only after both.
        if not move_original(subtype, destination) then complete = false end
    end
    if not complete then return end
    local returning = destination:name() == HOME
    cm:set_saved_value(PREFIX .. "phase", returning and "home" or "moon")
    local notify = not returning or cm:get_saved_value(PREFIX .. "refuge_announced")
    cm:set_saved_value(PREFIX .. "refuge_announced", not returning)
    if not notify then return end -- Revival cancelled an incomplete refuge transfer.
    local incident = returning and "edh_charter_homecoming" or "edh_charter_moon_sanctuary"
    cm:trigger_incident(MOON, incident, true)
    if returning and home:is_human() then cm:trigger_incident(HOME, incident, true) end
    out("[edh_refuge] " .. (returning and "RETURNED HOME" or "JOINED MOON") .. ": both original characters confirmed")
end
local function reconcile()
    if busy then return end
    busy = true
    local ok, err = pcall(process)
    busy = false
    if not ok then out("[edh_refuge] Transfer remains pending: " .. tostring(err)) end
end
local function deferred() cm:callback(reconcile, 0.5) end

cm:add_first_tick_callback(function() cm:callback(reconcile, 0.2) end)
core:add_listener("edh_refuge_death", "FactionDeath",
    function(context) return context:faction():name() == HOME end,
    function() reconcile(); deferred() end, true)
core:add_listener("edh_refuge_turn", "FactionTurnStart",
    function(context) return context:faction():name() == HOME or context:faction():name() == MOON end,
    reconcile, true)
core:add_listener("edh_refuge_round", "WorldStartRound", true, reconcile, true)
core:add_listener("edh_refuge_region", "RegionFactionChangeEvent",
    function(context)
        local region = context:region()
        return valid(region) and not region:is_abandoned() and region:owning_faction():name() == HOME
    end,
    deferred, true)
core:add_listener("edh_refuge_liberated", "FactionLiberated", true, deferred, true)
for _, event in ipairs({"CharacterCreated", "CharacterConvalescedOrKilled", "CharacterFactionChangeEvent"}) do
    core:add_listener("edh_refuge_" .. event, event,
        function(context)
            local character = context:character()
            return valid(character) and (character:character_subtype_key() == TYPES[1] or character:character_subtype_key() == TYPES[2])
        end,
        function(context) remember(context:character()); deferred() end, true)
end
