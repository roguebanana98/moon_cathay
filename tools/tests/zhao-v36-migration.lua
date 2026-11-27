-- Boundary tests for scope, one-time reset, traits, item and immortality policy.
-- These tests do not emulate native skill refunds or prove game runtime safety.
local saved, listeners, callbacks, roster = {}, {}, {}, {}
local resets, removals, grants = 0, 0, 0
local function char(id, sub, faction, skills, item)
    local c = {id=id, sub=sub, faction_key=faction, skills=skills or {}, seal=item,
        xp=1234, trait="fleet_footed", immutable_identity="Zhao-" .. id}
    function c:is_null_interface() return false end
    function c:character_subtype(s) return self.sub == s end
    function c:faction() return {name=function() return self.faction_key end} end
    function c:command_queue_index() return self.id end
    function c:rank() return self.level or 1 end
    function c:has_skill(s) return (self.skills[s] or 0) > 0 end
    function c:has_ancillary(s) return s=="mc_mooncourt_lord_command_seal" and self.seal end
    return c
end
local function lookup(c) return "character_cqi:" .. c.id end
local function find(k) for _,c in ipairs(roster) do if lookup(c)==k then return c end end; error(k) end
cm={}
function cm:char_lookup_str(c) return lookup(c) end
function cm:get_saved_value(k) return saved[k] end
function cm:set_saved_value(k,v) saved[k]=v end
function cm:force_reset_skills(k)
    resets=resets+1
    local c=find(k)
    -- An intentionally surviving hidden legacy grant exercises cleanup.
    c.skills={mc_mooncourt_lord_moon_skill_14=1,wh3_main_skill_innate_cth_fleet_footed=1}
end
function cm:remove_skill_point(k,s) local c=find(k); c.skills[s]=math.max(0,(c.skills[s] or 0)-1); removals=removals+1; return true end
function cm:add_skill(k,s) local c=find(k); c.skills[s]=(c.skills[s] or 0)+1;grants=grants+1 end
function cm:force_remove_ancillary(c,s,pool,suppress) assert(s=="mc_mooncourt_lord_command_seal" and not pool and suppress);c.seal=false end
function cm:set_character_immortality(k,v) find(k).immortal=v end
function cm:add_first_tick_callback(f) callbacks[#callbacks+1]=f end
function cm:callback(f,_) f() end
local faction={}
function faction:name() return "cr_cth_agents_of_the_moon" end
function faction:is_null_interface() return false end
function faction:character_list() return {num_items=function() return #roster end,item_at=function(_,i) return roster[i+1] end} end
function cm:get_faction(k) assert(k==faction:name());return faction end
core={}
function core:add_listener(k,event,condition,action,persistent) assert(persistent);listeners[k]={event=event,condition=condition,action=action} end
function out(_) end
roster={char(1,"mc_mooncourt_lord",faction:name(),{mc_mooncourt_lord_moon_skill_3=2},true),
    char(2,"mc_mooncourt_lord",faction:name(),{mc_zhao_v36_foundation=1},false),
    char(3,"mc_moonveil_adept",faction:name(),{mc_mooncourt_lord_moon_skill_3=1},true),
    char(4,"mc_mooncourt_lord","another_faction",{mc_mooncourt_lord_moon_skill_3=1},true)}
dofile("build/moon-v36-zhao-jade/script/campaign/mod/mc_zhao_v36_migration.lua")
for _,f in ipairs(callbacks) do f() end
assert(resets==1 and removals==1 and grants==1)
assert(roster[1]:has_skill("mc_zhao_v36_foundation") and not roster[1].seal and not roster[1].immortal)
assert(roster[1].xp==1234 and roster[1].trait=="fleet_footed" and roster[1].immutable_identity=="Zhao-1")
assert(roster[1]:has_skill("wh3_main_skill_innate_cth_fleet_footed"))
assert(roster[3].seal and roster[4].seal and not roster[3].immortal and not roster[4].immortal)
local turn=listeners.mc_zhao_v36_turn;local context={faction=function() return faction end};assert(turn.condition(context));turn.action(context)
assert(resets==1 and removals==1 and grants==1)
roster[1].skills.wh2_main_skill_all_immortality_lord=1
local skill=listeners.mc_zhao_v36_immortality_skill
local ctx={skill_point_spent_on=function() return "wh2_main_skill_all_immortality_lord" end};assert(skill.condition(ctx));skill.action(ctx);assert(roster[1].immortal)
assert(not skill.condition({skill_point_spent_on=function() return "some_other_skill" end}))
assert(roster[3].seal and roster[4].seal and not roster[3].immortal and not roster[4].immortal)
roster[#roster+1]=char(5,"mc_mooncourt_lord",faction:name(),{},false)
local created=listeners.mc_zhao_v36_CharacterCreated
assert(created.condition({character=function() return roster[5] end}));created.action({})
assert(resets==1 and grants==2 and roster[5]:has_skill("mc_zhao_v36_foundation"))
turn.action(context);assert(resets==1 and grants==2)
roster[1].level=15;turn.action(context)
assert(roster[1]:has_skill("mc_zhao_v36_mount_warhorse") and roster[1]:has_skill("mc_zhao_v36_mount_jade_longma"))
assert(resets==1 and grants==4);turn.action(context);assert(grants==4)
assert(not turn.condition({faction=function() return {name=function() return "another_faction" end} end}))
print("Zhao v36 migration scope/idempotence/traits/item/immortality boundaries passed")
