local function scenario(opts)
    opts=opts or {}
    local e={created=0,grants=0,level_ups=0,completed=0,queue={},pool=opts.pool or false,valid=opts.valid~=false,existing=opts.existing or false,wounded=opts.wounded or false,rank=opts.rank or 1,saves=0,near=opts.near~=false,owned=opts.owned~=false}
    local hero={}
    function hero:character_subtype(k) return k=="mc_da_lien" end
    function hero:command_queue_index() return 444 end
    function hero:is_null_interface() return false end
    function hero:is_wounded() return e.wounded end
    function hero:rank() return e.rank end
    local lord={is_null_interface=function() return false end,is_wounded=function() return false end,logical_position_x=function() return 100 end,logical_position_y=function() return 200 end}
    local faction={}
    function faction:is_null_interface() return false end
    function faction:ancillary_exists() return e.pool end
    function faction:character_list() return {num_items=function() return e.existing and 1 or 0 end,item_at=function() return hero end} end
    cm={}
    function cm:get_saved_value() return nil end
    function cm:get_faction() return faction end
    function cm:find_valid_spawn_location_for_character_from_position() if e.near and e.valid then return 100,200 end return -1,-1 end
    function cm:get_region() return {is_null_interface=function() return false end,owning_faction=function() return {name=function() return e.owned and "cr_cth_agents_of_the_moon" or "enemy" end} end} end
    function cm:find_valid_spawn_location_for_character_from_settlement() if e.valid then return 300,400 end return -1,-1 end
    function cm:create_agent()
        e.created=e.created+1
        if opts.spawn_fails then return nil end
        e.existing=true
        return hero
    end
    function cm:change_character_custom_name() e.renamed=true end
    function cm:char_lookup_str() return "character_cqi:444" end
    function cm:add_agent_experience(_,amount,by_level) assert(by_level);e.rank=e.rank+amount;e.level_ups=e.level_ups+amount end
    function cm:set_character_immortality() e.immortal=true end
    function cm:force_add_ancillary() e.grants=e.grants+1;if not opts.grant_fails then e.pool=true end end
    function cm:callback(fn) table.insert(e.queue,fn) end
    function cm:set_saved_value() end
    e.s={chapter=2,phase="reward_pending"}
    function e:pulse()
        mc_huyen_ve_quest_rewards.ensure_da_lien(self.s,lord,function()self.saves=self.saves+1 end,function()self.completed=self.completed+1;self.s.chapter=3;self.s.phase="locked" end)
        local q=self.queue;self.queue={};for _,fn in ipairs(q)do fn()end
    end
    dofile("src/script/campaign/mod/mc_huyen_ve_quest_rewards.lua")
    return e
end
local e=scenario();e:pulse();e:pulse()
assert(e.created==1 and e.grants==1 and e.level_ups==4 and e.rank==5 and e.immortal and e.completed==1)
local old=scenario({existing=true,rank=22,pool=true});old:pulse()
assert(old.created==0 and old.grants==0 and old.level_ups==0 and old.rank==22 and not old.renamed and old.completed==1)
local wounded=scenario({existing=true,wounded=true});wounded:pulse()
assert(wounded.created==0 and wounded.grants==0 and wounded.completed==0)
local sea=scenario({near=false});sea:pulse();assert(sea.created==1,"owned Long Vi fallback")
local no_land=scenario({near=false,owned=false});no_land:pulse();assert(no_land.created==0 and no_land.completed==0)
local blocked=scenario({valid=false});blocked:pulse();assert(blocked.created==0 and blocked.completed==0)
local failed=scenario({spawn_fails=true});failed:pulse();assert(failed.created==1 and not failed.s.hero_created_cqi and failed.completed==0)
local absent=scenario();absent.s.hero_created_cqi=444;absent:pulse();assert(absent.created==0,"missing convalescing Hero must not be duplicated")
local locked=scenario();locked.s.phase="active";locked:pulse();assert(locked.created==0 and locked.grants==0,"no reward before confirmed mission success")
local gem_failed=scenario({grant_fails=true});gem_failed:pulse();assert(gem_failed.created==1 and gem_failed.completed==0 and gem_failed.s.phase=="reward_pending")
print("PASS: 10 Da Lien reward-service scenarios (mocked engine)")
