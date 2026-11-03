-- Execute CA's real generated-battle library against fake engine boundaries.
-- This checks library contracts and listener fan-out, not engine/map behaviour.
is_number = function(x) return type(x)=="number" end
is_string = function(x) return type(x)=="string" end
is_function = function(x) return type(x)=="function" end
is_table = function(x) return type(x)=="table" end
is_nil = function(x) return x==nil end
is_generatedarmy = function(x) return type(x)=="table" and x.sunits~=nil end
set_object_class = function(o,c) setmetatable(o,{__index=c}) end
set_class_custom_type_and_tostring = function() end
set_class_custom_type = function() end
set_class_tostring = function() end
script_error = function(x) error(x) end
local queue,phases,objectives,groups={},{},{},{}
local hp,ended,routed=1,false,false
local listeners={}
local sm={}
function sm:add_listener(key,fn)
    listeners[key]=listeners[key] or {};table.insert(listeners[key],fn)
end
function sm:trigger_message(key)
    for _,fn in ipairs(listeners[key] or {}) do fn() end
end
get_messager=function() return sm end
bm={}
function bm:out() end
function bm:register_phase_change_callback(key,fn) phases[key]=fn end
function bm:setup_victory_callback() end
function bm:callback(fn) table.insert(queue,fn) end
function bm:camera() return {fade=function() end} end
function bm:set_objective(key) objectives[key]=true end
function bm:watch(predicate,delay,fn) self.death={predicate=predicate,fn=fn} end
function bm:change_victory_countdown_limit() end
function bm:end_battle() ended=true end
local function flush()
    while #queue>0 do local current=queue;queue={};for _,fn in ipairs(current) do fn() end end
end
dofile("reference/local/lord-scripts/script/_lib/lib_generated_battle.lua")
function generated_battle:build_armies()
    self.player_alliance_id=1;self.non_player_alliance_id=2
    local function army(label)
        local a={script_name=label,sm=sm,id=label,sunits={},alliance_index=label=="mc_rescue_besiegers" and 2 or 1}
        set_object_class(a,generated_army)
        function a.sunits:item() return {unit={position=function()
            return {get_x=function() return 123 end,get_z=function() return 456 end}
        end}} end
        function a.sunits:unary_hitpoints() return hp end
        function a.sunits:invincible_if_standing() end
        function a:attack() self.attacked=true end
        function a:attack_force(target)
            assert(target==groups.mc_rescue_escort.sunits)
            self.attacked=true
        end
        function a:defend(x,z,r) self.defended=r end
        function a:get_allied_and_enemy_forces()
            self.enemy_force={rout_over_time=function() routed=true end}
        end
        groups[label]=a;return a
    end
    self.generated_armies={
        {{army("mc_rescue_player")},{army("mc_da_lien_proxy"),army("mc_rescue_escort")}},
        {{army("mc_rescue_besiegers")}}
    }
end
function generated_battle:generated_armies_report() end
load_script_libraries=function() end
dofile("src/script/battle/quest_battles/mc_huyen_ve/rescue/battle_script.lua")
assert(not objectives.mc_rescue_protect_da_lien)
assert(phases.Deployed,"native deployment callback must be registered")
phases.Deployed();flush()
assert(groups.mc_rescue_besiegers.attacked)
assert(groups.mc_da_lien_proxy.defended==35 and groups.mc_rescue_escort.defended==70)
assert(objectives.mc_rescue_protect_da_lien and objectives.mc_rescue_defeat_besiegers,
    "all listeners on the same start message must fire")
assert(bm.death and not bm.death.predicate())
hp=0;assert(bm.death.predicate());bm.death.fn();flush()
assert(routed and ended,"native defeat path routes player force and ends battle")
print("PASS: rescue uses actual native generated-battle contracts (fake engine boundaries)")
