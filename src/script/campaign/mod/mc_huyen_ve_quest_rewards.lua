-- Shared chapter-2 reward service; called only after rescue victory is confirmed.
-- No automatic grant or spawn is performed when this module is loaded.
mc_huyen_ve_quest_rewards = {}
local M = mc_huyen_ve_quest_rewards
local busy = false
local faction_key = "cr_cth_agents_of_the_moon"
local hero_key = "mc_da_lien"
local gem = "mc_da_lien_crimson_moonstone"

local function find_hero(f)
    local chars = f:character_list()
    for i = 0, chars:num_items() - 1 do
        local c = chars:item_at(i)
        if c:character_subtype(hero_key) then return c end
    end
end

function M.ensure_da_lien(s, commander, persist, completed)
    if busy or s.chapter ~= 2 or s.phase ~= "reward_pending" then return end
    local f = cm:get_faction(faction_key)
    if not f or f:is_null_interface() then return end
    local hero = find_hero(f)
    if not hero then
        -- A previously created Hero may be outside the active character list
        -- while convalescing. Never create another just because it is absent.
        if s.hero_created_cqi or cm:get_saved_value("mc_da_lien_visual_test_v20_spawned") then return end
        local x,y
        if commander and not commander:is_null_interface() and not commander:is_wounded() then
            x,y = cm:find_valid_spawn_location_for_character_from_position(faction_key,
                commander:logical_position_x(), commander:logical_position_y(), true, 2)
        end
        if not x or not y or x < 0 or y < 0 then
            local r = cm:get_region("cr_combi_region_long_vi")
            if r and not r:is_null_interface() and r:owning_faction():name() == faction_key then
                x,y = cm:find_valid_spawn_location_for_character_from_settlement(faction_key,
                    "cr_combi_region_long_vi", false, true)
            end
        end
        if not x or not y or x < 0 or y < 0 then return end
        hero = cm:create_agent(faction_key, "engineer", hero_key, x, y, true, true)
        if not hero or hero:is_null_interface() then return end
        s.hero_created_cqi = hero:command_queue_index()
        s.hero_created_for_rescue = true
        persist()
    end
    -- Existing test Hero is never renamed, downgraded or respecialised.
    if s.hero_created_for_rescue and hero:command_queue_index() == s.hero_created_cqi then
        cm:change_character_custom_name(hero, "Da Lien", "", "", "")
        if hero:rank() < 5 then
            -- Native campaign_manager by_level adds ranks, it does not set rank.
            cm:add_agent_experience(cm:char_lookup_str(hero), 5 - hero:rank(), true)
        end
    end
    cm:set_character_immortality(cm:char_lookup_str(hero), true)
    if f:ancillary_exists(gem) then
        s.hero_reward_confirmed = true
        persist()
        completed(hero)
        return
    end
    if hero:is_wounded() then return end
    busy = true
    cm:force_add_ancillary(hero, gem, true, true)
    cm:callback(function()
        busy = false
        local current = cm:get_faction(faction_key)
        if current and not current:is_null_interface() then
            local actual = find_hero(current)
            if actual and current:ancillary_exists(gem) then
                s.hero_reward_confirmed = true
                cm:set_saved_value("mc_da_lien_crimson_moonstone_v24_granted", true)
                persist()
                completed(actual)
            end
        end
    end, 1)
end
