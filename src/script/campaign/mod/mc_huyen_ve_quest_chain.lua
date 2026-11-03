-- Six sequential chapters. Native mission UI, one early set-piece battle,
-- persistent objective/reward state and no automatic visual-test grants.
local F="cr_cth_agents_of_the_moon"
local LORD="mc_moon_warden"
local LONG="cr_combi_region_long_vi"
local AVA="cr_combi_region_avauka"
local ARCHIVE="cr_combi_region_leilou"
local BATTLE="mc_huyen_ve_rescue_da_lien"
local SAVE="mc_huyen_ve_quest_state_v25"
local MARKER="mc_huyen_ve_archive"
local s,M,ready,busy,marker_live=nil,nil,false,false,false
local pulse
local function mission(ch) return string.format("mc_huyen_ve_quest_%02d",ch) end
local function objective(ch) return mission(ch).."_complete" end
local function persist() cm:set_saved_value(SAVE,s) end
local function faction()
    local f=cm:get_faction(F)
    if f and not f:is_null_interface() and f:is_human() then return f end
end
local function owned(key)
    local r=cm:get_region(key)
    return r and not r:is_null_interface() and not r:is_abandoned() and r:owning_faction():name()==F
end
local function lord(f)
    local chars=f:character_list()
    for i=0,chars:num_items()-1 do
        local c=chars:item_at(i)
        if c:character_subtype(LORD) and not c:is_wounded() then return c end
    end
end
local function at_long(c)
    return c and c:has_region() and c:region():name()==LONG and owned(LONG)
end
local function independent_hero(c)
    return c and not c:is_null_interface() and c:faction():name()==F and
        not c:is_wounded() and cm:char_is_agent(c) and
        not c:is_embedded_in_military_force() and not c:is_loaned()
end
local function friendly_avauka(f)
    local r=cm:get_region(AVA)
    if not r or r:is_null_interface() or r:is_abandoned() then return false end
    local owner=r:owning_faction()
    return owner:name()~=F and not f:at_war_with(owner)
end
local function valid_position(anchor)
    local r=cm:get_region(anchor)
    if not r or r:is_null_interface() then return end
    local x,y=cm:find_valid_spawn_location_for_character_from_settlement(F,anchor,false,true)
    if not x or not y or x<0 or y<0 then return end
    local px,py=cm:find_valid_spawn_location_for_character_from_position(F,x+6,y+3,true,4)
    if px and py and px>=0 and py>=0 then return px,py end
    return x,y
end
local function clear_marker()
    if marker_live or s.marker_x then cm:remove_interactable_campaign_marker(MARKER) end
    marker_live=false
end
local function ensure_marker()
    if s.chapter~=4 or s.phase~="active" or s.discovered then
        if marker_live then clear_marker() end
        return
    end
    if not s.marker_x then
        s.marker_x,s.marker_y=valid_position(ARCHIVE)
        if not s.marker_x then s.last_error="Archive has no valid land position";persist();return end
        persist()
    end
    if not marker_live then
        -- The engine saves markers; replace our own id on load, never duplicate it.
        cm:remove_interactable_campaign_marker(MARKER)
        cm:add_interactable_campaign_marker(MARKER,"mc_huyen_ve_archive_info",
            s.marker_x,s.marker_y,3,F,"")
        marker_live=true
    end
end
local function refresh_text()
    if not s.issued or s.chapter>6 or s.chapter==2 then return end
    local ch=s.chapter
    local key="mission_text_text_"..mission(ch).."_active"
    local n,total=0,0
    if ch==1 then key="mission_text_text_mc_huyen_ve_quest_01_"..(owned(LONG) and "owned" or "unowned");n=s.wins
    elseif ch==4 and s.discovered then key="mission_text_text_mc_huyen_ve_quest_04_deliver"
    elseif ch==5 then
        key="mission_text_text_mc_huyen_ve_quest_05_active";n=s.kills;total=s.kill_target
    elseif ch==6 and s.paid then key="mission_text_text_mc_huyen_ve_quest_06_processing";n=s.processing_turns end
    cm:set_scripted_mission_text(mission(ch),objective(ch),key,n,total)
end
local function sync_completions()
    for ch=1,6 do
        if ch~=2 and s.completed[ch] and not s.ui_completed[ch] then
            cm:complete_scripted_mission_objective(F,mission(ch),objective(ch),true)
            s.ui_completed[ch]=true;persist()
        end
    end
end
local function finish_reward(f,hero)
    if not f or s.phase~="reward_pending" or s.chapter>6 then return end
    local ch=s.chapter
    if M.confirm_reward(s,f:ancillary_exists(M.items[ch]),hero~=nil) then
        if ch==4 then clear_marker() end
        persist();sync_completions()
        out("[mc_huyen_ve_quests] Chapter "..ch.." reward confirmed")
        cm:callback(pulse,0.2)
    end
