-- Early rescue prototype: fixed armies, no reinforcements or timed victory.
load_script_libraries()
local gb = generated_battle:new(false, false, false, nil, false)
local da_lien = gb:get_army(gb:get_player_alliance_num(), "mc_da_lien_proxy")
local escort = gb:get_army(gb:get_player_alliance_num(), "mc_rescue_escort")
local enemies = gb:get_army(gb:get_non_player_alliance_num(), "mc_rescue_besiegers")
bm:out("[mc_rescue] Script loaded: allied Hero, escort and enemy labels resolved")

gb:message_on_time_offset("mc_rescue_start", 1000)
gb:add_listener("mc_rescue_start", function()
    bm:out("[mc_rescue] Battle started: setting defence and exact-death watch")
    bm:camera():fade(false, 0.5)
    local position = da_lien.sunits:item(1).unit:position()
    da_lien:defend(position:get_x(), position:get_z(), 35)
    escort:defend(position:get_x(), position:get_z(), 70)
    -- Native message_on_casualties uses a strict `>` comparison, so threshold 1
    -- can never fire. Check zero hitpoints directly for this one-Hero group.
    bm:watch(function() return da_lien.sunits:unary_hitpoints() <= 0 end, 0,
        function() gb.sm:trigger_message("mc_rescue_da_lien_dead") end,
        "mc_rescue_da_lien_death_watch")
end)
-- The warband is hunting the escort. The player must intervene, rather than
-- wait while the entire enemy army obligingly attacks the player's formation.
enemies:attack_force_on_message("mc_rescue_start", escort)
enemies:force_victory_on_message("mc_rescue_da_lien_dead", 0)
gb:set_objective_on_message("mc_rescue_start", "mc_rescue_defeat_besiegers")
gb:set_objective_on_message("mc_rescue_start", "mc_rescue_protect_da_lien")
-- Normal engine victory remains in charge; there is no automatic timer win.
