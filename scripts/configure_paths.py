from pathlib import Path
import json, gzip, shutil, hashlib
root=Path(__file__).resolve().parents[1]
parts_manifest=root/'data/raw/snapshot_parts.json'
if parts_manifest.exists():
 parts=json.loads(parts_manifest.read_text())
 assembled=b''.join((parts_manifest.parent/e['name']).read_bytes() for e in parts['parts'])
 if hashlib.sha256(assembled).hexdigest()!=parts['sha256']:raise ValueError('Source snapshot checksum mismatch')
 (parts_manifest.parent/parts['output']).write_bytes(assembled)
snapshot=root/'data/clean/FactSales.csv.gz' 
output=root/'data/clean/FactSales.csv'
if snapshot.exists():
 with gzip.open(snapshot,'rb') as source, output.open('wb') as target: shutil.copyfileobj(source,target)
f=root/'powerbi/Dashboard.SemanticModel/model.bim'
m=json.loads(f.read_text(encoding='utf-8-sig'))
folder=str((root/'data/clean').resolve()).replace('"','""')+'/'
for e in m['model']['expressions']:
 if e['name']=='DataRoot':e['expression']='"'+folder+'" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
f.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('DataRoot configured. Open powerbi/Dashboard.pbip and refresh.')
