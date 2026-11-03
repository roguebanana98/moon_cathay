"""Read-only native audit and private design presentation; never builds a mod."""
import csv, json, subprocess, html, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'reference/local/lord-vanilla/db'
OUT = ROOT / 'build/da-lien-skill-design'
OUT.mkdir(parents=True, exist_ok=True)
CFG = json.loads((ROOT/'config/local.json').read_text())

def read(t):
    with (DB/(t+'_tables/data__.tsv')).open(encoding='utf-8-sig', newline='') as f:
        a = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    return [dict(zip(a[0], x)) for x in a[2:]]

skills = {r['key']: r for r in read('character_skills')}
nodes = {r['key']: r for r in read('character_skill_nodes')}
items = read('character_skill_node_set_items')
effects = read('character_skill_level_to_effects_junctions')
details = read('character_skill_level_details')
links = read('character_skill_node_links')
sets = ['wh3_main_skill_node_set_cth_alchemist', 'wh3_main_skill_node_set_cth_astromancer', 'wh_dlc05_skill_node_set_jade_wizard']
audit = {}
for s in sets:
    ns = [nodes[i['item']] for i in items if i['set'] == s]
    keys = {n['character_skill_key'] for n in ns}
    nk = {n['key'] for n in ns}
    audit[s] = dict(nodes=ns, skills=[skills[k] for k in sorted(keys)],
        effects=[e for e in effects if e['character_skill_key'] in keys],
        levels=[d for d in details if d['skill_key'] in keys],
        links=[l for l in links if l['child_key'] in nk and l['parent_key'] in nk])
(OUT/'native-audit.json').write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding='utf-8')

rows = []
def add(group, name, key, points, gate, desc, custom=False):
    assert key in skills, key
    rows.append(dict(group=group, name=name, key=key, points=points, gate=gate, desc=desc,
                     custom=custom, icon_name=skills[key]['image_path']))

metal='wh_main_skill_all_magic_metal_'
life='wh_dlc05_skill_magic_life_wizard_'
magic='wh_main_skill_all_magic_all_'
add('Phép thuật', 'Searing Doom', metal+'01_searing_doom', 2, 'Cấp 1', 'Phép bombardment chống đội hình lính. Có sẵn bản cơ bản khi xuất hiện; 2 điểm nâng cấp theo native.')
add('Phép thuật', 'Earth Blood', life+'earth_blood', 3, 'Cấp 1', 'Hồi máu nhẹ theo vùng; không hồi sinh lính chết. 6 Winds ở bản cơ bản; giữ healing cap native.')
add('Phép thuật', 'Glittering Robe', metal+'04_glittering_robe', 3, 'Cấp 1', 'Tăng 60 giáp trong 44 giây; bản cơ bản cho một mục tiêu, overcast hỗ trợ theo vùng.')
add('Phép thuật', "Gehenna’s Golden Hounds", metal+'05_gehennas_golden_hounds', 3, 'Cấp 1', 'Vortex di chuyển gây sát thương lên đội hình lính; cần cẩn thận vị trí đồng minh.')
add('Phép thuật', 'Metalshifting', metal+'03_metalshifting', 1, 'Cấp 1', 'Giữ một lore passive native. Không cộng thêm Life Bloom để tránh hồi máu tự động mỗi lần niệm phép.')
add('Phép thuật', 'Evasion', magic+'06_evasion', 1, 'Cấp 7 + 4 điểm phép đầu', 'Giữ passive sinh tồn dành cho caster; nút nối sang nhóm phép nâng cao.')
add('Phép thuật', 'Transmutation of Lead', metal+'09_transmutation_of_lead', 3, 'Cấp 8 + Evasion', 'Hex giảm sức chiến đấu của đối phương; hỗ trợ bộ binh giữ tuyến.')
add('Phép thuật', 'The Dwellers Below', life+'the_dwellers_below', 3, 'Cấp 8 + Evasion', 'Phép sát thương vùng cao cấp cho cụm lính. 17 Winds ở bản cơ bản; không đổi thành sát thương miễn phí.')
add('Phép thuật', 'Earthing', magic+'07_earthing', 1, 'Cấp 8 + Evasion', 'Giảm 15 điểm phần trăm nguy cơ miscast theo effect native.')
add('Phép thuật', 'Magical Reserves', magic+'08_power_drain', 1, 'Cấp 8 + Evasion', 'Tăng 5 sức chứa dự trữ Winds của quân đoàn; không phải tự tạo Winds vô hạn.')
add('Phép thuật', 'Arcane Conduit', magic+'11_arcane_conduit', 1, 'Cấp 12 + 4 điểm nhóm nâng cao', 'Giữ cơ chế Arcane Conduit native hiện tại: passive, không thiết kế thành nút bấm cũ.')

