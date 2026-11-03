local listeners,armies,objectives = {},{},{}
local watch,triggered,attack,reinforcements = nil,0,nil,0
local hp = 1
load_script_libraries = function() end
bm = {}
function bm:out() end
function bm:camera() return {fade=function() end} end
function bm:watch(predicate,delay,callback,key)
    assert(key == "mc_rescue_da_lien_death_watch")
    watch = {predicate=predicate,callback=callback}
end
local sm = {}
function sm:trigger_message(key)
    triggered = triggered + 1
    if listeners[key] then listeners[key]() end
end
local gb = {sm=sm}
function gb:get_player_alliance_num() return 1 end
function gb:get_non_player_alliance_num() return 2 end
function gb:get_army(alliance,label)
    local id = label or "player"
    local a = {alliance=alliance}
    a.sunits = {}
    function a.sunits:item()
        return {unit={position=function() return {get_x=function() return 123 end,get_z=function() return 456 end} end}}
    end
    function a.sunits:unary_hitpoints() return hp end
    function a:defend(x,y,radius)
        assert(x==123 and y==456)
        self.radius = radius
    end
    function a:attack_on_message(key) attack=key end
    function a:attack_force_on_message(key,target)
        assert(target==armies.mc_rescue_escort)
        attack=key
    end
    function a:force_victory_on_message(key,delay)
        assert(self.alliance==2 and delay==0)
        listeners[key]=function() self.victory=true end
    end
    function a:reinforce_on_message() reinforcements=reinforcements+1 end
    armies[id]=a
    return a
end
function gb:message_on_time_offset(key,delay) assert(key=="mc_rescue_start" and delay==1000) end
function gb:add_listener(key,callback) listeners[key]=callback end
function gb:set_objective_on_message(key,text) objectives[text]=key end
generated_battle = {}
function generated_battle:new(black,prevent_player,prevent_ai,intro,debug)
    assert(not black and not prevent_player and not prevent_ai and intro==nil and not debug)
    return gb
end
dofile("src/script/battle/quest_battles/mc_huyen_ve/rescue/battle_script.lua")
assert(armies.mc_da_lien_proxy and armies.mc_rescue_escort and armies.mc_rescue_besiegers)
assert(attack=="mc_rescue_start" and reinforcements==0)
assert(objectives.mc_rescue_defeat_besiegers and objectives.mc_rescue_protect_da_lien)
listeners.mc_rescue_start()
assert(armies.mc_da_lien_proxy.radius==35 and armies.mc_rescue_escort.radius==70)
assert(watch and not watch.predicate())
hp=0.0001
assert(not watch.predicate(),"low health is not death")
hp=0
assert(watch.predicate(),"zero health must trigger failure")
watch.callback()
assert(armies.mc_rescue_besiegers.victory and triggered==1)
print("PASS: rescue battle script labels, orders, no reinforcements and exact-death failure (mocked battle)")
