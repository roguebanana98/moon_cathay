-- Use MIXER's real functions; mock only the game's frontend host interfaces.
local values, callbacks, errors = {}, {}, {}
common = {set_context_value=function(k,v) values[k]=v end}
core = {is_frontend=function() return true end,
    add_ui_created_callback=function(_,f) callbacks[#callbacks+1]=f end}
is_string=function(v) return type(v)=="string" end
is_table=function(v) return type(v)=="table" end
out=function(v) errors[#errors+1]=v end
dofile("reference/local/mixer/script/mixer/mixer_helpers.lua")
dofile("reference/local/mixer/script/_lib/mod/mixer_lib_frontend.lua")
local original = {}
for k,v in pairs(mixer_factions_that_require_other_mods) do original[k]=v end
assert(original["186992224"]=="mixer_emp_vaults_gigasdongo")
dofile("src/script/frontend/mod/zz_edh_east_sea_charter_playable.lua")
for _,f in ipairs(callbacks) do f() end
assert(mixer_factions_that_require_other_mods["186992224"]==nil)
assert(mixer_enabled_custom_factions.mixer_emp_vaults_gigasdongo==true)
assert(values.mixer_major_factions.mixer_emp_vaults_gigasdongo==true)
assert(values.mixer_lords_with_name_changes["186992224"]=="edh_heinrich_cb")
assert(#values.mixer_starting_unit_override.mixer_emp_vaults_gigasdongo==3)
for k,v in pairs(original) do
    if k~="186992224" then assert(mixer_factions_that_require_other_mods[k]==v) end
end
assert(#errors==0)
-- Re-entry must not invoke the native API on an already-enabled ID.
for _,f in ipairs(callbacks) do f() end
assert(#errors==0)
-- Library ordering fallback retries through ui-created without crashing.
mixer_enable_custom_faction=nil
dofile("src/script/frontend/mod/zz_edh_east_sea_charter_playable.lua")
assert(#errors==1)
print("PASS: real MIXER unlock/name/major-faction APIs; re-entry; all other hidden factions preserved")
