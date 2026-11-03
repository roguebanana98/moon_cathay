-- New-campaign placement only. Move the existing commander/army before normal
-- first-tick scripts and camera setup; never recreate units or edit a live save.
local F="cr_cth_agents_of_the_moon"
local R="cr_combi_region_long_vi"
local KEY="mc_huyen_ve_long_vi_start_v25"
cm:add_pre_first_tick_callback(function()
    if not cm:is_new_game() or cm:get_saved_value(KEY) then return end
    local campaign=cm:get_campaign_name()
    if campaign~="main_warhammer" and campaign~="cr_combi_expanded" then return end
    local f=cm:get_faction(F)
    local region=cm:get_region(R)
    if not f or f:is_null_interface() or
       not region or region:is_null_interface() or region:is_abandoned() or
       region:owning_faction():name()~=F then return end
    local chars=f:character_list()
    for i=0,chars:num_items()-1 do
        local c=chars:item_at(i)
        if c:character_subtype("mc_moon_warden") and not c:is_wounded() and c:has_military_force() then
            if c:has_region() and c:region():name()==R then
                cm:set_saved_value(KEY,true)
                return
            end
            local x,y=cm:find_valid_spawn_location_for_character_from_settlement(F,R,false,true,2)
            if not x or not y or x<=0 or y<=0 then
                out("[mc_huyen_ve_start] No valid land position at Long Vi; starting army unchanged")
                return
            end
            if cm:teleport_to(cm:char_lookup_str(c),x,y)~=false then
                cm:set_saved_value(KEY,true)
                out("[mc_huyen_ve_start] Existing Huyen Ve army placed at Long Vi: "..x..", "..y)
            end
            return
        end
    end
end)
