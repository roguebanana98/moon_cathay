"""Replace only the registered starting leader; add existing character assets by dependency."""
import csv,hashlib,importlib.util,json,lzma,shutil,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
s=importlib.util.spec_from_file_location('b',R/'tools/Build-Province-Candidate.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/east-sea-characters';O.mkdir(parents=True,exist_ok=True)
BASE=R/'build/east-sea-faction/edh_east_sea_charter_faction_v2.pack'
ASSETS=Path('D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/edh_heinrich_sariwa_v4.pack')
A=R/'reference/local/edh-campaign-assets';Q=R/'reference/local/edh-campaign-base';files=[]
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='0e929934ae0056d056b0db4abf532c8cf4c7fd23c296a48ce1da0952be7c6146'
assert hashlib.sha256(ASSETS.read_bytes()).hexdigest()=='0ef0b3d05dc9599013c31a5014a1e5bd3d24d5e4cc75a34cde53a5c418957239'
def cli(*args):
 p=subprocess.run([C['rpfm'],'-g','warhammer_3',*map(str,args)],capture_output=True,text=True)
 with (O/'build.log').open('a',encoding='utf-8') as f:f.write(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout
cli('pack','extract','-p',BASE,'-t',C['schema'],'-F','/;'+str(Q))
cli('pack','extract','-p',ASSETS,'-t',C['schema'],'-F','db;'+str(A),'-F','ui/portraits;'+str(A))
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
 return a[:2],[dict(zip(a[0],r)) for r in a[2:]]
def write(t,head,rows):
 h,m=head;p='db/'+t+'_tables/edh_campaign_characters';m=m.copy();m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([h,m]+[[r[k] for k in h] for r in rows])
 files.append(p)
for t in ['agent_subtypes','main_units']:
 rs=[]
 for key in ['edh_heinrich_cb','edh_sariwa']:
  head,rows=read(A/'db'/(t+'_tables')/(key+'.tsv'));assert len(rows)==1;r=rows[0]
  if t=='agent_subtypes':
   r.update(auto_generate='false',cap='1',recruitable='true',can_be_loaned='false')
   if key=='edh_heinrich_cb':r['recruitment_category']='legendary_lords'
   # Same as Karl Franz/Ulrika: this is the reusable-character import/export
   # setting, not ordinary campaign-save persistence. Keep the native LL/LH value.
   assert r['saving_settings']=='cannot_be_loaded_in_campaign'
  else:r.update(campaign_cap='1',restrict_xp_gain_in_campaign='false')
  rs.append(r)
 write(t,head,rs)
head,_=read(R/'reference/local/lord-vanilla/db/faction_agent_permitted_subtypes_tables/data__.tsv')
write('faction_agent_permitted_subtypes',head,[dict(agent=a,faction='mixer_emp_vaults_gigasdongo',subtype=k,mod_disabled='false') for a,k in [('general','edh_heinrich_cb'),('wizard','edh_sariwa')]])
# Remove test-only display suffixes in the new campaign presentation.
p='text/db/edh_campaign_characters.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'',''],['land_units_onscreen_name_edh_heinrich_cb','Heinrich von Adlerhorst','true'],['agent_subtypes_onscreen_name_override_edh_heinrich_cb','Heinrich von Adlerhorst','true']])
files.append(p)
source=Q/'campaigns/cr_combi_expanded/startpos.esf';outer=b.Document(source.read_bytes());root,_=outer.decode(16)
n=next(n for n in b.walk(root) if n['name']=='COMPRESSED_DATA');payload,info=n['groups'][0][:2];length,props=info['groups'][0][:2]
raw=lzma.decompress(props+struct.pack('<Q',length)+payload,format=lzma.FORMAT_ALONE);(O/'base.raw.esf').write_bytes(raw)
d=b.Document(raw);patches={};audit=[]
def locate(name,near,index,value):
 hits=[]
 for pos in range(near-1024,near+1024):
  try:
   if d.header(pos)[4]==name:
    node,_=d.decode(pos)
    if node['groups'][0][index]==value:hits.append(node)
  except (AssertionError,KeyError,ValueError,IndexError,struct.error):pass
 assert len(hits)==1,(name,len(hits));return hits[0]
details=locate('CHARACTER_DETAILS',67213897,4,515)
unit=locate('UNIT',27577000,0,2454)
assert details['groups'][0][13]=='wh_main_emp_lord'
def field(node,index,old,new):
 a,z,value=d.children(node['offset'])[index];assert value==old,(node['name'],index,value,old)
 assert isinstance(new,str);patches[a]=d.add_string(new);audit.append(dict(node=node['name'],offset=a,index=index,old=old,new=new))
field(details,13,'wh_main_emp_lord','edh_heinrich_cb')
field(details,28,'wh_main_art_set_emp_general_050','edh_heinrich_cb_art')
art=next(n for n in b.walk(details) if n['name']=='CHARACTER_DETAILS_ART_SET_INFO')
field(art,4,'wh_main_emp_lord','edh_heinrich_cb');field(art,5,'wh_main_art_set_emp_general_05','edh_heinrich_cb_art')
skills=next(n for n in b.walk(details) if n['name']=='CAMPAIGN_SKILLS')
field(skills,1,'wh_main_skill_node_set_emp_general','edh_heinrich_skill_node_set')
for node in b.walk(details):
 if node['name']=='CHARACTER_NAME_ELEMENT':
  loc=next(n for n in b.walk(node) if n['name']=='CAMPAIGN_LOCALISATION')
  kind=node['groups'][0][1]
  if kind in ['forename','family_name']:
   field(loc,0,loc['groups'][0][0],'names_name_'+('1800412610' if kind=='forename' else '1800412611'))
flags=d.children(details['offset'])[8];assert flags[2]==['male','is_immortal']
encoded=b''.join(d.add_string(k)[1:] for k in ['male','is_immortal','is_named_character']);patches[flags[0]]=b'\x4f'+b.var(len(encoded))+encoded
u=next(n for n in b.walk(unit) if n['name']=='UNIT_RECORD_KEY');field(u,0,'wh_main_emp_cha_general_0','edh_heinrich_cb')
edited=d.rewrite(patches)
# Store selected before records for an independent reversal check.
(O/'startpos-changes.json').write_text(json.dumps(dict(details_offset=details['offset'],unit_offset=unit['offset'],changes=audit,named_immortal_flags=True,leader_character_id_preserved=515,general_unit_id_preserved=2454,patch_offsets=sorted(patches)),indent=2))
prop=props[0];filters=[{'id':lzma.FILTER_LZMA1,'dict_size':int.from_bytes(props[1:5],'little'),'lc':prop%9,'lp':(prop//9)%5,'pb':prop//45}]
packed=lzma.compress(edited,format=lzma.FORMAT_RAW,filters=filters);assert lzma.decompress(packed,format=lzma.FORMAT_RAW,filters=filters)==edited
encoded=outer.rewrite({outer.children(n['offset'])[0][0]:b'\x46'+b.var(len(packed))+packed,outer.children(info['offset'])[0][0]:b'\x08'+struct.pack('<I',len(edited))})
(O/'startpos.esf').write_bytes(encoded)
# Reuse approved portrait artwork/settings to add the faction leader panel.
donor=A/'ui/portraits/portholes/portrait_settings__edh_heinrich_cb.bin';jp=O/'portrait-leader.json';cli('portrait-settings','to-json','-b',donor,'-j',jp)
portrait=json.loads(jp.read_text());assert portrait['entries'][0]['id']=='edh_heinrich_cb_art'
imagepath='ui/portraits/faction_leaders/edh_heinrich_cb_0.png'
for variant in portrait['entries'][0]['variants']:variant.update(file_diffuse=imagepath,faction_leader=True)
jp.write_text(json.dumps(portrait,indent=2));internal='ui/portraits/faction_leaders/portrait_settings__edh_heinrich_cb.bin';bp=O/internal;bp.parent.mkdir(parents=True,exist_ok=True);cli('portrait-settings','from-json','-j',jp,'-b',bp)
shutil.copy2(A/'ui/portraits/portholes/no_culture/edh_heinrich_cb_0.png',O/imagepath);files.extend([internal,imagepath])
pack=O/'edh_east_sea_charter_characters_v3.pack';assert not pack.exists();shutil.copy2(BASE,pack)
cli('pack','add-dependency-pack','-p',pack,'-d',ASSETS.name)
script='script/campaign/mod/edh_east_sea_charter_start.lua'
cli('pack','add','-p',pack,'-f',str(O/'startpos.esf')+';campaigns/cr_combi_expanded/startpos.esf','-f',str(R/'src'/script)+';'+script)
for p in files:cli('pack','add','-p',pack,*(['-t',C['schema']] if p.startswith(('db/','text/')) else []),'-f',str(O/(p+'.tsv') if p.startswith(('db/','text/')) else O/p)+';'+p)
report=dict(pack=str(pack),sha256=hashlib.sha256(pack.read_bytes()).hexdigest(),base_pack=str(BASE),base_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),asset_pack=str(ASSETS),asset_sha256=hashlib.sha256(ASSETS.read_bytes()).hexdigest(),files=files+[script,'campaigns/cr_combi_expanded/startpos.esf'],runtime_verified=False,deployed=False,new_game_only=True)
(O/'build-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
