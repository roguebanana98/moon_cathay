-- Bind only this subtype to the approved appearance, including existing saves.
local SUBTYPE = "mc_assault_general"
local FACTION = "cr_cth_agents_of_the_moon"
local FEMALE_ART = "mc_assault_general_art"
local MALE_ART = "mc_assault_general_art_male"
local applied = {}
local function valid(value) return value and not value:is_null_interface() end
local function supported()
    local campaign = cm:get_campaign_name()
    return campaign == "main_warhammer" or campaign == "cr_combi_expanded"
end
local function wanted(character)
    return supported() and valid(character) and character:character_subtype(SUBTYPE)
        and not character:is_wounded() and valid(character:faction())
        and character:faction():name() == FACTION
end
local function bind(character, refresh)
    if not wanted(character) then return end
    local cqi = character:command_queue_index()
    local art = character:is_male() and MALE_ART or FEMALE_ART
    if applied[cqi] == art and not refresh then return end
    cm:add_character_model_override(character, art)
    applied[cqi] = art
    out("[mc_assault_appearance] Bound " .. tostring(cqi) .. " to " .. art)
end
local function scan(faction)
    if not supported() or not valid(faction) or faction:name() ~= FACTION then return end
    local characters = faction:character_list()
    for i = 0, characters:num_items() - 1 do bind(characters:item_at(i), false) end
end
cm:add_first_tick_callback(function()
    if not supported() then return end
    cm:callback(function() scan(cm:get_faction(FACTION)) end, 0.5)
end)
core:add_listener("mc_assault_appearance_turn", "FactionTurnStart", true,
    function(context) scan(context:faction()) end, true)
for _, event in ipairs({"CharacterCreated", "CharacterFactionChangeEvent",
                       "CharacterConvalescedOrKilled", "CharacterSelected"}) do
    core:add_listener("mc_assault_appearance_" .. event, event,
        function(context) return wanted(context:character()) end,
        function(context)
            local cqi = context:character():command_queue_index()
            applied[cqi] = nil
            cm:callback(function() bind(cm:get_character_by_cqi(cqi), true) end, 0.2)
        end, true)
end
