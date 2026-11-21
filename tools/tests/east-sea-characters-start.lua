local F="mixer_emp_vaults_gigasdongo"
local M="cr_cth_agents_of_the_moon"
local D="cr_combi_region_dai_loa"
local P="cr_combi_region_preenn"
local L="cr_combi_region_long_vi"
local KEY="edh_east_sea_charter_start_v1"
local HERO="edh_sariwa_start_v1_created"
local tests=0
local function run(o)
 o=o or {};tests=tests+1
 local saved={};local events={};local before,after;local spawned=0
 if o.initialised then saved[KEY]=true end
 if o.hero_saved then saved[HERO]=true end
 local owners={[D]=o.foreign and "other" or M,[P]=M,[L]=M}
 if o.initialised then owners[D]=F;owners[P]=F end
 local lord={}
 function lord:is_null_interface() return false end
 function lord:character_subtype(k) return not o.wrong_lord and k=="edh_heinrich_cb" end
 function lord:has_military_force() return not o.no_force end
 function lord:is_wounded() return o.wounded_lord or false end
 function lord:logical_position_x() return 300 end
 function lord:logical_position_y() return 400 end
 local hero={}
 function hero:is_null_interface() return false end
 function hero:character_subtype(k) return k=="edh_sariwa" end
 function hero:command_queue_index() return 900 end
 local faction={}
 function faction:is_null_interface() return o.missing_faction or false end
 function faction:subculture() return o.bad_culture and "other" or "wh_main_sc_emp_empire" end
 function faction:region_list() return {num_items=function() return o.occupied and 1 or 0 end} end
 function faction:has_faction_leader() return not o.no_leader end
 function faction:faction_leader() return lord end
 function faction:character_list()
  local list=o.no_lord and {} or {lord}
  if o.existing_hero or spawned>0 then list[#list+1]=hero end
  return {num_items=function() return #list end,item_at=function(_,i) return list[i+1] end}
 end
 local moon={is_null_interface=function() return false end}
 local regions={}
 for _,key in ipairs({D,P,L}) do
  regions[key]={is_null_interface=function() return o.missing_region and key==P end,
    is_abandoned=function() return o.abandoned and key==P end,
    owning_faction=function() return {name=function() return owners[key] end} end}
 end
 cm={}
 function cm:add_pre_first_tick_callback(fn) before=fn end
 function cm:add_first_tick_callback(fn) after=fn end
 function cm:is_new_game() return not o.old_save end
 function cm:get_saved_value(k) return saved[k] end
 function cm:set_saved_value(k,v) saved[k]=v end
 function cm:get_campaign_name() return o.roc and "wh3_main_chaos" or (o.alias or "main_warhammer") end
 function cm:get_faction(k) return k==F and faction or moon end
 function cm:get_region(k) return regions[k] end
 function cm:find_valid_spawn_location_for_character_from_settlement() if o.no_position then return -1,-1 end return 300,400 end
 function cm:find_valid_spawn_location_for_character_from_position(k,x,y,same,distance)
  assert(k==F and x==300 and y==400 and same and distance==2)
  if o.no_hero_position then return -1,-1 end return 302,400
 end
 function cm:char_lookup_str(c) return c==hero and "hero" or "lord" end
 function cm:teleport_to() if o.teleport_fail then return false end events[#events+1]="teleport" end
 function cm:transfer_region_to_faction(k,f) owners[k]=f;events[#events+1]="transfer:"..k end
 function cm:change_home_region_of_faction(f) events[#events+1]=f==faction and "capital:Dai Loa" or "capital:Long Vi" end
 function cm:make_diplomacy_available() events[#events+1]="meet" end
 function cm:change_character_custom_name(c,name) assert(name==(c==hero and "Sariwa" or "Heinrich von Adlerhorst"));events[#events+1]="name:"..name end
 function cm:set_character_immortality(_,v) assert(v);events[#events+1]="immortal" end
 function cm:set_character_unique(_,v) assert(v);events[#events+1]="unique" end
 function cm:grant_unit_to_character() events[#events+1]="unit" end
 function cm:callback(fn) fn() end
 function cm:create_agent(f,agent,subtype,x,y,quiet,no_trait)
  assert(f==F and agent=="wizard" and subtype=="edh_sariwa" and quiet and no_trait and x==302 and y==400)
  if o.create_fail then return false end
  spawned=spawned+1;return hero
 end
 out=function() end
 dofile("src/script/campaign/mod/edh_east_sea_charter_start.lua")
 before();after()
 if o.success then
  assert(saved[KEY] and saved[HERO] and spawned==1 and saved.edh_sariwa_start_v1_cqi==900)
  assert(owners[D]==F and owners[P]==F and owners[L]==M)
  local count=#events;before();after();assert(#events==count and spawned==1,"duplicate initialization")
 elseif o.hero_case then
  assert(spawned==0)
  if o.existing_hero then assert(saved[HERO]) end
 else assert(#events==0 and spawned==0 and not saved[KEY],"failed preflight mutated campaign") end
end
run({success=true});run({success=true,alias="cr_combi_expanded"})
for _,key in ipairs({"old_save","roc","missing_faction","missing_region","occupied","bad_culture","foreign","abandoned","no_position","wrong_lord","no_force","no_lord","teleport_fail"}) do run({[key]=true}) end
for _,key in ipairs({"hero_saved","existing_hero","wounded_lord","no_hero_position","create_fail","no_leader","old_save"}) do run({initialised=true,hero_case=true,[key]=true}) end
print("PASS: "..tests.." cases; exact ownership, named immortal leader, independent Hero, duplicate/wounded/load guards")
