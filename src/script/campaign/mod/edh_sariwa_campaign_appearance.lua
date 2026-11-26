-- Explicit campaign model binding also repairs existing Sariwa instances on load.
-- The battle model and character progression are not modified.
local SUBTYPE = "edh_sariwa"
local ART = "edh_sariwa_art"
local applied = {}
local function supported()
    local key = cm:get_campaign_name()
    return key == "main_warhammer" or key == "cr_combi_expanded"
end
local function valid(value) return value and not value:is_null_interface() end
local function bind(character, refresh)
    if not supported() or not valid(character) or
       not character:character_subtype(SUBTYPE) or character:is_wounded() then return end
    local cqi = character:command_queue_index()
    if applied[cqi] and not refresh then return end
    cm:add_character_model_override(character, ART)
    applied[cqi] = true
    out("[edh_sariwa_appearance] Bound original character " .. tostring(cqi) .. " to " .. ART)
end
local function scan(faction)
    if not supported() or not valid(faction) then return end
    local characters = faction:character_list()
    for i = 0, characters:num_items() - 1 do bind(characters:item_at(i), false) end
end
cm:add_first_tick_callback(function()
    if not supported() then return end
    -- No new-game-only guard: overrides are session-local and old saves need it.
    cm:callback(function()
        local factions = cm:model():world():faction_list()
        for i = 0, factions:num_items() - 1 do scan(factions:item_at(i)) end
    end, 0.3)
end)
core:add_listener("edh_sariwa_appearance_turn", "FactionTurnStart", true,
    function(context) scan(context:faction()) end, true)
for _, event in ipairs({"CharacterCreated", "CharacterFactionChangeEvent", "CharacterConvalescedOrKilled"}) do
    core:add_listener("edh_sariwa_appearance_" .. event, event,
        function(context)
            local character = context:character()
            return supported() and valid(character) and character:character_subtype(SUBTYPE)
        end,
        function(context)
            local cqi = context:character():command_queue_index()
            applied[cqi] = nil
            cm:callback(function() bind(cm:get_character_by_cqi(cqi), true) end, 0.1)
        end, true)
end
