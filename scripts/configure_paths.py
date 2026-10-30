from pathlib import Path
import json, gzip, shutil
root=Path(__file__).resolve().parents[1]
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
