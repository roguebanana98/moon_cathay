-- Boundary tests run in a standalone Lua runtime, never attached to the game.
local F="mixer_emp_vaults_gigasdongo"
local M="cr_cth_agents_of_the_moon"
local D="cr_combi_region_dai_loa"
local P="cr_combi_region_preenn"
local L="cr_combi_region_long_vi"
local function run(options)
    local o=options or {};local events={};local done=false;local callback
    local owners={[D]=o.foreign and "foreign" or M,[P]=M,[L]=M}
    local f={}
    function f:is_null_interface() return o.missing_faction or false end
    function f:subculture() return o.bad_culture and "other" or "wh_main_sc_emp_empire" end
    function f:region_list() return {num_items=function() return o.occupied and 1 or 0 end} end
    function f:character_list()
        return {num_items=function() return o.no_commander and 0 or 1 end,item_at=function() return {character_subtype=function(_,key) return not o.non_dummy and key=="wh_main_emp_lord" end,has_military_force=function() return not o.no_force end} end}
    end
    local moon={is_null_interface=function() return false end}
    local regions={}
    for _,key in ipairs({D,P,L}) do
        local r={}
        function r:is_null_interface() return o.missing_region and key==P end
        function r:is_abandoned() return o.abandoned and key==P end
        function r:owning_faction() return {name=function() return owners[key] end} end
        regions[key]=r
    end
    cm={}
    function cm:add_pre_first_tick_callback(fn) callback=fn end
    function cm:is_new_game() return not o.old_save end
    function cm:get_saved_value() return o.already_done or done end
    function cm:get_campaign_name() return o.roc and "wh3_main_chaos" or (o.alias or "main_warhammer") end
    function cm:get_faction(key) return key==F and f or moon end
    function cm:get_region(key) return regions[key] end
    function cm:find_valid_spawn_location_for_character_from_settlement() if o.no_position then return -1,-1 end return 300,400 end
    function cm:char_lookup_str() return "character_cqi:123" end
    function cm:teleport_to() if o.teleport_fail then return false end events[#events+1]="teleport" end
    function cm:transfer_region_to_faction(key,target) owners[key]=target;events[#events+1]="transfer:"..key end
    function cm:change_home_region_of_faction(faction,region) events[#events+1]=faction==f and "capital:Dai Loa" or "capital:Long Vi" end
    function cm:make_diplomacy_available() events[#events+1]="meet" end
    function cm:change_character_custom_name() events[#events+1]="name" end
    function cm:set_character_immortality() events[#events+1]="mortal" end
    function cm:grant_unit_to_character() events[#events+1]="unit" end
    function cm:set_saved_value(_,value) done=value end
    out=function() end
    dofile("src/script/campaign/mod/edh_east_sea_charter_start.lua")
    callback()
    if o.expect_success then
        assert(done and owners[D]==F and owners[P]==F and owners[L]==M)
        assert(table.concat(events,",")=="teleport,transfer:"..D..",transfer:"..P..",capital:Dai Loa,capital:Long Vi,meet,name,mortal,unit,unit,unit,unit,unit,unit")
        local count=#events;callback();assert(#events==count,"repeated initialization")
    else assert(#events==0 and not done,"preflight mutated state") end
end
run({expect_success=true});run({expect_success=true,alias="cr_combi_expanded"})
for _,key in ipairs({"old_save","already_done","roc","missing_faction","missing_region","occupied","bad_culture","foreign","abandoned","no_position","non_dummy","no_force","no_commander","teleport_fail"}) do run({[key]=true}) end
print("PASS: 16 campaign boundaries, exact two-region transfer, capitals, native army and repeat guard")
