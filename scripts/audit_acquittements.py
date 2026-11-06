"""Inventorier les événements exportés sans exposer leurs éventuelles valeurs."""
import concurrent.futures,glob,openpyxl,collections,json,argparse
from pathlib import Path
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Inventaire des colonnes et événements : recherche de clics/acquittements explicites.')
parser.add_argument('--sources',type=Path,required=True)
args=parser.parse_args()
def run(n):
 paths=list(args.sources.rglob(f'SUJ{n}.xlsx'))
 if len(paths)!=1:raise ValueError(f'SUJ{n} : source absente ou ambiguë')
 w=openpyxl.load_workbook(paths[0],read_only=True,data_only=True);it=w.active.values;h=next(it)
 keys=[x for x in h if any(k in x.lower() for k in ['ack','click','mouse','touch','button','response','acquitt','event'])]
 idx=h.index('Event');iv=h.index('Event value');events=collections.Counter();values=collections.Counter();sensors=collections.Counter()
 for row in it:
  if len(row)>idx and row[idx]:events[str(row[idx])]+=1
  if len(row)>iv and row[iv] is not None:values['non_empty']+=1
  sensors[row[h.index('Sensor')]]+=1
 w.close()
 return {'sujet':f'SUJ{n}','colonnes_evenements':keys,'evenements':dict(events),'valeurs_evenements_non_vides':values['non_empty'],'capteurs':{str(k):v for k,v in sensors.items()}}
result=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for r in pool.map(run,range(1,8)):
  result.append(r);print(json.dumps(r,ensure_ascii=False),flush=True)
p=root/'results'/'comparaison'/'mouvements_FND'/'audit_acquittements.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2))
