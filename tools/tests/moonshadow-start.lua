local F="cr_cth_agents_of_the_moon"
local KEY="mc_da_anh_start_v1_created"
local cases=0
local function run(o)
    o=o or {};cases=cases+1
    local saved={};local spawned=0;local initial;local calls={};local attempts=0
    if o.saved then saved[KEY]=true end
    local lord={}
    function lord:character_subtype(s) return s=="mc_moon_warden" and not o.wrong_lord end
    function lord:is_wounded() return o.wounded_lord end
    function lord:has_military_force() return not o.no_force end
    function lord:logical_position_x() return 300 end
    function lord:logical_position_y() return 400 end
    local hero={}
    function hero:character_subtype(s) return s=="mc_da_anh" end
    function hero:is_null_interface() return o.null_creation or false end
    function hero:command_queue_index() return 900 end
    local faction={}
    function faction:is_null_interface() return o.null_faction end
    function faction:character_list()
        local list=o.no_lord and {} or {lord}
        if o.existing or spawned>0 then list[#list+1]=hero end
        return {num_items=function() return #list end,item_at=function(_,i) return list[i+1] end}
    end
    cm={}
    function cm:add_first_tick_callback(fn) initial=fn end
    function cm:is_new_game() return not o.old_save end
    function cm:get_saved_value(k) return saved[k] end
    function cm:set_saved_value(k,v) saved[k]=v end
    function cm:get_campaign_name() return o.roc and "wh3_main_chaos" or (o.alias or "main_warhammer") end
    function cm:get_faction(k) assert(k==F);if o.missing_faction then return nil end return faction end
    function cm:callback(fn) calls[#calls+1]=fn end
    function cm:find_valid_spawn_location_for_character_from_position(f,x,y,land,radius)
        assert(f==F and x==300 and y==400 and land and radius==2)
        attempts=attempts+1
        if o.no_position or (o.transient_position and attempts==1) then return -1,-1 end
        return 302,400
    end
    function cm:create_agent(f,agent,subtype,x,y,quiet,no_trait)
        assert(f==F and agent=="spy" and subtype=="mc_da_anh" and x==302 and y==400 and quiet and no_trait)
        if o.failed_creation then return nil end
        if o.null_creation then return hero end
        spawned=spawned+1;return hero
    end
    function cm:change_character_custom_name(c,name)
        assert(saved[KEY] and saved.mc_da_anh_start_v1_cqi==900 and c==hero)
        assert(name=="Da Anh, The Moon's Hidden Blade")
        if o.name_error then error("presentation failure") end
    end
    function cm:char_lookup_str(c) assert(c==hero);return "character_cqi:900" end
    local unique,immortal=false,false
    function cm:set_character_unique(k,v) assert(k=="character_cqi:900" and v);unique=true end
    function cm:set_character_immortality(k,v) assert(k=="character_cqi:900" and v);immortal=true end
    out=function() end
    dofile("src/script/campaign/mod/mc_moonshadow_start.lua")
    initial()
    for _,fn in ipairs(calls) do pcall(fn) end
    if o.success then
        assert(spawned==1 and unique and immortal and saved[KEY])
    elseif o.name_error then assert(spawned==1 and saved[KEY])
    else assert(spawned==0) end
    local before=spawned
    -- Repeated callbacks and reloading old saves must not create a second hero.
    for _,fn in ipairs(calls) do pcall(fn) end
    assert(spawned==before)
    if o.existing then assert(saved[KEY]) end
    o.old_save=true;initial();assert(spawned==before)
end
run({success=true});run({success=true,alias="cr_combi_expanded"})
run({success=true,transient_position=true})
for _,key in ipairs({"old_save","roc","missing_faction","null_faction","no_lord","wrong_lord",
                    "wounded_lord","no_force","saved","existing","no_position","failed_creation","null_creation","name_error"}) do
    run({[key]=true})
end
print("PASS: "..cases.." Moonshadow spawn scenarios; duplicate, wounded, load, invalid location and creation guards")
