-- Execute the authored state, reward service and all-six-chapter adapter.
-- Campaign engine interfaces are fake; no claim of in-game verification.
local F="cr_cth_agents_of_the_moon"
local LONG="cr_combi_region_long_vi"
local AVA="cr_combi_region_avauka"
local ARC="cr_combi_region_leilou"
local BATTLE="mc_huyen_ve_rescue_da_lien"
local SAVE="mc_huyen_ve_quest_state_v25"
local checks=0
local function check(v,msg) checks=checks+1;assert(v,msg) end
local function copy(t)
    if type(t)~="table" then return t end
    local r={};for k,v in pairs(t) do r[k]=copy(v) end;return r
end
local function engine(opts)
    opts=opts or {}
    dofile("src/script/campaign/mod/mc_huyen_ve_quest_state.lua")
    local M=mc_huyen_ve_quest_model
    local e={saved={},queue={},ticks={},listeners={},missions={},ui={},items={},grants={},
      rank=opts.rank or 6,turn=1,mult=opts.mult or 0.5,gold=5000,charges=0,created=0,
      regions={[LONG]=F,[AVA]="enemy",[ARC]=F},war=true,land=true,markers={},
      commander=100,force=200,side="attacker",winner=true,kills=0,quest=false,battle_key="",
      hero_exists=opts.hero or false,hero_rank=opts.hero_rank or 1,hero_wounded=false,
      lord_region=LONG,hero_region=ARC,embedded=false,loaned=false,grant_fails=false}
    if opts.stage then
        local state=M.new();state.chapter=opts.stage
        for ch=1,opts.stage-1 do state.completed[ch]=true;state.ui_completed[ch]=true end
        e.saved[SAVE]=state
    end
    local f={}
    function f:name() return F end
    function f:is_null_interface() return false end
    function f:is_human() return opts.human~=false end
    function f:ancillary_exists(k) return e.items[k] or false end
    function f:treasury() return e.gold end
    function f:at_war_with() return e.war end
    local function character(kind,cqi)
        local c={kind=kind,id=cqi}
        function c:is_null_interface() return false end
        function c:character_subtype(k) return k==(kind=="lord" and "mc_moon_warden" or "mc_da_lien") end
        function c:command_queue_index() return self.id end
        function c:faction() return f end
        function c:is_wounded() return kind=="hero" and e.hero_wounded or (kind=="lord" and e.lord_wounded) or false end
        function c:rank() return kind=="lord" and e.rank or e.hero_rank end
        function c:has_region() return true end
        function c:region() return {name=function() return kind=="lord" and e.lord_region or e.hero_region end} end
        function c:is_embedded_in_military_force() return kind=="hero" and e.embedded end
        function c:is_loaned() return e.loaned end
        function c:logical_position_x() return 1400 end
        function c:logical_position_y() return 280 end
        return c
    end
    e.lord=character("lord",100);e.hero=character("hero",444);e.hero2=character("hero",445)
    function f:character_list()
        return {num_items=function() return e.hero_exists and 2 or 1 end,
          item_at=function(_,i) return i==0 and e.lord or e.hero end}
    end
    local function region(key)
        return {is_null_interface=function() return false end,is_abandoned=function() return e.regions[key]=="abandoned" end,
          name=function() return key end,
          owning_faction=function() return {name=function() return e.regions[key] end} end}
    end
    local pb={}
    function pb:set_piece_battle_key() return e.battle_key end
    function pb:units_killed_by_attacker_unit_set(force,key)
        assert(force==e.expected_force and key=="mc_huyen_ve_all_army_units")
        e.read_side="attacker";return e.kills
    end
    function pb:units_killed_by_defender_unit_set(force,key)
        assert(force==e.expected_force and key=="mc_huyen_ve_all_army_units")
        e.read_side="defender";return e.kills
    end
    cm={}
    function cm:get_campaign_name() return opts.campaign or "cr_combi_expanded" end
    function cm:get_faction(k) assert(k==F);return f end
    function cm:get_region(k) return region(k) end
    function cm:get_saved_value(k) return copy(e.saved[k]) end
    function cm:set_saved_value(k,v) e.saved[k]=copy(v) end
    function cm:add_first_tick_callback(fn) table.insert(e.ticks,fn) end
    function cm:callback(fn) table.insert(e.queue,fn) end
    function cm:model() return {turn_number=function() return e.turn end,
        unit_size_multiplier=function() return e.mult end,pending_battle=function() return pb end} end
    function cm:char_is_agent(c) return c.kind=="hero" end
    function cm:char_lookup_str(c) return "character_cqi:"..c.id end
    function cm:find_valid_spawn_location_for_character_from_settlement(_,anchor)
        if not e.land then return -1,-1 end
        if anchor==ARC then return 1390,290 end
        return 1406,281
    end
    function cm:find_valid_spawn_location_for_character_from_position(_,x,y)
        if not e.land then return -1,-1 end;return x,y
    end
    function cm:set_mission_location_override(target,key,x,y)
        assert(target==f and key=="mc_huyen_ve_quest_02" and x>=0 and y>=0)
        e.rescue_location={x,y}
    end
    function cm:add_interactable_campaign_marker(id,info,x,y,r,fac)
        assert(id=="mc_huyen_ve_archive" and info=="mc_huyen_ve_archive_info" and r==3 and fac==F)
        assert(not e.markers[id],"marker must not duplicate on load")
        e.markers[id]={x,y}
    end
    function cm:remove_interactable_campaign_marker(id) e.markers[id]=nil end
    function cm:set_scripted_mission_text(key,objective,loc,n,total) e.text={key=key,loc=loc,n=n,total=total} end
    function cm:complete_scripted_mission_objective(_,key,objective,success)
        assert(success);e.ui[key]=(e.ui[key] or 0)+1
    end
    function cm:force_add_ancillary(_,item)
        e.grants[item]=(e.grants[item] or 0)+1
        if not e.grant_fails then e.items[item]=true end
    end
    function cm:create_agent(_,kind,subtype)
        assert(kind=="engineer" and subtype=="mc_da_lien")
        e.created=e.created+1;e.hero_exists=true;return e.hero
    end
    function cm:change_character_custom_name() e.renamed=true end
    function cm:set_character_immortality() e.immortal=true end
    function cm:add_agent_experience(_,levels,by_level)
        assert(by_level);e.hero_rank=e.hero_rank+levels
    end
    function cm:pending_battle_cache_num_attackers() return e.side=="attacker" and 1 or 0 end
    function cm:pending_battle_cache_num_defenders() return e.side=="defender" and 1 or 0 end
    function cm:pending_battle_cache_get_attacker() return e.commander,e.force,F end
    function cm:pending_battle_cache_get_defender() return e.commander,e.force,F end
    function cm:pending_battle_cache_is_quest_battle() return e.quest end
    function cm:pending_battle_cache_attacker_victory() return e.winner end
    function cm:pending_battle_cache_defender_victory() return e.winner end
    function cm:create_dilemma_builder(key)
        e.offered=key
        return {add_choice_payload=function() end}
    end
    function cm:create_payload() return {text_display=function() end,clear=function() end} end
    function cm:launch_custom_dilemma_from_builder() e.offers=(e.offers or 0)+1 end
    function cm:treasury_mod(_,delta)
        assert(e.gold+delta>=0);e.gold=e.gold+delta;e.charges=e.charges+1
    end
    core={}
    function core:add_listener(key,event,condition,fn) e.listeners[key]={event=event,condition=condition,fn=fn} end
    mission_manager={}
    function mission_manager:new(faction,key)
        assert(faction==F);local m={key=key,conditions={}}
        function m:set_mission_issuer() end
        function m:add_new_objective(kind) self.kind=kind end
        function m:add_condition(c) table.insert(self.conditions,c) end
        function m:add_payload() end
        function m:set_should_cancel_before_issuing() end
        function m:set_position(x,y) self.position={x,y} end
        function m:trigger() e.missions[key]=(e.missions[key] or 0)+1;e.last_mission=self end
        return m
    end
    out=function() end;script_error=function(msg) error(msg) end
    function e:flush()
        local n=0
        while #self.queue>0 do
            n=n+1;assert(n<50,"callback loop")
            local q=self.queue;self.queue={};for _,fn in ipairs(q) do fn() end
        end
    end
    function e:state() return self.saved[SAVE] end
    function e:load()
        self.listeners={};self.ticks={}
        dofile("src/script/campaign/mod/mc_huyen_ve_quest_rewards.lua")
        dofile("src/script/campaign/mod/mc_huyen_ve_quest_chain.lua")
        for _,fn in ipairs(self.ticks) do fn() end;self:flush()
    end
    function e:event(event,opts2)
        local o=opts2 or {};local ctx={}
        function ctx:faction() return f end
        function ctx:character() return o.character or e.lord end
        function ctx:region() return region(o.region or LONG) end
        function ctx:mission() return {mission_record_key=function() return "mc_huyen_ve_quest_02" end} end
        function ctx:dilemma() return o.dilemma or e.offered end
        function ctx:choice() return o.choice or 0 end
        function ctx:area_key() return "mc_huyen_ve_archive" end
        function ctx:family_member() return {character=function() return o.character or e.hero end} end
        for _,listener in pairs(self.listeners) do
            if listener.event==event and listener.condition(ctx) then listener.fn(ctx) end
        end
        self:flush()
    end
    function e:battle(opts2)
        local o=opts2 or {};self.quest=o.quest or false;self.battle_key=o.key or ""
        self.winner=o.won~=false;self.side=o.side or "attacker";self.commander=o.commander or 100
        self.force=o.force or 200;self.expected_force=self.force;self.kills=o.kills or 0
        self:event("PendingBattle")
        if o.force_after then self.force=o.force_after end
        if o.success_first then self:event("MissionSucceeded") end
        self:event("CharacterCompletedBattle")
        if o.success then self:event("MissionSucceeded") end
    end
    function e:rank_to(n) self.rank=n;self:event("CharacterRankUp") end
    function e:next_turn() self.turn=self.turn+1;self:event("FactionTurnStart") end
    return e
