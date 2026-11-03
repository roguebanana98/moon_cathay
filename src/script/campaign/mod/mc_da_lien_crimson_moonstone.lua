-- Signature item: one grant for new or existing Da Lien, never repeated equip.
local faction_key = "cr_cth_agents_of_the_moon"
local item = "mc_da_lien_crimson_moonstone"
local marker = "mc_da_lien_crimson_moonstone_v24_granted"
local busy = false

local function grant_moonstone()
    if cm:get_saved_value("mc_huyen_ve_quests_v25_enabled") then return end
    if busy or cm:get_saved_value(marker) then return end
    local faction = cm:get_faction(faction_key)
    if not faction or faction:is_null_interface() or not faction:is_human() then return end
    -- Also recognises an unequipped item. Do not issue another or override the
    -- player's equipment choice after loading a save with the gem in the pool.
    if faction:ancillary_exists(item) then
        cm:set_saved_value(marker, true)
        return
    end
    local characters = faction:character_list()
    for i = 0, characters:num_items() - 1 do
        local character = characters:item_at(i)
        if character:character_subtype("mc_da_lien") and not character:is_wounded() then
            busy = true
            cm:force_add_ancillary(character, item, true, true)
            -- Confirm the grant before persisting the marker. An unsuccessful
            -- grant retries next faction turn, without creating another Hero.
            cm:callback(function()
                busy = false
                local current = cm:get_faction(faction_key)
                if current and not current:is_null_interface() and current:ancillary_exists(item) then
                    cm:set_saved_value(marker, true)
                    out("[mc_da_lien] Crimson Moonstone granted")
                else
                    out("[mc_da_lien] Crimson Moonstone grant unconfirmed; retry next turn")
                end
            end, 1)
            return
        end
    end
end

-- v20 spawn runs at one second; v23 skill migration runs at two seconds.
cm:add_first_tick_callback(function() cm:callback(grant_moonstone, 3) end)
core:add_listener("mc_da_lien_crimson_moonstone_grant", "FactionTurnStart",
    function(context) return context:faction():name() == faction_key end,
    function() cm:callback(grant_moonstone, 3) end, true)