end
local function try_reward(f,c)
    if s.phase~="reward_pending" or busy then return end
    if s.chapter==2 then
        if not s.rescue_won or not s.rescue_mission_succeeded then return end
        mc_huyen_ve_quest_rewards.ensure_da_lien(s,c,persist,function(hero)
            finish_reward(faction(),hero)
        end)
        return
    end
    local item=M.items[s.chapter]
    if f:ancillary_exists(item) then finish_reward(f);return end
    if not c then return end
    busy=true
    cm:force_add_ancillary(c,item,true,true)
    cm:callback(function()
        busy=false
        local current=faction()
        if current then finish_reward(current) end
    end,1)
end
local function issue(f)
    local ch=s.chapter
    if ch==2 and not s.rescue_x then
        s.rescue_x,s.rescue_y=valid_position(LONG)
        if not s.rescue_x then s.last_error="Rescue has no valid land position";persist();return end
    end
    if ch==4 then ensure_marker();if not s.marker_x then return end end
    local mm=mission_manager:new(F,mission(ch))
    mm:set_mission_issuer("mc_huyen_ve_moon_court")
    if ch==2 then
        mm:add_new_objective("FIGHT_SET_PIECE_BATTLE")
        mm:add_condition("set_piece_battle "..BATTLE)
    else
        mm:add_new_objective("SCRIPTED")
        mm:add_condition("script_key "..objective(ch))
        local text="mission_text_text_"..mission(ch).."_active"
        if ch==1 then text="mission_text_text_mc_huyen_ve_quest_01_unowned"
        end
        mm:add_condition("override_text "..text)
        if ch==4 then mm:set_position(s.marker_x,s.marker_y) end
    end
    mm:add_payload("text_display mc_huyen_ve_quest_reward_"..ch)
    mm:set_should_cancel_before_issuing(false)
    mm:trigger()
    if ch==2 then
        -- Native Monster Hunts use this API after issuing a dynamic QB mission.
        cm:set_mission_location_override(f,mission(ch),s.rescue_x,s.rescue_y)
    end
    s.issued=true;persist()
end
local function offer_payment(f,c)
    local ch=s.chapter
    if s.phase~="active" or not s.issued or s.paid or s.dilemma_key or
       (ch~=3 and ch~=6) then return end
    local turn=cm:model():turn_number()
    if s.prompt_turn==turn then return end
    local eligible=(ch==3 and friendly_avauka(f)) or (ch==6 and at_long(c))
    local cost=ch==3 and 2000 or 3000
    if not eligible or f:treasury()<cost then return end
    local key=ch==3 and "mc_huyen_ve_negotiate" or "mc_huyen_ve_restore"
    local db=cm:create_dilemma_builder(key)
    local payload=cm:create_payload()
    payload:text_display("mc_huyen_ve_quest_pay_"..cost)
    db:add_choice_payload("FIRST",payload);payload:clear()
    payload:text_display("dummy_do_nothing")
    db:add_choice_payload("SECOND",payload)
    -- Treasury is charged in the guarded callback after rechecking ownership,
    -- diplomacy and funds; the UI payload only describes the proposed payment.
    s.dilemma_key=key;s.prompt_turn=turn;persist()
    cm:launch_custom_dilemma_from_builder(db,f)
end
pulse=function()
    if not ready then return end
    local f=faction();if not f then return end
    sync_completions()
    if s.chapter>6 then return end
    local c=lord(f)
    local multiplier=cm:model():unit_size_multiplier()
    local target=2000
    if type(multiplier)=="number" and multiplier>0 then
        target=math.floor(2000*multiplier+0.5)
    end
    if c and M.activate(s,c:rank(),target) then persist() end
    if s.phase=="active" and not s.issued then issue(f) end
    if s.chapter==2 and s.issued and s.phase=="active" then
        cm:set_mission_location_override(f,mission(2),s.rescue_x,s.rescue_y)
    end
    ensure_marker();refresh_text()
    if M.check_objective(s,owned(LONG),owned(AVA)) then persist() end
    offer_payment(f,c);try_reward(f,c)
end
local function side_for(cqi)
    for _,side in ipairs({"attacker","defender"}) do
        local count=cm["pending_battle_cache_num_"..side.."s"](cm)
        for i=1,count do
            local character,force,f=cm["pending_battle_cache_get_"..side](cm,i)
            if character==cqi and f==F then return side,force end
        end
    end
