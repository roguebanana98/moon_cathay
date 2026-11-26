# Native recruitment tab reused for Bastion - 2026-11-23

Implements the user's safer alternative to hiding an empty Celestial General tab. Bastion's recruitment_category becomes wh3_dlc24_cth_celestial_general. Assault retains its own mc_assault_general category, order4 after native CG order3. The unused private mc_bastion_general category row is removed, so no separate empty Bastion category remains.

The native category label remains Celestial General because it is shared with other Cathay factions. The character entry inside it is Bastion General. Original native Yin/Yang Celestial General subtypes remain disabled for Agents of the Moon, and Assault/Bastion permissions are unchanged. No global localization, native category, UI layout or runtime UI callbacks are changed.

Built directly on the rollback v26 baseline. The failed v27/v28 tab-hiding script is absent. Only two existing DB payloads differ: the two-generals subtype table (one Bastion category field) and the private category table (Bastion row removed, Assault order4). Names, stats, skills, mounts, graphics, other heroes and all remaining scripts are byte-identical to v26.

Checks: exact changed-payload/field audit, category membership and native subtype permission assertions, RPFM DB roundtrip and zero blocking diagnostics. Deployed/enabled mc_moonshadow_heroes_v29_general_tabs.pack; v26 retained disabled. The old active pack's load-order slot9 is preserved, with launcher backups. No saves, native or Workshop files modified. No game launch or runtime UI/crash resolution confirmation; reopening recruitment in-game remains the live check.

Tools: Build-Moon-General-Recruitment-Tabs.py and Deploy-Moon-General-Recruitment-Tabs.py. Reports: build/moon-v29-general-tabs. Full current DB reference: reference/local/moon-v29-roundtrip/db.
