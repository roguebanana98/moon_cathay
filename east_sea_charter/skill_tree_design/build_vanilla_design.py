import csv,json,re,base64,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
P=R/'vanilla_reference/db'
def read(t):
    with (P/(t+'_tables/data__.tsv')).open(encoding='utf-8-sig',newline='') as f:
        rows=csv.DictReader(f,delimiter='\t');next(rows);return list(rows)
skills={x['key']:x for x in read('character_skills')}
nodes={x['key']:x for x in read('character_skill_nodes')}
items=read('character_skill_node_set_items');effects=read('character_skill_level_to_effects_junctions');links=read('character_skill_node_links')
def resolve(s):
    return re.sub(r'\{\{tr:character_skills_localised_name_([^}]+)\}\}',lambda m:skills.get(m[1],{}).get('localised_name',m[1]),s)
rename={
'Hold the Line!':'Giữ Vững Đầu Cầu','Stand Your Ground!':'Đứng Sau Ta','Full Plate Armour':'Thép Nhà Adlerhorst','Survival Instincts':'Dạn Dày Viễn Chinh','Statesman':'Người Mang Hiến Chương','Leader of Men':'Uy Danh Phó Vương','Guardian':'Đại Bàng Che Chở',
'Harmonic Convergence':'Điềm Lành Đền Cổ','Roiling Skies':'Bầu Trời Của Ngọc Xà','Wind Blast':'Hơi Thở Naga','Curse of the Midnight Wind':'Lời Nguyền Đền Rắn',"Urannon's Thunderbolt":'Lôi Kích Ngọc Xà','Comet of Casandora':'Thiên Thạch Đền Cổ','Chain Lightning':'Ngũ Xà Lôi Quang','Aura of the Lady':'Hào Quang Người Giữ Đền',"Lady’s Mantle":'Áo Choàng Lời Thề',"Lady�s Mantle":'Áo Choàng Lời Thề','Greater Arcane Conduit':'Mạch Phép Đền Cổ'}
data={'h':[],'s':[]}
def make(key,group,source,node=None,note=''):
    s=skills[key];original=resolve(s['localised_name']).strip()
    actions={'{{tr:agent_action_name_replenish_troops}}':'Replenish Troops','{{tr:agent_action_name_cleanse_corruption}}':'Cleanse Corruption','{{tr:agent_action_name_steal_technology}}':'Steal Technology','{{tr:agent_action_name_wound}}':'Wound','{{tr:agent_action_name_block_army}}':'Block Army'}
    original=actions.get(original,original)
    es=[e for e in effects if e['character_skill_key']==key]
    iconpath=R/'vanilla_reference/ui/campaign ui/skills'/s['image_path']
    if not iconpath.exists():
        rel='ui/battle ui/ability_icons/'+s['image_path']
        iconpath=R/'vanilla_reference'/rel
        if not iconpath.exists():
            subprocess.run([r'D:\Mod TW3k\rpfm-v4.5.4-x86_64-pc-windows-msvc\rpfm_cli.exe','-g','warhammer_3','pack','extract','-p',r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data\ui.pack','-f',rel+';'+str(R/'vanilla_reference')],check=True,stdout=subprocess.DEVNULL)
    assert iconpath.exists(),iconpath
    parents=[] if not node else [l for l in links if l['child_key']==node['key']]
    return dict(key=key,original=original,name=rename.get(original,original),group=group,source=source,description=resolve(s['localised_description']) or 'Dùng nguyên tooltip và thông số của skill nguồn.',ranks=max([int(e['level']) for e in es] or [1]),note=note or 'Giữ cấp mở, số bậc và điều kiện nối của cây gốc.',icon='data:image/png;base64,'+base64.b64encode(iconpath.read_bytes()).decode(),image_path=s['image_path'],effects=es,node=node,links=parents)
for hero,se in [('h','wh_main_skill_node_set_emp_general'),('s','wh_main_skill_node_set_brt_damsel')]:
    ns=[nodes[x['item']] for x in items if x['set']==se and x['mod_disabled']=='false']
    for n in sorted(ns,key=lambda n:(int(n['indent']),int(n['tier']))):
        s=skills[n['character_skill_key']];indent=int(n['indent']);key=s['key']
        if indent>5 or n['visible_in_ui']!='true' or '[HIDDEN]' in s['localised_name']:continue
        if key in ['wh3_dlc25_skill_emp_all_unique_mark_of_hysh','wh_main_skill_emp_lord_unique_general_imperial_pegasus','wh_dlc07_skill_brt_damsel_heavens_unique_unicorn','wh_main_skill_brt_wizard_unique_damsel_warhorse']:continue
        if hero=='s' and key=='wh_main_skill_all_magic_all_11_arcane_conduit':
            data[hero].append(make('wh2_dlc14_skilll_all_magic_all_greater_arcane_conduit','Phép thuật · Heavens','High Elf Archmage (Heavens)',n,'Thay Arcane Conduit bằng Greater Arcane Conduit; giữ cửa mở cuối nhánh phép của Damsel. Không nhận cả hai.'));continue
        group=({0:'Kỹ năng chung & thú cưỡi',1:'Chuyên môn General · giữ lựa chọn loại trừ gốc',2:'Chỉ huy General · giữ lựa chọn loại trừ gốc',3:'Cận chiến · ưu tiên chống chịu',4:'Quân đội Empire',5:'Chiến dịch · đoàn viễn chinh'} if hero=='h' else {0:'Bảo hộ & kỹ năng chung',2:'Phép thuật · Heavens',5:'Chiến dịch · học giả Khuresh'})[indent]
        data[hero].append(make(key,group,'General of the Empire' if hero=='h' else 'Damsel (Heavens)',n))
data['h'].append(make('wh2_dlc10_skill_hef_handmaiden_protector_2','Bổ sung từ class khác','High Elf Handmaiden',note='Skill bổ sung. Đề xuất mở cấp 11 theo skill nguồn; 1 bậc. Dùng nguyên Guardian, áp dụng theo đối tượng gốc, không giới hạn riêng Sariwa.'))
for h in data:
    assert len({s['key'] for s in data[h]})==len(data[h])
out={h:[{k:v for k,v in x.items() if k!='icon'} for x in data[h]] for h in data}
(R/'skills-vanilla-v2.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
md=['# Heinrich & Sariwa — thiết kế skill tree v2: skill có sẵn trong game','','Bản này thay thế thiết kế 48 skill tự tạo trước đó. Chỉ thiết kế, chưa sửa hoặc xuất pack game. Nguồn đối chiếu trực tiếp: db.pack và ui.pack trong bản game đang cài.','','## Nguyên tắc','','- Chỉ dùng skill, hiệu ứng và icon vanilla. Tên mới chỉ là đề xuất localization; không sửa chỉ số, mana, hồi chiêu, loại sát thương, VFX hay animation.','- Heinrich lấy General of the Empire làm nền. Sariwa lấy Damsel (Heavens) làm nền để có Thunderbolt, Comet và Chain Lightning phù hợp vai trò sát thương tầm xa.','- Giữ cửa điểm, cấp mở, bậc nâng và các lựa chọn loại trừ của cây gốc. Thêm Guardian cho Heinrich; Sariwa thay Arcane Conduit bằng Greater Arcane Conduit từ Archmage. Không cộng hai conduit.','- Heinrich giữ Barded Warhorse và Imperial Griffon; bỏ Pegasus khỏi thiết kế. Sariwa đi bộ theo mô tả, bỏ Warhorse và Unicorn khỏi thiết kế này.','- Không đưa trait bẩm sinh, skill ẩn hoặc Mark of Hysh phụ thuộc cơ chế khác vào cây phân điểm.','- Không tạo bonus cặp đôi, phép Naga mới, skill kiếm mới, nhánh chính trị hoặc hiệu ứng thuế/cảng tự chế. Kiếm Sariwa vẫn là vũ khí model; không cần thêm nhánh cận chiến.','','## Hai bổ sung quan trọng','','- **Guardian → Đại Bàng Che Chở**, nguồn Handmaiden: giúp Heinrich che chở nhân vật đồng minh gần mình bằng đúng ability Guardian. Không viết lại thành aura chỉ dành cho Sariwa.','- **Greater Arcane Conduit → Mạch Phép Đền Cổ**, nguồn Archmage (Heavens): tăng năng lực pháp sư của Sariwa bằng ability có sẵn, thay cho Arcane Conduit thường.','','Các hiệu ứng số cụ thể và liên kết DB nguyên bản được lưu trong skills-vanilla-v2.json; không suy diễn số từ tên skill. Tên gốc luôn ghi cạnh tên đề xuất để dễ đối chiếu.']
for hero,title in [('h','Heinrich von Adlerhorst'),('s','Sariwa')]:
    md+=['','## '+title]
    for group in dict.fromkeys(x['group'] for x in data[hero]):
        md+=['','### '+group,'','| Icon gốc | Skill gốc | Tên đề xuất | Nguồn / ghi chú |','|---|---|---|---|']
        for x in data[hero]:
            if x['group']==group:
                ip=R/'vanilla_reference/ui/campaign ui/skills'/x['image_path']
                if not ip.exists():ip=R/'vanilla_reference/ui/battle ui/ability_icons'/x['image_path']
                path=ip.as_posix().replace(' ','%20')
                md.append(f"| ![icon]({path}) | {x['original']} | {x['name']} | {x['source']}. {x['note']} |")
        md+=['','Khóa skill để đối chiếu:']
        md += ['- `'+x['key']+'`' for x in data[hero] if x['group']==group]
(R/'Heinrich-Sariwa-Skill-Tree-v2-Vanilla.md').write_text('\n'.join(md)+'\n',encoding='utf8')
fragment=(R/'vanilla-review-template.html').read_text(encoding='utf8').replace('__DATA__',json.dumps(data,ensure_ascii=False,separators=(',',':')))
target=Path('C:/Users/ADMIN/.codex/visualizations/2026/11/02/01a19c9d-9880-7ae2-8e9c-08d274cea911/vanilla-skill-review.html')
target.write_text(fragment,encoding='utf8')
assert target.stat().st_size<1000000
print('Verified native skill keys, effects, icons:',{h:len(x) for h,x in data.items()},'HTML bytes',target.stat().st_size)