add('Kỹ năng riêng', 'Moon Scholar', 'wh3_cp1_skill_cth_alchemist_unique_student_of_the_house_of_secrets', 1, 'Cấp 8', 'Đề xuất: −10% cooldown phép Metal và Life của Da Lien.', True)
add('Kỹ năng riêng', 'Silver Ward', 'wh3_cp1_skill_cth_alchemist_unique_steel_sheathing', 1, 'Cấp 12', 'Đề xuất: +20 giáp cho bản thân. Không cấp elixir hay cơ chế Alchemist đi kèm.', True)
add('Kỹ năng riêng', 'Deep Wells', magic+'08_power_drain', 1, 'Cấp 16', 'Đề xuất: +5 dự trữ Winds; cộng với Magical Reserves thành +10.', True)
add('Kỹ năng riêng', 'Moonlit Grace', 'wh3_cp1_skill_cth_alchemist_unique_alchemical_wrath', 1, 'Cấp 20', 'Đề xuất: +10% tốc độ và +8 melee defence cho bản thân; giúp thoát cận chiến.', True)
add('Kỹ năng riêng', 'Veil of the Moon', 'wh2_main_skill_all_immortality_hero', 1, 'Cấp 24', 'Đề xuất: −2 lượt hồi phục khi bị thương. Đây không phải ô mua Immortality.', True)
add('Kỹ năng riêng', 'Lunar Mastery', 'wh3_cp1_skill_cth_alchemist_unique_living_forge', 1, 'Cấp 28', 'Đề xuất: +10% spell mastery cho bản thân; phải nối cả effect và attribute cho phép mastery.', True)

add('Sinh tồn', 'Wind Harmony', 'wh3_main_skill_cth_all_unique_magic_resist', 1, 'Cấp 7', 'Native: +10% spell resistance cho bản thân.')
add('Sinh tồn', 'Ranged Discipline', 'wh3_main_skill_cth_all_unique_missile_resist', 1, 'Cấp 7', 'Native: +10% missile resistance cho bản thân.')
camp='wh2_main_skill_all_hero_'
add('Campaign', 'Increase Mobility', camp+'assist_army_increase_mobility', 3, 'Cấp 1 / 5 / 10', 'Native: nâng hiệu quả hỗ trợ di chuyển quân đoàn +5 / +10 / +15; phải gắn đúng action khi nhúng quân.')
add('Campaign', 'Boost Income', camp+'passive_boost_income', 3, 'Cấp 1 / 5 / 10', 'Native: nâng hiệu quả tác động thu nhập +2 / +4 / +6; áp dụng theo cơ chế vùng và action native.')
add('Campaign', 'Damage Building', camp+'hinder_settlement_damage_building', 3, 'Cấp 1 / 5 / 10', 'Native: +5 / +15 / +30 vào hiệu quả hành động phá công trình; không phải +% sát thương battle.')
add('Campaign', 'Assassinate', camp+'hinder_agent_assassinate', 3, 'Cấp 1 / 5 / 10', 'Native của Cathay Alchemist: nâng hiệu quả hành động ám sát Hero +3 / +8 / +15. Không tăng sức đấu tay đôi trong battle.')
add('Campaign', 'Hinder Replenishment', camp+'hinder_army_hinder_replenishment', 3, 'Cấp 1 / 5 / 10', 'Native: −10 / −20 / −40 vào hiệu quả cản bổ sung quân địch; cần giữ enable/action scaling nền.')
add('Campaign', 'Specialist', camp+'reduce_action_cost', 3, 'Cấp 1', 'Native: chi phí hành động −10 / −20 / −40%; cơ hội thành công +1 / +3 / +6 điểm phần trăm.')
add('Mentor', 'Mentor', 'wh3_main_skill_all_mentor_hero', 3, 'Cấp 30 / 40 / 50', 'Native Hero Mentor: chia sẻ kinh nghiệm theo mức 15 / 30 / 50. Không dùng mốc cấp 29 / 39 / 49 hiển thị: đó là rank nội bộ.')
assert sum(r['points'] for r in rows) == 51
(OUT/'design.json').write_text(json.dumps(dict(status='design_only_not_implemented', total_points=51, rows=rows), ensure_ascii=False, indent=2), encoding='utf-8')

