-- Saved state contains scalars/tables only; no engine interfaces.
mc_huyen_ve_quest_model = {}
local M = mc_huyen_ve_quest_model
M.levels = {6,8,10,14,18,22}
M.items = {"mc_huyen_ve_ngoc_boi_nguyet_anh", "mc_da_lien_crimson_moonstone",
    "mc_huyen_ve_giap_son_van_long_vi", "mc_huyen_ve_an_tran_thu",
    "mc_huyen_ve_nguyet_dang", "mc_huyen_ve_kiem_tran_da"}

function M.new()
    return {version = 2, chapter = 1, phase = "locked", issued = false,
        wins = 0, battle_serial = 0, pending_serial = 0, counted_serial = 0,
        kills=0,move_serial=0,completed={},ui_completed={},last_reward = "", last_error = ""}
end

function M.upgrade(s)
    if s.version==1 then
        s.version=2;s.completed=s.chapter>1 and {[1]=true} or {};s.ui_completed={}
        s.move_serial=0;s.kills=0
        if s.phase=="awaiting_implementation" then s.phase="locked" end
    end
    return s.version==2
end
function M.activate(s, rank, kill_target)
    if s.chapter>6 or s.phase ~= "locked" or rank < M.levels[s.chapter] then return false end
    s.phase = "active"
    s.issued=false;s.pending_serial=0
    if s.chapter==1 then s.wins=0 end
    if s.chapter==5 then s.kills=0;s.kill_target=kill_target end
    return true
end

function M.battle_pending(s,snapshot)
    s.battle_serial = s.battle_serial + 1
    s.pending_serial = s.phase == "active" and s.battle_serial or 0
    s.pending=snapshot
end

function M.battle_completed(s, commander_matches, quest_battle, won,kills,battle_key)
    if s.phase ~= "active" or not s.issued or not commander_matches then return false end
    local serial = s.pending_serial
    if serial == 0 or serial <= s.counted_serial then return false end
    s.counted_serial = serial
    if s.chapter==2 then
        if quest_battle and battle_key=="mc_huyen_ve_rescue_da_lien" and won then
            s.rescue_won=true;s.phase="reward_pending";return true
        end
        return false
    end
    if quest_battle then return false end
    if s.chapter==1 and won then s.wins=math.min(2,s.wins+1);return true end
    if s.chapter==5 and type(kills)=="number" and kills>=0 and kills<math.huge and kills==kills then
        s.kills=math.min(s.kill_target,s.kills+math.floor(kills))
        if s.kills>=s.kill_target then s.phase="reward_pending" end
        return true
    end
    return false
end

function M.check_objective(s, owns_long_vi,owns_avauka)
    if s.phase~="active" or not s.issued then return false end
    if (s.chapter==1 and s.wins>=2 and owns_long_vi) or
       (s.chapter==3 and owns_avauka) then s.phase="reward_pending";return true end
    return false
end
function M.investigate(s)
    if s.chapter~=4 or s.phase~="active" or not s.issued or s.discovered then return false end
    s.discovered=true;s.discovery_move=s.move_serial;return true
end
function M.move(s,eligible_hero,at_owned_long_vi)
    s.move_serial=s.move_serial+1
    if s.chapter==4 and s.phase=="active" and s.discovered and eligible_hero and
       at_owned_long_vi and s.move_serial>s.discovery_move then
        s.phase="reward_pending";return true
    end
    return false
end
function M.pay(s,cost,treasury,eligible,turn)
    if s.phase~="active" or not s.issued or s.paid or not eligible or treasury<cost then return false end
    if s.chapter~=3 and s.chapter~=6 then return false end
    s.paid=true;s.paid_turn=turn
    if s.chapter==3 then s.phase="reward_pending"
    else s.processing_turns=0;s.last_processing_turn=turn end
    return true
end
function M.turn(s,turn,owns_long_vi)
    if s.chapter~=6 or s.phase~="active" or not s.paid or
       turn<=s.last_processing_turn then return false end
    s.last_processing_turn=turn
    if owns_long_vi then s.processing_turns=s.processing_turns+1 end
    if s.processing_turns>=2 then s.phase="reward_pending" end
    return true
end
function M.confirm_reward(s,item_exists,hero_exists)
    if s.phase~="reward_pending" or not item_exists or (s.chapter==2 and not hero_exists) then return false end
    local ch=s.chapter
    s.completed[ch]=true;s.last_reward=M.items[ch];s.chapter=ch+1
    s.phase=s.chapter>6 and "completed" or "locked";s.issued=false
    s.pending_serial=0;s.pending=nil;s.paid=nil;s.dilemma_key=nil;s.prompt_turn=nil
    s.marker_x=nil;s.marker_y=nil;s.discovered=nil;s.discovery_move=nil
    return true
end