end

local e=engine();e:load()
check(e:state().chapter==1 and e:state().issued,"chapter 1 issued at 6")
e:battle({commander=999});check(e:state().wins==0,"wrong commander excluded")
e:battle({quest=true,won=true});check(e:state().wins==0,"quest battle excluded")
e:battle();e:event("CharacterCompletedBattle");check(e:state().wins==1,"duplicate result excluded")
e.regions[LONG]="enemy";e:battle();check(e:state().chapter==1 and e:state().wins==2,"lost region blocks reward")
e.regions[LONG]=F;e:event("RegionFactionChangeEvent")
check(e:state().chapter==2 and not e:state().issued,"chapter 2 remains rank gated")
check(e.grants.mc_huyen_ve_ngoc_boi_nguyet_anh==1,"pendant once")
e:load();e:rank_to(7);check(not e.missions.mc_huyen_ve_quest_02,"no rescue at rank 7")
e:rank_to(8);check(e:state().issued and e.rescue_location and e.last_mission.kind=="FIGHT_SET_PIECE_BATTLE","native rescue at valid dynamic position")
e:battle({quest=true,key="other",success=true});check(e.created==0,"wrong battle cannot grant Hero")
e:battle({quest=true,key=BATTLE,won=false});check(e.created==0 and e:state().chapter==2,"loss grants nothing")
e:battle({quest=true,key=BATTLE,success_first=true})
check(e.created==1 and e.hero_rank==5 and e.immortal,"successful rescue creates rank-five immortal Hero")
check(e.grants.mc_da_lien_crimson_moonstone==1 and e:state().chapter==3,"gem confirmed before advancing")
e:event("MissionSucceeded");e:load();check(e.created==1,"reload/success duplicate cannot spawn Hero again")
e:rank_to(10);check(e:state().chapter==3 and e:state().phase=="active" and not e.offered,"hostile Avauka has no ransom path")
e.regions[AVA]=F;e:event("RegionFactionChangeEvent",{region=AVA})
check(e:state().chapter==4 and e.grants.mc_huyen_ve_giap_son_van_long_vi==1,"occupation grants armour")
e:rank_to(14);check(e.markers.mc_huyen_ve_archive and e.last_mission.position,"archive marker and mission position created")
e:load();check(e.markers.mc_huyen_ve_archive,"marker restored without duplicate")
e:event("AreaEntered",{character=e.lord});check(not e:state().discovered,"Lord cannot investigate")
e.embedded=true;e:event("AreaEntered");check(not e:state().discovered,"embedded Hero cannot investigate")
e.embedded=false;e:event("AreaEntered");check(e:state().discovered and not e.markers.mc_huyen_ve_archive,"independent Hero discovers and removes marker")
e.hero_region=LONG;e:event("RegionFactionChangeEvent");check(e:state().chapter==4,"Hero already in Long Vi does not auto-deliver")
e:event("CharacterFinishedMovingEvent",{character=e.hero2})
check(e:state().chapter==5 and e.grants.mc_huyen_ve_an_tran_thu==1,"another Hero can deliver")
e:rank_to(18);check(e:state().kill_target==1000 and e.text.total==1000,"unit-size target saved and displayed")
e:battle({kills=400,force=200,force_after=999});check(e:state().kills==400,"uses captured force CQI after force change")
e:event("CharacterCompletedBattle");check(e:state().kills==400,"kill callback deduplicated")
e:battle({quest=true,kills=900});check(e:state().kills==400,"quest kills excluded")
e:battle({kills=600,side="defender",won=false})
check(e.read_side=="defender" and e:state().chapter==6,"defender kills count on a loss")
check(e.grants.mc_huyen_ve_nguyet_dang==1,"lantern once")
e:rank_to(22);check(e.offered=="mc_huyen_ve_restore","restoration offered in owned Long Vi")
e:event("DilemmaChoiceMadeEvent",{choice=1});check(e.charges==0,"declining costs nothing")
e:next_turn();e:event("DilemmaChoiceMadeEvent")
check(e.gold==2000 and e.charges==1 and e:state().paid and e:state().processing_turns==0,"pay once, not a processing turn")
e:event("DilemmaChoiceMadeEvent");e:event("FactionTurnStart")
check(e.charges==1 and e:state().processing_turns==0,"duplicate payment and same-turn event excluded")
e:next_turn();check(e:state().processing_turns==1,"first later faction turn")
e.regions[LONG]="enemy";e:next_turn();check(e:state().processing_turns==1,"lost town pauses work")
e:load();e.regions[LONG]=F;e:next_turn()
check(e:state().chapter==7 and e:state().phase=="completed" and e.grants.mc_huyen_ve_kiem_tran_da==1,"second owned turn completes entire chain")
e:load();e:next_turn();check(e.charges==1 and e.created==1 and e.grants.mc_huyen_ve_kiem_tran_da==1,"completed campaign reload remains idempotent")
for ch=1,6 do check(e:state().completed[ch],"chapter recorded complete "..ch) end

