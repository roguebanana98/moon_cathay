local listeners, ticks, queue, calls = {}, {}, {}, {}
local campaign = "cr_combi_expanded"
local function list(items) return {num_items=function() return #items end,item_at=function(_,i) return items[i+1] end} end
local home = {name=function() return "cr_cth_agents_of_the_moon" end,is_null_interface=function() return false end}
local away = {name=function() return "wh3_main_cth_the_northern_provinces" end,is_null_interface=function() return false end}
local function char(id, subtype, male, wounded, faction)
    return {id=id,subtype=subtype,male=male,wounded=wounded,owner=faction or home,xp=1234,skills="original",gear="original",
        is_null_interface=function() return false end,character_subtype=function(self,k) return self.subtype==k end,
        is_wounded=function(self) return self.wounded end,is_male=function(self) return self.male end,
        faction=function(self) return self.owner end,command_queue_index=function(self) return self.id end}
end
local male=char(10,"mc_assault_general",true,false)
local female=char(11,"mc_assault_general",false,false)
local other=char(12,"mc_bastion_general",true,false)
local wounded=char(13,"mc_assault_general",true,true)
local transferred=char(14,"mc_assault_general",true,false,away)
local people={male,female,other,wounded,transferred};local by_id={}
for _,c in ipairs(people) do by_id[c.id]=c end
home.character_list=function() return list(people) end
cm={get_campaign_name=function() return campaign end,
    is_new_game=function() error("Existing-save repair cannot depend on new-game status") end,
    add_first_tick_callback=function(_,f) ticks[#ticks+1]=f end,
    callback=function(_,f) queue[#queue+1]=f end,
    get_faction=function(_,key) assert(key==home:name());return home end,
    get_character_by_cqi=function(_,id) return by_id[id] end,
    add_character_model_override=function(_,c,art)
        assert(c.subtype=="mc_assault_general" and c.owner==home and not c.wounded)
        assert(art==(c.male and "mc_assault_general_art_male" or "mc_assault_general_art"))
        calls[#calls+1]={c,art}
    end}
core={add_listener=function(_,name,event,condition,action) listeners[event]={condition,action} end}
out=function() end
local function flush() local q=queue;queue={};for _,f in ipairs(q) do f() end end
local function emit(event,c)
    local l=listeners[event];local ctx={character=function() return c end,faction=function() return home end}
    if l[1]==true or l[1](ctx) then l[2](ctx) end;flush()
end
local function load()
    ticks={};listeners={};dofile("src/script/campaign/mod/mc_assault_campaign_appearance.lua")
    for _,f in ipairs(ticks) do f() end;flush()
end
load();assert(#calls==2 and calls[1][1]==male and calls[2][1]==female)
emit("FactionTurnStart");assert(#calls==2)
emit("CharacterCreated",other);assert(#calls==2)
emit("CharacterCreated",transferred);assert(#calls==2)
local newborn=char(15,"mc_assault_general",true,false);people[#people+1]=newborn;by_id[15]=newborn
emit("CharacterCreated",newborn);assert(#calls==3)
emit("CharacterSelected",male);assert(#calls==4) -- Repairs a later/stale override.
wounded.wounded=false;emit("FactionTurnStart");assert(#calls==5)
male.wounded=true;emit("CharacterConvalescedOrKilled",male);assert(#calls==5)
male.wounded=false;emit("CharacterConvalescedOrKilled",male);assert(#calls==6)
transferred.owner=home;emit("CharacterFactionChangeEvent",transferred);assert(#calls==7)
load();assert(#calls==12) -- Every applicable existing character rebound on load.
assert(male.xp==1234 and male.skills=="original" and male.gear=="original" and #people==6)
campaign="main_warhammer";load();assert(#calls==17)
campaign="wh3_main_chaos";load();assert(#calls==17)
print("PASS: existing/new male/female Assault, selection refresh, recovery, faction/campaign boundaries; original progression and character identity preserved")