# Resolve real native PNGs, with exact pack paths; no invented/AI icons.
packs = [Path(CFG['game'])/'data'/n for n in ['ui.pack','ui2.pack','ui3.pack','ui_3.pack']]
index={}
for pack in packs:
    result=subprocess.run([CFG['rpfm'],'-g','warhammer_3','pack','list','-p',str(pack)],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
    for line in result.stdout.splitlines():
        p=line.strip()
        if p.endswith('.png') and p.startswith('ui/'):
            index.setdefault(p,pack)
icons=OUT/'icons';icons.mkdir(exist_ok=True)
for row in rows:
    name=row['icon_name']
    candidates=['ui/campaign ui/skills/'+name,'ui/battle ui/ability_icons/'+name]
    path=next((p for p in candidates if p in index),None)
    if not path:
        matches=[p for p in index if p.endswith('/'+name)]
        assert matches, name
        path=matches[0]
    target=icons/name
    if not target.exists():
        subprocess.run([CFG['rpfm'],'-g','warhammer_3','pack','extract','-p',str(index[path]),'-f',path+';'+str(OUT/'native')],capture_output=True,check=True)
        shutil.copy2(OUT/'native'/path,target)
    row['icon']=str(target)
    row['native_icon_path']=path
    with Image.open(target) as im: im.verify()
(OUT/'icon-provenance.json').write_text(json.dumps([{k:r[k] for k in ['name','key','native_icon_path','custom']} for r in rows], ensure_ascii=False, indent=2),encoding='utf-8')

intro='Da Lien là Legendary Hero pháp sư con người của Agents of the Moon: đánh cụm lính, hồi máu nhẹ, tăng giáp. Bộ phép Metal/Life hỗn hợp; giữ tên và hình phép native để dễ nhận biết.'
notes=[
 'ĐÂY LÀ BẢN THIẾT KẾ ĐỂ DUYỆT. Chưa sửa DB, script, pack hay bản game v22. Tên skill riêng bằng ASCII khi đưa vào game; icon của chúng chỉ là artwork native minh họa, không kế thừa hiệu ứng của skill cho icon.',
 'Sáu phép chủ động: Searing Doom, Earth Blood, Glittering Robe, Golden Hounds, Transmutation of Lead và Dwellers Below. Ba phép gây sát thương vùng, một heal, một buff giáp và một hex. Không chọn Final Transmutation vì ưu tiên cụm lính; không chọn Regrowth/Life Bloom để giữ vai trò hồi máu phụ.',
 'Khởi đầu: Searing Doom cơ bản miễn phí qua hidden enable node; không tự cấp Earth Blood/Glittering Robe. 2 điểm Searing Doom chỉ nâng phép đã có. Những phép còn lại dùng 3 mức native: mở phép → overcast/cooldown → tối ưu chi phí/miscast. Lore passive Metalshifting phải được mua riêng.',
 'Gating đề xuất: 4 điểm đầu phải được tiêu trong nhóm Searing Doom, Earth Blood, Glittering Robe, Golden Hounds hoặc Metalshifting để mở Evasion ở cấp 7. Nhóm nâng cao gồm Lead, Dwellers, Earthing, Reserves mở sau Evasion ở cấp 8. Tiêu 4 điểm trong nhóm nâng cao mới mở Conduit từ cấp 12. Đây là mốc thiết kế riêng; native thường dùng điều kiện điểm/link, không áp nguyên mốc cấp này.',
 'Nhánh riêng gồm 6 ô độc lập, mở theo cấp và mỗi ô tốn 1 điểm. Không ép mua cả chuỗi để lấy Lunar Mastery. Các số cộng là đề xuất cân bằng, chưa đo hiệu quả trong game.',
 'Tổng mua tối đa: phép thuật 22 + riêng 6 + sinh tồn 2 + campaign 18 + Mentor 3 = 51 điểm. Ngân sách chuẩn 49 điểm từ tăng cấp 1→50, nếu không có điểm thưởng. Không thể max tất cả: nhánh battle/caster có thể giảm đầu tư hành động campaign. Không tính phép khởi đầu, immortality hoặc action nền vào chi phí.',
 'Ví dụ build cấp 50 dùng đủ 49 điểm: phép 22 + riêng 6 + sinh tồn 2 + Mobility 3 + Specialist 3 + Income 3 + Assassinate 3 + Hinder Replenishment 3 + Damage Building 1 + Mentor 3. Hai điểm Damage Building còn lại là lựa chọn đánh đổi. Đây là tổng cuối cây, không phải thứ tự auto-spend.',
 'Nền miễn phí/ẩn bắt buộc: immortality ngay khi nhận Legendary Hero; agent action enables và scaling; enable phép khởi đầu; lore/composite group chỉ liệt kê base spells và giữ đúng liên kết overcast. Giữ trait/equipment slots của living Hero; không đem regeneration, undead healing, crumbling, raising dead hay cơ chế Lord của Neferata vào.',
 'Không có ô mua mount ở phiên bản đầu vì chưa có model/animation cưỡi tương ứng. Không có nhánh đỏ Lord, Route Marcher Lord, Army of Renown hay Lightning Strike. Mobility là skill Hero hỗ trợ quân đoàn. Tạm không đưa hai action buff alchemy mới của Alchemist vào vì kit Da Lien dùng Glittering Robe và không giữ toàn bộ hệ alchemy.',
 'Campaign giữ bộ hành động thực của khung Cathay Alchemist hiện tại (engineer): Mobility, Income, Damage Building, Assassinate, Hinder Replenishment. Không tự thêm Wound, Block Army hay Steal Technology khi chưa đổi action framework. Các phần trăm hiệu quả action không đồng nghĩa tỷ lệ thành công cuối cùng: engine còn tính cấp, mục tiêu và bổ trợ khác.',
 'Khả thi: phép/overcast, caster basics, Mentor, resistance và campaign skills có donor native kiểm chứng trong DB. Nhánh riêng chủ yếu ghép effect native; Lunar Mastery cần attribute enable tương ứng. Phải kiểm thử cây hỗn hợp, passive trigger khi cast cả hai lore, tooltip/mana thực tế, friendly fire, heal cap, action menus và điểm/link mở khóa. Chưa khẳng định runtime hoặc chất lượng cân bằng trước các bài kiểm tra này.',
 'Cấp khi nhận qua quest chưa chốt. Bản thiết kế hoạt động từ cấp 1; nếu sau này nhận ở cấp 15, phải cấp đúng XP/điểm chưa dùng hoặc chọn preset rõ ràng, không tự lén mua skill. Prototype Long Vi vẫn dùng cây thử nghiệm Metal hiện có.'
]
groups=list(dict.fromkeys(r['group'] for r in rows))
style='''body{background:#101622;color:#e8edf4;font:16px/1.55 "Segoe UI",sans-serif;max-width:1200px;margin:auto;padding:40px}h1{font-size:36px;color:#edce8d}h2{color:#c3d7f1;margin-top:36px}.lead{max-width:1000px;color:#c4cfdd}.badge{font-size:12px;color:#e9c782}table{width:100%;border-collapse:collapse;background:#172132}td,th{text-align:left;padding:14px;border-bottom:1px solid #344154;vertical-align:top}td:first-child{min-width:240px}img{width:48px;height:48px;vertical-align:middle;margin-right:12px;object-fit:contain}small{color:#9aacc2}li{margin:12px 0}.note{padding:16px;background:#283144;border-left:4px solid #edce8d}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.card{padding:18px;background:#172132;border:1px solid #344154}.card strong{display:block}.card img{float:left}a{color:#c4ddff}@media(max-width:800px){.grid{grid-template-columns:1fr}body{padding:18px}}'''
doc=['<!doctype html><html lang="vi"><meta charset="utf-8"><title>Da Lien — Skill tree design</title><style>'+style+'</style><h1>DA LIEN · Skill tree đề xuất</h1><div class="note">BẢN DUYỆT THIẾT KẾ · 03/11/2026 · CHƯA ĐƯA VÀO MOD</div><p class="lead">'+intro+'</p><p>26 ô kỹ năng mua điểm · 51 điểm tối đa · 6 phép chủ động · 6 kỹ năng riêng. Mốc cấp dưới đây là cấp nhân vật hiển thị.</p>']
md=['# Da Lien — Thiết kế skill tree (chưa triển khai)', '',intro,'','Ngày: 03/11/2026. Nguồn kiểm tra: DB native local; audit đầy đủ và icon provenance tại build/da-lien-skill-design/.','']
for group in groups:
    doc.append('<h2>'+group+'</h2><table><tr><th>Kỹ năng / icon native</th><th>Điểm · Mở khóa</th><th>Chức năng</th></tr>')
    md+=['## '+group,'','| Kỹ năng | Điểm tối đa | Mở khóa | Thiết kế |','|---|---:|---|---|']
    for r in rows:
        if r['group'] != group:
            continue
        badge='ĐỀ XUẤT RIÊNG · ICON MINH HỌA' if r['custom'] else 'SKILL / EFFECT NATIVE'
        doc.append('<tr><td><img src="icons/'+html.escape(r['icon_name'])+'"><strong>'+html.escape(r['name'])+'</strong><br><small>'+badge+'</small></td><td>'+str(r['points'])+' điểm<br>'+r['gate']+'</td><td>'+html.escape(r['desc'])+'</td></tr>')
        md.append('| '+r['name']+' | '+str(r['points'])+' | '+r['gate']+' | '+r['desc']+' |')
    doc.append('</table>');md.append('')
doc.append('<h2>Quy tắc, tính đầy đủ và khả năng triển khai</h2><ol>')
for n in notes:
    doc.append('<li>'+html.escape(n)+'</li>');md+=['- '+n,'']
doc.append('</ol><p><small>Icon trích từ game cài local để minh họa riêng; không phải artwork mới hoặc tài nguyên phát hành công khai. Native-audit.json ghi các node, link, level, effect của ba cây tham chiếu.</small></p></html>')
(OUT/'Da_Lien_Skill_Tree.html').write_text('\n'.join(doc),encoding='utf-8')
(ROOT/'docs/DA-LIEN-SKILL-TREE-DESIGN.md').write_text('\n'.join(md),encoding='utf-8')

# Compact contact sheet with original game artwork next to every skill name.
W=1800
font='C:/Windows/Fonts/segoeui.ttf'
bold='C:/Windows/Fonts/segoeuib.ttf'
f=lambda size,b=False:ImageFont.truetype(bold if b else font,size)
canvas=Image.new('RGB',(W,2220),'#101622');d=ImageDraw.Draw(canvas)
d.text((55,35),'DA LIEN',font=f(48,True),fill='#edce8d')
d.text((55,100),'SKILL TREE ĐỀ XUẤT · CHƯA ĐƯA VÀO MOD',font=f(25,True),fill='#d3dfec')
d.text((55,145),'AOE lên lính  /  Hồi máu nhẹ  /  Buff giáp  •  26 ô  •  51 điểm tối đa',font=f(23),fill='#aebfd4')
y=205
for group in groups:
    d.text((55,y),group.upper(),font=f(26,True),fill='#edce8d');y+=48
    rs=[r for r in rows if r['group']==group]
    for j,r in enumerate(rs):
        x=55+(j%3)*570;cy=y+(j//3)*112
        d.rounded_rectangle((x,cy,x+550,cy+101),radius=10,fill='#1b283a')
        icon=Image.open(r['icon']).convert('RGBA');icon.thumbnail((64,64))
        canvas.paste(icon,(x+12,cy+17),icon)
        name=r['name'].replace('Gehenna’s Golden Hounds','Golden Hounds')
        d.text((x+88,cy+12),name,font=f(22,True),fill='#f1f4f8')
        gate=r['gate'].replace('nhóm nâng cao','nhóm sau').replace('điểm phép đầu','điểm đầu')
        d.text((x+88,cy+44),str(r['points'])+' điểm · '+gate,font=f(17),fill='#b5c6da')
        d.text((x+88,cy+70),'Đề xuất riêng · icon minh họa' if r['custom'] else 'Kỹ năng / effect native',font=f(16),fill='#d9bd83' if r['custom'] else '#95b7b4')
    y+=((len(rs)+2)//3)*112+25
d.text((55,y),'Khởi đầu: Searing Doom cơ bản + Immortality miễn phí. Không tốn điểm cho node nền.',font=f(22),fill='#c5d3e5');y+=38
d.text((55,y),'Chi tiết chức năng, đường mở khóa, build 49 điểm và giới hạn: xem bản HTML đi kèm.',font=f(22),fill='#c5d3e5');y+=55
canvas.crop((0,0,W,y)).save(OUT/'Da_Lien_Skill_Tree.png')
print(json.dumps(dict(rows=len(rows),points=sum(r['points'] for r in rows),native_sets=len(audit),icons=len(list(icons.glob('*.png'))),output=str(OUT),height=y)))

