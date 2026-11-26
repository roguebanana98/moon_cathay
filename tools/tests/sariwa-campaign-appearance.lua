local listeners, ticks, queue, calls = {}, {}, {}, {}
local campaign = "main_warhammer"
local function list(items) return {num_items=function() return #items end,item_at=function(_,i) return items[i+1] end} end
local function char(cqi, subtype, wounded)
    return {id=cqi,subtype=subtype,wounded=wounded,xp=1234,skills="original",gear="original",
        is_null_interface=function() return false end,
        character_subtype=function(self,k) return self.subtype==k end,
        is_wounded=function(self) return self.wounded end,
        command_queue_index=function(self) return self.id end}
end
local original=char(10,"edh_sariwa",false)
local other=char(11,"edh_heinrich_cb",false)
local wounded=char(12,"edh_sariwa",true)
local people={original,other,wounded};local by_id={[10]=original,[11]=other,[12]=wounded}
local home={is_null_interface=function() return false end,character_list=function() return list(people) end}
cm={get_campaign_name=function() return campaign end,
    is_new_game=function() error("Existing-save repair must not depend on new-game status") end,
    add_first_tick_callback=function(_,f) ticks[#ticks+1]=f end,
    callback=function(_,f) queue[#queue+1]=f end,
    model=function() return {world=function() return {faction_list=function() return list({home}) end} end} end,
    get_character_by_cqi=function(_,id) return by_id[id] end,
    add_character_model_override=function(_,c,art)
        assert(c.subtype=="edh_sariwa" and art=="edh_sariwa_art")
        calls[#calls+1]=c
    end}
core={add_listener=function(_,name,event,condition,action) listeners[event]={condition,action} end}
out=function() end
local function flush() local pending=queue;queue={};for _,f in ipairs(pending) do f() end end
local function emit(event,c)
    local l=listeners[event];local ctx={character=function() return c end,faction=function() return home end}
    if l[1]==true or l[1](ctx) then l[2](ctx) end
    flush()
end
local function load_script()
    ticks={};listeners={}
    dofile("src/script/campaign/mod/edh_sariwa_campaign_appearance.lua")
    for _,f in ipairs(ticks) do f() end;flush()
end
load_script();assert(#calls==1 and calls[1]==original)
emit("FactionTurnStart");assert(#calls==1) -- No repeated override spam.
emit("CharacterCreated",other);assert(#calls==1)
local newborn=char(13,"edh_sariwa",false);people[#people+1]=newborn;by_id[13]=newborn
emit("CharacterCreated",newborn);assert(#calls==2 and calls[2]==newborn)
wounded.wounded=false;emit("FactionTurnStart");assert(#calls==3 and calls[3]==wounded)
emit("CharacterFactionChangeEvent",original);assert(#calls==4 and calls[4]==original)
original.wounded=true;emit("CharacterConvalescedOrKilled",original);assert(#calls==4)
original.wounded=false;emit("FactionTurnStart");assert(#calls==5)
load_script();assert(#calls==8) -- Session-local override reapplied after loading.
assert(original.xp==1234 and original.skills=="original" and original.gear=="original")
assert(#people==4) -- No replacement/spawned character, including on old saves.
campaign="wh3_main_chaos";load_script();assert(#calls==8)
print("PASS: old-save and new Hero binding, wounded recovery, faction transfer, reload, subtype/campaign boundaries; original identity/progression preserved")
