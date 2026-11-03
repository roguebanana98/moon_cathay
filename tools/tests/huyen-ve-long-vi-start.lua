-- Protect existing saves and move the real army only at new-campaign creation.
local count=0
local function run(options)
    local moved,marker,callback=0,false,nil
    local c={character_subtype=function(_,key)return key=="mc_moon_warden" end,
        is_wounded=function()return false end,has_military_force=function()return true end,
        has_region=function()return true end,region=function()return {name=function()return options.already and "cr_combi_region_long_vi" or "cr_combi_region_dai_loa" end} end}
    local f={is_null_interface=function()return false end,is_human=function()return options.human~=false end,
        name=function()return "cr_cth_agents_of_the_moon" end,
        character_list=function()return {num_items=function()return 1 end,item_at=function()return c end} end}
    cm={add_pre_first_tick_callback=function(_,fn)callback=fn end,
        is_new_game=function()return options.new~=false end,get_saved_value=function()return options.marker end,
        get_campaign_name=function()return options.campaign or "main_warhammer" end,
        get_faction=function()return f end,
        get_region=function()return {is_null_interface=function()return false end,is_abandoned=function()return false end,
            owning_faction=function()return {name=function()return options.enemy and "enemy" or f:name() end} end} end,
        find_valid_spawn_location_for_character_from_settlement=function(_,faction,region,sea,land,radius)
            assert(faction==f:name() and region=="cr_combi_region_long_vi" and sea==false and land==true and radius==2)
            if options.blocked then return -1,-1 end;return 1407,281 end,
        char_lookup_str=function(_,character)assert(character==c);return "character_cqi:329" end,
        teleport_to=function(_,lookup,x,y)assert(lookup=="character_cqi:329" and x==1407 and y==281);moved=moved+1;return not options.failed end,
        set_saved_value=function(_,key,value)assert(key=="mc_huyen_ve_long_vi_start_v25");marker=value end}
    out=function()end
    dofile("src/script/campaign/mod/mc_huyen_ve_start_at_long_vi.lua");assert(callback);callback()
    count=count+1;return moved,marker
end
local moved,marker=run({});assert(moved==1 and marker)
for _,o in ipairs({{new=false},{marker=true},{campaign="wh3_main_chaos"},{enemy=true},{blocked=true}}) do
    moved,marker=run(o);assert(moved==0 and not marker)
end
moved,marker=run({already=true});assert(moved==0 and marker)
moved,marker=run({failed=true});assert(moved==1 and not marker)
moved,marker=run({campaign="cr_combi_expanded"});assert(moved==1 and marker)
moved,marker=run({human=false});assert(moved==1 and marker)
print("Long Vi new-campaign placement checks passed: "..count)
