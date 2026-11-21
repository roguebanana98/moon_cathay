"""Expose the existing IEE campaign slot; preserve every v4 gameplay payload."""
import csv,hashlib,json,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/east-sea-playable';O.mkdir(parents=True,exist_ok=True)
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
BASE=json.loads((R/'build/east-sea-refuge/deployment.json').read_text());P=Path(BASE['deployed_path'])
assert hashlib.sha256(P.read_bytes()).hexdigest()==BASE['sha256']
PACK=O/'edh_east_sea_charter_playable_v5.pack';assert not PACK.exists(),'Preserve existing builds'
F='mixer_emp_vaults_gigasdongo';files=[]
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
 return a[:2],[dict(zip(a[0],r)) for r in a[2:]]
def write(t,head,rows):
 h,m=head;p='db/'+t+'_tables/edh_playable';m=m.copy();m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([h,m]+[[r[k] for k in h] for r in rows])
 files.append(p)
h,rs=read(R/'reference/local/mixer/db/frontend_faction_leaders_tables/zzz_mixu_startpos.tsv');row=next(r for r in rs if r['key']==F)
# Retain the registered party key/startpos_map. The engine uses it to select the
# existing character; the campaign subtype is Heinrich, never mixer_dummy.
row.update(character_image='ui/portraits/faction_leaders/edh_heinrich_cb_0.png',agent_subtype_record='edh_heinrich_cb',uniform='composite_scene/lord_selection/empire_provinces/emperor_karl_franz.csc',voiceover='',video='Front_end_selection_movies/franz_front_end',loading_screen_image='ui/loading_ui/load_images/campaign_empire1.png',prelude_battle='',show_full_intro_option='false',difficulty='normal')
write('frontend_faction_leaders',h,[row])
loc={
 'frontend_faction_leaders_frontend_description_'+F:'Heinrich von Adlerhorst leads East Sea Charter from Dai Loa and Preenn, accompanied by the sorceress Sariwa.',
 'frontend_faction_leaders_localised_description_'+F:'Lead an Empire expedition in the eastern seas. Heinrich commands the starting army; Sariwa begins beside him as an independent Hero.',
 'frontend_faction_leaders_loading_screen_text_'+F:'East Sea Charter holds Dai Loa and Preenn. Heinrich von Adlerhorst and Sariwa defend its place in the eastern seas.',
 'frontend_faction_leaders_localised_action_points_'+F:'Heinrich von Adlerhorst: Legendary Lord.||Sariwa: starting wizard Hero.||Starting settlements: Dai Loa and Preenn.',
 'frontend_factions_localised_info_'+F:'East Sea Charter - an Empire faction based at Dai Loa.',
 'frontend_factions_localised_playstyle_'+F:'Empire combined arms, led by Heinrich von Adlerhorst with Sariwa providing magical support.',
 'frontend_factions_localised_mechanics_'+F:'Empire recruitment and technology.||Sanctuary of the Moon: Heinrich and Sariwa seek refuge with Agents of the Moon after the Charter falls, and return when it is restored.'}
p='text/db/edh_playable.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
files.append(p);script='script/frontend/mod/zz_edh_east_sea_charter_playable.lua';files.append(script)
def cli(*args):
 result=subprocess.run([C['rpfm'],'-g','warhammer_3',*map(str,args)],capture_output=True,text=True)
 with (O/'build.log').open('a',encoding='utf-8') as f:f.write(result.stdout+result.stderr)
 if result.returncode:raise RuntimeError(result.stdout+result.stderr)
 return result.stdout
shutil.copy2(P,PACK)
for p in files:
 if p.startswith(('db/','text/')):cli('pack','add','-p',PACK,'-t',C['schema'],'-f',str(O/(p+'.tsv'))+';'+p)
 else:cli('pack','add','-p',PACK,'-f',str(R/'src'/p)+';'+p)
def payloads(p):
 raw=p.read_bytes();assert raw[:4]==b'PFH5';_,_,ds,fc,fs,_=struct.unpack('<6I',raw[4:28]);pos=28+ds;stop=pos+fs;entries=[]
 for _ in range(fc):
  size,compression=struct.unpack('<IB',raw[pos:pos+5]);pos+=5;assert compression==0;end=raw.index(0,pos);key=raw[pos:end].decode().replace('\\','/');pos=end+1;entries.append((key,size))
 assert pos==stop;result={}
 for key,size in entries:result[key]=raw[pos:pos+size];pos+=size
 assert pos==len(raw);return {k:v for k,v in result.items() if not k.endswith('.rpfm_reserved')}
before=payloads(P);after=payloads(PACK);assert set(after)-set(before)==set(files);assert all(after[k]==v for k,v in before.items())
assert row['character_image'] in after
Q=R/'reference/local/edh-playable-roundtrip';cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','/;'+str(Q))
for p in files:
 if p.startswith(('db/','text/')):
  a,z=read(O/(p+'.tsv')),read(Q/(p+'.tsv'));assert a[0][0]==z[0][0] and a[1]==z[1],p
 else:assert after[p]==(R/'src'/p).read_bytes()==(Q/p).read_bytes()
report=dict(pack=str(PACK),sha256=hashlib.sha256(PACK.read_bytes()).hexdigest(),base_pack=str(P),base_sha256=BASE['sha256'],added_payloads=files,all_v4_payloads_byte_identical=True,startpos_and_gameplay_unchanged=True,db_loc_roundtrip=True,frontend_character_id='186992224',campaign='cr_combi_expanded',faction=F,static_validation='passed',runtime_verified=False,game_testing_deferred_by_user=True,preview_scene='Native Karl Franz frontend scene; custom Heinrich portrait/subtype. A bespoke selection scene is not authored.',dependency_sha256=BASE['dependency_sha256'])
(O/'build-report.json').write_text(json.dumps(report,indent=2));print('PASS: frontend unlock, Heinrich presentation, three additions; all v4 gameplay/startpos byte-identical')
