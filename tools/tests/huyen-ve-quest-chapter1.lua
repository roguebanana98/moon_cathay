local model_path = "src/script/campaign/mod/mc_huyen_ve_quest_state.lua"
local adapter_path = "src/script/campaign/mod/mc_huyen_ve_quest_campaign.lua"
dofile(model_path)
local M = mc_huyen_ve_quest_model
local tests = 0
local function check(value, label)
    tests = tests + 1
    assert(value, label)
end
local function clone(t)
    if type(t) ~= "table" then return t end
    local c = {}; for k,v in pairs(t) do c[k] = clone(v) end; return c
end
local s = M.new()
M.battle_pending(s); M.battle_completed(s,true,false,true)
check(s.wins == 0, "pre-mission battles excluded")
check(not M.activate(s,5) and M.activate(s,6), "level-six gate")
s.issued = true
M.battle_pending(s); M.battle_completed(s,false,false,true)
check(s.wins == 0, "other army excluded")
M.battle_pending(s); M.battle_completed(s,true,true,true)
check(s.wins == 0, "quest battle excluded")
M.battle_pending(s); M.battle_completed(s,true,false,false)
check(s.wins == 0, "loss not a victory")
M.battle_pending(s); M.battle_completed(s,true,false,true)
M.battle_completed(s,true,false,true)
check(s.wins == 1, "duplicate completion event excluded")
s = clone(s)
M.battle_completed(s,true,false,true)
check(s.wins == 1, "dedup persists across serialised state copy")
M.battle_pending(s); M.battle_completed(s,true,false,true)
check(s.wins == 2, "two battles in the same turn can both count")
check(not M.check_objective(s,false) and s.wins == 2, "lost Long Vi preserves wins and blocks reward")
check(M.check_objective(s,true), "recovered region completes combined objective")
check(not M.confirm_reward(s,false), "unconfirmed grant does not advance")
check(M.confirm_reward(s,true) and s.chapter == 2, "confirmed item advances once")
check(not M.confirm_reward(s,true), "reward cannot advance twice")

print("PASS: " .. tests .. " chapter-1 state regressions")
