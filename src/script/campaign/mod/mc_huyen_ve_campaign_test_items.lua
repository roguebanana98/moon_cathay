-- Private campaign test loadout, explicitly requested by the user.
-- Run on existing saves as well as new campaigns; save one marker per item.
local items = {
    "mc_huyen_ve_ngoc_boi_nguyet_anh",
    "mc_huyen_ve_giap_son_van_long_vi",
    "mc_huyen_ve_an_tran_thu",
    "mc_huyen_ve_nguyet_dang",
    "mc_huyen_ve_kiem_tran_da"
}

local function grant_test_loadout()
    local faction = cm:get_faction("cr_cth_agents_of_the_moon")
    if not faction or faction:is_null_interface() then return end
    local characters = faction:character_list()
    for i = 0, characters:num_items() - 1 do
        local character = characters:item_at(i)
        if character:character_subtype("mc_moon_warden") then
            for _, item in ipairs(items) do
                local marker = "mc_huyen_ve_campaign_test_v17_" .. item
                if character:has_ancillary(item) then
                    cm:set_saved_value(marker, true)
                elseif not cm:get_saved_value(marker) then
                    cm:force_add_ancillary(character, item, true, true)
                    cm:set_saved_value(marker, true)
                end
            end
            return
        end
    end
end

cm:add_first_tick_callback(function()
    cm:callback(grant_test_loadout, 1)
end)
core:add_listener("mc_huyen_ve_campaign_test_items", "FactionTurnStart",
    function(context) return context:faction():name() == "cr_cth_agents_of_the_moon" end,
    grant_test_loadout, true)
