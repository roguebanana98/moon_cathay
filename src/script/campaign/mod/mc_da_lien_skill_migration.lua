-- Scoped v23 test-save migration. Keep XP, background traits, items and identity.
-- API: WH3 episodic_scripting force_reset_skills, remove_skill_point, add_skill.
-- BEGIN GENERATED LEGACY SKILLS
local legacy_skills = {
    "wh2_main_skill_all_hero_assist_army_increase_mobility",
    "wh2_main_skill_all_hero_hinder_agent_assassinate",
    "wh2_main_skill_all_hero_hinder_army_hinder_replenishment",
    "wh2_main_skill_all_hero_hinder_settlement_damage_building",
    "wh2_main_skill_all_hero_passive_boost_income",
    "wh2_main_skill_all_hero_reduce_action_cost",
    "wh3_cp1_skill_cth_alchemist_army_alchemical_hardening",
    "wh3_cp1_skill_cth_alchemist_army_metallurgic_refining",
    "wh3_cp1_skill_cth_alchemist_self_alchemical_enhancements",
    "wh3_cp1_skill_cth_alchemist_unique_alchemical_wrath",
    "wh3_cp1_skill_cth_alchemist_unique_harmonic_anchoring",
    "wh3_cp1_skill_cth_alchemist_unique_living_forge",
    "wh3_cp1_skill_cth_alchemist_unique_steel_sheathing",
    "wh3_cp1_skill_cth_alchemist_unique_student_of_the_house_of_secrets",
    "wh3_main_skill_all_dummy_agent_actions_cth_alchemist",
    "wh3_main_skill_all_mentor_hero",
    "wh3_main_skill_cth_alchemist_self_enchanted_metallurgy",
    "wh3_main_skill_cth_alchemist_self_enchanted_metallurgy_flaming",
    "wh3_main_skill_cth_alchemist_self_enchanted_metallurgy_piercing",
    "wh3_main_skill_cth_alchemist_self_enchanted_metallurgy_poison",
    "wh3_main_skill_cth_all_unique_magic_resist",
    "wh3_main_skill_cth_all_unique_missile_resist",
    "wh_main_skill_all_magic_all_06_evasion",
    "wh_main_skill_all_magic_all_07_earthing",
    "wh_main_skill_all_magic_all_08_power_drain",
    "wh_main_skill_all_magic_all_11_arcane_conduit",
    "wh_main_skill_all_magic_metal_01_searing_doom",
    "wh_main_skill_all_magic_metal_02_plague_of_rust",
    "wh_main_skill_all_magic_metal_03_metalshifting",
    "wh_main_skill_all_magic_metal_04_glittering_robe",
    "wh_main_skill_all_magic_metal_05_gehennas_golden_hounds",
    "wh_main_skill_all_magic_metal_09_transmutation_of_lead",
    "wh_main_skill_all_magic_metal_10_final_transmutation",
    "wh_main_skill_all_magic_metal_dummy_searing_doom",
}
-- END GENERATED LEGACY SKILLS

local function initialise(character)
    if character:is_null_interface() or not character:character_subtype("mc_da_lien") then return end
    local id = tostring(character:command_queue_index())
    local complete = "mc_da_lien_v23_skills_complete_" .. id
    if cm:get_saved_value(complete) then return end
    local lookup = cm:char_lookup_str(character)
    local reset = "mc_da_lien_v23_skills_reset_" .. id
    if not cm:get_saved_value(reset) then
        local has_legacy = false
        for _, skill in ipairs(legacy_skills) do
            if character:has_skill(skill) then has_legacy = true; break end
        end
        if has_legacy then
            cm:force_reset_skills(lookup)
            out("[mc_da_lien] v23: reset legacy test skills; XP and background retained")
        end
        -- Never reset this Hero again if later cleanup needs a retry.
        cm:set_saved_value(reset, true)
    end
    -- Remove any legacy hidden grant surviving the native reset. Bounded: each
    -- old visible skill has at most three levels; no XP or point grants are added.
    for _, skill in ipairs(legacy_skills) do
        for attempt = 1, 3 do
            if not character:has_skill(skill) then break end
            cm:remove_skill_point(lookup, skill)
        end
    end
    for _, skill in ipairs({"mc_da_lien_skill_foundation_actions", "mc_da_lien_skill_foundation_blossom"}) do
        if not character:has_skill(skill) then cm:add_skill(lookup, skill, true, true) end
    end
    cm:set_character_immortality(lookup, true)
    for _, skill in ipairs(legacy_skills) do
        if character:has_skill(skill) then
            out("[mc_da_lien] v23: legacy skill cleanup pending: " .. skill)
            return
        end
    end
    if not character:has_skill("mc_da_lien_skill_foundation_actions") or
       not character:has_skill("mc_da_lien_skill_foundation_blossom") then
        out("[mc_da_lien] v23: foundation grants pending")
        return
    end
    cm:set_saved_value(complete, true)
    out("[mc_da_lien] v23: Moon Arts foundations ready")
end

local function scan()
    local faction = cm:get_faction("cr_cth_agents_of_the_moon")
    if not faction or faction:is_null_interface() or not faction:is_human() then return end
    local characters = faction:character_list()
    for i = 0, characters:num_items() - 1 do initialise(characters:item_at(i)) end
end

-- v20 appearance-spawn callback runs first, at one second.
cm:add_first_tick_callback(function() cm:callback(scan, 2) end)
core:add_listener("mc_da_lien_v23_skill_migration", "FactionTurnStart",
    function(context) return context:faction():name() == "cr_cth_agents_of_the_moon" end,
    function() cm:callback(scan, 1) end, true)