end
cm:add_first_tick_callback(function()
    local f=faction()
    local campaign=cm:get_campaign_name()
    -- IEE loads cr_combi_expanded map data but aliases the scripting name to
    -- main_warhammer. Check its unique region as well as the scripting name.
    if not f or (campaign~="cr_combi_expanded" and campaign~="main_warhammer") then return end
    local anchor=cm:get_region(LONG)
    if not anchor or anchor:is_null_interface() then return end
    M=mc_huyen_ve_quest_model
    if not M or not mc_huyen_ve_quest_rewards then script_error("Huyen Ve quest modules missing");return end
    s=cm:get_saved_value(SAVE) or M.new()
    if not M.upgrade(s) then script_error("Unsupported Huyen Ve quest state");return end
    cm:set_saved_value("mc_huyen_ve_quests_v25_enabled",true)
    ready=true;persist()
    out("[mc_huyen_ve_quests] Six-chapter campaign controller initialised; state "..s.version..", chapter "..s.chapter)
    cm:callback(pulse,0.5)
end)
core:add_listener("mc_hv_chain_turn","FactionTurnStart",
    function(ctx) return ready and ctx:faction():name()==F end,
    function()
        local turn=cm:model():turn_number()
        if s.dilemma_key and (s.prompt_turn or 0)<turn then s.dilemma_key=nil end
        if s.chapter==2 and s.rescue_mission_succeeded and not s.rescue_won then
            -- A mission completed by the wrong commander must never grant Da Lien.
            s.rescue_mission_succeeded=false;s.issued=false
            s.last_error="Rescue success did not match Huyen Ve's battle; retry required"
        end
        M.turn(s,turn,owned(LONG));persist();pulse()
    end,true)
core:add_listener("mc_hv_chain_rank","CharacterRankUp",
    function(ctx) return ready and ctx:character():faction():name()==F and ctx:character():character_subtype(LORD) end,
    function() cm:callback(pulse,0.1) end,true)
core:add_listener("mc_hv_chain_region","RegionFactionChangeEvent",
    function(ctx) return ready and (ctx:region():name()==LONG or ctx:region():name()==AVA) end,pulse,true)
core:add_listener("mc_hv_chain_pending","PendingBattle",function() return ready end,
    function()
        local f=faction();if not f then return end
        local c=lord(f);local snapshot
        if c then
            local side,force=side_for(c:command_queue_index())
            if side then snapshot={cqi=c:command_queue_index(),force=force,side=side,
                quest=cm:pending_battle_cache_is_quest_battle(),
                key=cm:model():pending_battle():set_piece_battle_key()} end
        end
        M.battle_pending(s,snapshot);persist()
    end,true)
core:add_listener("mc_hv_chain_battle","CharacterCompletedBattle",
    function(ctx) return ready and s.pending and ctx:character():command_queue_index()==s.pending.cqi end,
    function()
        local p=s.pending
        local won=cm["pending_battle_cache_"..p.side.."_victory"](cm)
        local kills
        if s.chapter==5 and not p.quest then
            local pb=cm:model():pending_battle()
            kills=pb["units_killed_by_"..p.side.."_unit_set"](pb,p.force,"mc_huyen_ve_all_army_units")
        end
        M.battle_completed(s,true,p.quest,won,kills,p.key);persist();pulse()
    end,true)
core:add_listener("mc_hv_chain_rescue_success","MissionSucceeded",
    function(ctx) return ready and s.chapter==2 and s.issued and
        ctx:faction():name()==F and ctx:mission():mission_record_key()==mission(2) end,
    function() s.rescue_mission_succeeded=true;persist();cm:callback(pulse,0.2) end,true)
core:add_listener("mc_hv_chain_rescue_retry","MissionFailed",
    function(ctx) return ready and s.chapter==2 and s.phase=="active" and
        ctx:faction():name()==F and ctx:mission():mission_record_key()==mission(2) end,
    function() s.issued=false;persist() end,true)
core:add_listener("mc_hv_chain_archive","AreaEntered",
    function(ctx) return ready and ctx:area_key()==MARKER end,
    function(ctx)
        local c=ctx:family_member():character()
        if independent_hero(c) and M.investigate(s) then
            persist();clear_marker();refresh_text()
        end
    end,true)
core:add_listener("mc_hv_chain_move","CharacterFinishedMovingEvent",
    function(ctx) return ready and ctx:character():faction():name()==F end,
    function(ctx)
        local c=ctx:character()
        M.move(s,independent_hero(c),at_long(c));persist();pulse()
    end,true)
core:add_listener("mc_hv_chain_payment","DilemmaChoiceMadeEvent",
    function(ctx) return ready and ctx:faction():name()==F and ctx:dilemma()==s.dilemma_key end,
    function(ctx)
        local f=faction();local ch=s.chapter;s.dilemma_key=nil
        local eligible=(ch==3 and friendly_avauka(f)) or (ch==6 and at_long(lord(f)))
        local cost=ch==3 and 2000 or 3000
        if ctx:choice()==0 and M.pay(s,cost,f:treasury(),eligible,cm:model():turn_number()) then
            cm:treasury_mod(F,-cost)
        end
        persist();pulse()
    end,true)