local ransom=engine({stage=3,rank=50});ransom.war=false;ransom:load()
check(ransom.offered=="mc_huyen_ve_negotiate","peaceful owner supports ransom")
ransom.gold=1999;ransom:event("DilemmaChoiceMadeEvent")
check(ransom.charges==0 and not ransom:state().paid,"funds rechecked at choice")
ransom.gold=2000;ransom:next_turn();ransom.war=true;ransom:event("DilemmaChoiceMadeEvent")
check(ransom.charges==0 and ransom:state().chapter==3,"diplomacy rechecked at choice")
ransom.war=false;ransom:next_turn();ransom:event("DilemmaChoiceMadeEvent")
check(ransom.charges==1 and ransom.gold==0 and ransom:state().chapter==4,"ransom pays once and grants armour")
local old=engine({stage=2,rank=50,hero=true,hero_rank=22})
old.items.mc_da_lien_crimson_moonstone=true;old:load();old:battle({quest=true,key=BATTLE,success=true})
check(old.created==0 and old.hero_rank==22 and not old.renamed,"existing test Hero retained unchanged")
check(not old.grants.mc_da_lien_crimson_moonstone,"existing gem not duplicated")
local land=engine({stage=2,rank=8});land.land=false;land:load()
check(not land:state().issued and land.created==0,"no invalid land position issued")
land.land=true;land:next_turn();check(land:state().issued,"valid-land retry")
local missing=engine({stage=2,rank=8});missing.saved.mc_da_lien_visual_test_v20_spawned=true;missing:load()
missing:battle({quest=true,key=BATTLE,success=true})
check(missing.created==0 and missing:state().phase=="reward_pending","absent wounded legacy Hero never duplicated")
local failed=engine();failed.grant_fails=true;failed:load();failed:battle();failed:battle()
check(failed:state().phase=="reward_pending" and failed:state().chapter==1,"failed item grant does not advance")
failed.grant_fails=false;failed:next_turn();check(failed:state().chapter==2,"failed item grant retries")
local early=engine({rank=50});early:load();check(early:state().chapter==1 and early:state().wins==0,"high rank cannot skip chapters")
local alias=engine({campaign="main_warhammer"});alias:load();check(alias:state() and alias:state().issued,"real IEE main_warhammer scripting alias is supported")
local roc=engine({campaign="wh3_main_chaos"});roc:load();check(not roc:state(),"other campaigns excluded")
local legacy=engine();local st=mc_huyen_ve_quest_model.new();st.version=1;st.chapter=2;st.phase="awaiting_implementation";st.completed=nil;st.ui_completed=nil
legacy.saved[SAVE]=st;legacy:load();check(legacy:state().version==2 and legacy:state().completed[1] and legacy:state().phase=="locked","chapter-one candidate save migrates")
print("PASS: "..checks.." full quest-chain checks; actual Lua modules, fake campaign engine")
