local HOME="mixer_emp_vaults_gigasdongo"
local MOON="cr_cth_agents_of_the_moon"
local LORD="edh_heinrich_cb"
local HERO="edh_sariwa"
local PREFIX="edh_refuge_v1_"
local checks=0
local function expect(value,label) checks=checks+1;assert(value,label) end
local function world()
 local w={saved={edh_east_sea_charter_start_v1=true,edh_sariwa_start_v1_cqi=900},incidents={},moves={},callbacks={},replacement_count=0,third="third",campaign="main_warhammer"}
 local null={is_null_interface=function() return true end}
 w.factions={}
 for i,key in ipairs({HOME,MOON,w.third}) do
  local f={key=key,dead=false,cqi=i,human=key==MOON}
  function f:is_null_interface() return false end
  function f:name() return self.key end
  function f:is_dead() return self.dead end
  function f:is_human() return self.human end
  function f:command_queue_index() return self.cqi end
  function f:has_home_region() return true end
  function f:home_region() return {name=function() return "capital_"..self.key end} end
  function f:character_list()
   local list={}
   for _,c in ipairs(w.characters or {}) do if c.owner==self.key and not c.hidden and not c.off_list then list[#list+1]=c end end
   return {num_items=function() return #list end,item_at=function(_,index) return list[index+1] end}
  end
  w.factions[key]=f
 end
 w.characters={}
 local function add(subtype,cqi,fm)
  local c={subtype=subtype,cqi=cqi,fm=fm,owner=HOME,wounded=false,army=false,hidden=false,xp=4321,rank=11,skills={route=1,attack=2},gear={"sword","talisman"}}
  function c:is_null_interface() return false end
  function c:character_subtype_key() return self.subtype end
  function c:faction() return w.factions[self.owner] end
  function c:command_queue_index() return self.cqi end
  function c:is_wounded() return self.wounded end
  function c:has_military_force() return self.army end
  function c:military_force() return w.army end
  function c:embedded_in_military_force() return self.embedded and w.army or null end
  function c:family_member()
   return {is_null_interface=function() return false end,command_queue_index=function() return self.fm end,
    character=function() return self.hidden and null or self end,
    character_details=function() return {is_null_interface=function() return false end,faction=function() return w.factions[self.owner] end} end}
  end
  w.characters[#w.characters+1]=c;return c
 end
 w.lord=add(LORD,515,525);w.hero=add(HERO,900,901);w.add=add
 w.army={owner=MOON,troops={"jade_warriors","peasant_archers"},faction=function(self) return w.factions[self.owner] end,is_null_interface=function() return false end}
 function w:load()
  self.listeners={};self.callbacks={};cm={};core={}
  function core:add_listener(name,event,condition,callback) w.listeners[name]={event=event,condition=condition,callback=callback} end
  function cm:get_campaign_name() return w.campaign end
  function cm:get_saved_value(key) return w.saved[key] end
  function cm:set_saved_value(key,value) w.saved[key]=value end
  function cm:get_faction(key) return w.factions[key] or null end
  function cm:get_character_by_cqi(cqi)
   for _,c in ipairs(w.characters) do if c.cqi==cqi and not c.hidden then return c end end return false
  end
  function cm:get_family_member_by_cqi(fm)
   for _,c in ipairs(w.characters) do if c.fm==fm then return c:family_member() end end return false
  end
  function cm:add_first_tick_callback(fn) w.first=fn end
  function cm:callback(fn) w.callbacks[#w.callbacks+1]=fn end
  function cm:replace_general_in_force(force,subtype)
   assert(force==w.army and subtype=="wh3_main_cth_lord_magistrate")
   w.replacement_count=w.replacement_count+1;w.lord.army=false
   return {is_null_interface=function() return false end}
  end
  function cm:reassign_character(cqi,target)
   local c
   for _,candidate in ipairs(w.characters) do if candidate.cqi==cqi then c=candidate end end
   assert(c,"unknown character")
   if c==w.hero and w.throw_hero then error("transient engine failure") end
   if c==w.hero and w.fail_hero then return end
   local faction
   for _,f in pairs(w.factions) do if f.cqi==target then faction=f end end
   assert(faction and not faction.dead)
   c.owner=faction.key;c.embedded=false;w.moves[#w.moves+1]={fm=c.fm,to=c.owner}
   w:emit("CharacterFactionChangeEvent",{character=function() return c end})
  end
  function cm:trigger_incident(faction,key) w.incidents[#w.incidents+1]={faction=faction,key=key} end
  function cm:find_valid_spawn_location_for_character_from_settlement() return 200,300 end
  function cm:char_lookup_str(c) return "character_cqi:"..c.cqi end
  function cm:teleport_to() w.teleports=(w.teleports or 0)+1 end
  out=function() end
  dofile("src/script/campaign/mod/edh_east_sea_charter_refuge.lua")
  w.first();w:flush()
 end
 function w:emit(event,context)
  local snapshot={};for _,listener in pairs(self.listeners) do snapshot[#snapshot+1]=listener end
  for _,l in ipairs(snapshot) do if l.event==event and (l.condition==true or l.condition(context)) then l.callback(context) end end
 end
 function w:flush()
  local count=0
  while #self.callbacks>0 do local fn=table.remove(self.callbacks,1);fn();count=count+1;assert(count<100,"recursive scheduling") end
 end
 function w:round() self:emit("WorldStartRound",{});self:flush() end
 function w:die()
  self.factions[HOME].dead=true;self.lord.wounded=true;self.lord.army=false
  self:emit("FactionDeath",{faction=function() return self.factions[HOME] end});self:flush()
 end
 function w:revive()
  self.factions[HOME].dead=false
  self:emit("RegionFactionChangeEvent",{region=function() return {is_null_interface=function() return false end,is_abandoned=function() return false end,owning_faction=function() return self.factions[HOME] end} end});self:flush()
 end
 return w
end
local function progression(w)
 for _,c in ipairs({w.lord,w.hero}) do
  expect(c.xp==4321 and c.rank==11 and c.skills.attack==2 and c.gear[1]=="sword" and c.gear[2]=="talisman","progression/equipment changed")
 end
end
do local w=world();w:load();expect(#w.moves==0 and #w.incidents==0,"premature transfer");w:die();expect(w.lord.owner==MOON and w.hero.owner==MOON,"refuge failed");expect(#w.incidents==1,"arrival event missing");w:round();w:load();expect(#w.incidents==1 and #w.moves==2,"duplicate on reload");w.lord.wounded=false;w.lord.army=true;local troops=w.army.troops;w:revive();expect(w.lord.owner==HOME and w.hero.owner==HOME,"return failed");expect(w.replacement_count==1 and w.army.owner==MOON and w.army.troops==troops,"host army stolen");expect(#w.incidents==2 and w.incidents[2].key=="edh_charter_homecoming","return event missing");w:load();expect(#w.incidents==2,"duplicate return event");progression(w) end
do local w=world();w:load();for i=1,3 do w:die();w:revive() end expect(#w.incidents==6 and #w.moves==12,"repeat cycles failed");progression(w) end
do local w=world();w:load();w.factions[MOON].dead=true;w:die();expect(#w.moves==0 and #w.incidents==0,"dead host revived or used");w.factions[MOON].dead=false;w:round();expect(w.lord.owner==MOON and #w.incidents==1,"host recovery failed") end
do local w=world();w:load();w.fail_hero=true;w:die();expect(w.lord.owner==MOON and w.hero.owner==HOME and #w.incidents==0,"partial commit incorrectly announced");w:load();w.fail_hero=false;w:round();expect(#w.incidents==1 and #w.moves==2,"partial load retry duplicated") end
do local w=world();w:load();w.fail_hero=true;w:die();w:revive();expect(w.lord.owner==HOME and w.hero.owner==HOME and #w.incidents==0,"cancelled refuge announced") end
do local w=world();w:load();w.throw_hero=true;w:die();expect(w.lord.owner==MOON and #w.incidents==0,"exception was not journaled");w.throw_hero=false;w:round();expect(w.hero.owner==MOON and #w.incidents==1,"exception retry failed") end
do local w=world();w:load();w.lord.hidden=true;w.hero.hidden=true;w:die();expect(w.lord.owner==MOON and w.hero.owner==MOON,"archived/wounded family record transfer failed");expect(w.lord.wounded,"recovery timer changed");progression(w) end
do local w=world();w:load();w.lord.owner=w.third;w:die();expect(w.lord.owner==w.third and #w.incidents==0,"stole third faction character") end
do local w=world();w:load();w:die();local duplicate=w.add(LORD,999,999);w:revive();expect(w.lord.owner==HOME and duplicate.owner==HOME and #w.moves==4,"adopted duplicate identity");expect(w.saved[PREFIX..LORD.."_fm"]==525,"original FM overwritten") end
do local w=world();w.saved.edh_east_sea_charter_start_v1=false;w:load();w:die();expect(#w.moves==0,"modified unrelated campaign") end
do local w=world();w.campaign="wh3_main_chaos";w:load();w:die();expect(#w.moves==0,"modified ROC") end
do local w=world();w:load();w.lord.army=true;w.factions[HOME].dead=true;w:round();expect(w.lord.owner==HOME and w.replacement_count==0,"revived dying army");w.lord.wounded=true;w.lord.army=false;w:round();expect(w.lord.owner==MOON,"battle cleanup retry failed") end
do local w=world();w:load();w.hero.embedded=true;w:die();expect(w.hero.owner==MOON and not w.hero.embedded and w.army.owner==MOON,"embedded Hero transfer");progression(w) end
do local w=world();w:load();w:die();w.hero.wounded=true;w:revive();expect(w.hero.wounded and w.replacement_count==0,"wounded return changed recovery");progression(w) end
do local w=world();w.campaign="cr_combi_expanded";w:load();w:die();expect(#w.incidents==1,"IEE alias failed");w.factions[HOME].human=true;w:revive();expect(#w.incidents==3,"human home notification missing") end
print("PASS: "..checks.." refuge assertions; two-way cycles, native identity/progression, host-army preservation, dead/wounded/partial/load/reentrancy guards")
