-- Only Mooncourt lords in Agents of the Moon; no UI operations or unit spawning.
-- Native reset refunds through the engine. Never assign XP/extra skill points.
local faction_key = "cr_cth_agents_of_the_moon"
local subtype = "mc_mooncourt_lord"
local foundation = "mc_zhao_v36_foundation"
local legacy_skills = {
__LEGACY_SKILLS__
}

local function eligible(character)
    return character and not character:is_null_interface()
        and character:character_subtype(subtype)
        and character:faction():name() == faction_key
end

local function initialise(character)
    if not eligible(character) then return end
    local lookup = cm:char_lookup_str(character)
    local marker = "mc_zhao_v36_reset_" .. tostring(character:command_queue_index())
    if not cm:get_saved_value(marker) then
        local has_legacy = false
        for _, skill in ipairs(legacy_skills) do
            if character:has_skill(skill) then has_legacy = true; break end
        end
        if has_legacy then
            cm:force_reset_skills(lookup)
            out("[mc_zhao_v36] Reset legacy Zhao skills; identity, XP and traits retained")
        end
        cm:set_saved_value(marker, true)
    end
    -- Old hidden free grants can survive a native reset. Remove only named
    -- private legacy skills, preserving every native background trait.
    for _, skill in ipairs(legacy_skills) do
        for attempt = 1, 4 do
            if not character:has_skill(skill) then break end
            cm:remove_skill_point(lookup, skill)
        end
    end
    if not character:has_skill(foundation) then cm:add_skill(lookup, foundation) end
    -- Refresh free mount milestones for existing high-rank lords after reset.
    for _, mount in ipairs({{5, "mc_zhao_v36_mount_warhorse"}, {15, "mc_zhao_v36_mount_jade_longma"}}) do
        if character:rank() >= mount[1] and not character:has_skill(mount[2]) then
            cm:add_skill(lookup, mount[2])
        end
    end
    if character:has_ancillary("mc_mooncourt_lord_command_seal") then
        cm:force_remove_ancillary(character, "mc_mooncourt_lord_command_seal", false, true)
    end
    cm:set_character_immortality(lookup, character:has_skill("wh2_main_skill_all_immortality_lord"))
end

local function scan()
    local faction = cm:get_faction(faction_key)
    if not faction or faction:is_null_interface() then return end
    local chars = faction:character_list()
    for i = 0, chars:num_items() - 1 do initialise(chars:item_at(i)) end
end

cm:add_first_tick_callback(function() cm:callback(scan, 1) end)
core:add_listener("mc_zhao_v36_turn", "FactionTurnStart",
    function(context) return context:faction():name() == faction_key end,
    function() cm:callback(scan, 0.2) end, true)
for _, event in ipairs({"CharacterCreated", "CharacterRecruited", "CharacterRankUp"}) do
    core:add_listener("mc_zhao_v36_" .. event, event,
        function(context) return eligible(context:character()) end,
        function() cm:callback(scan, 0.2) end, true)
end
-- This event explicitly exposes the skill key. Do not assume an inherited
-- character() accessor; the action scans only the already-scoped Moon roster.
core:add_listener("mc_zhao_v36_immortality_skill", "CharacterSkillPointAllocated",
    function(context) return context:skill_point_spent_on() == "wh2_main_skill_all_immortality_lord" end,
    function() cm:callback(scan, 0.2) end, true)
