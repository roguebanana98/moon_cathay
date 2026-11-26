"""Freeze the user-approved Da Anh Legendary Hero appearance checkpoint."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];SOURCE=R/'build/celestial-concubines-dual-knives/celestial-concubine-01-closed-chest-textured.blend';O=R/'assets/working/da-anh';O.mkdir(parents=True,exist_ok=True);OUT=O/'da-anh-legendary-hero.blend'
assert not OUT.exists(),'Keep existing checkpoints'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;scene.name='Da Anh | Legendary Hero'
rig=bpy.data.objects['Body_01_native_humanoid01e'];rig.parent.name='Da Anh | Approved body01 head01';rig.name='Da Anh | Native humanoid01e'
scene['character_key']='mc_da_anh';scene['character_name']='Da Anh';scene['character_role']='Legendary Hero';scene['appearance_status']='User approved';scene['engine_integration_status']='Pending; v7 runtime still has previous Khainite appearance and 01d sword-handbow links'
scene['source_mod']='GrandCathay_CelestialConcubines_ENG.pack';scene['body_variant']=1;scene['head_variant']=1
notes=bpy.data.texts.new('DA ANH - APPROVED APPEARANCE');notes.write('Approved for Da Anh Legendary Hero. Celestial Concubines body01 and head01; fitted black torso/arm/leg fabric; original charcoal cloth extended over both chest openings; separate gold ornaments and dragon heads hidden, two shoulder plates retained; structural footwear gold recoloured charcoal. Two Dark Society Death Squad knives fitted to current finger/palm geometry. Editable native humanoid01e skeleton and original weights retained. Preview actions are native hu1e_sword_and_shield. Runtime v7 remains unchanged: Da Anh previously uses humanoid01d sword-and-handbow, ranged category, ammo50. Engine conversion must resolve runtime rig/animation/weapon links together; simply replacing the VMD would be incorrect. Hidden parts and original variants preserved as backups. No game or save changes. No Git upload.\n')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
used={s.material for o in scene.objects if o.type=='MESH' and not o.hide_get() for s in o.material_slots if s.material}
images={n.image for m in used if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
assert all(im.packed_file for im in images if im.source=='FILE');assert not bpy.data.libraries
manifest=dict(character='Da Anh',role='Legendary Hero',character_key='mc_da_anh',blend=OUT.name,sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),approved_source=str(SOURCE),source_mod='GrandCathay_CelestialConcubines_ENG.pack',body=1,head=1,skeleton='humanoid01e',bones=len(rig.data.bones),weapons=['ninja_knife_1','ninja_knife_2'],preview_animation='hu1e_sword_and_shield',packed_used_images=len(images),linked_libraries=0,status='appearance_approved_runtime_integration_pending',deployed=False,runtime_verified=False)
(O/'checkpoint.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2),flush=True)
