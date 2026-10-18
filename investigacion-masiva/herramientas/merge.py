import json,re,unicodedata,sys
src={'sps-pollo.json':'SPS','sps-grill.json':'SPS','tgu-pollo.json':'TGU','tgu-grill.json':'TGU','otras.json':'Otras','grupos.json':'Grupos'}
def key(n):
    n=unicodedata.normalize('NFKD',n.lower()); n=''.join(c for c in n if not unicodedata.combining(c))
    n=re.sub(r'\(.*?\)','',n); n=re.sub(r'\b(hn|honduras|restaurante|restaurant|y bar|inc)\b','',n)
    return re.sub(r'[^a-z]','',n)[:10]
out={}
for f,z in src.items():
    for r in json.load(open(f)):
        if f=='grupos.json' and 'Hacienda Real' in r['nombre']: continue
        r['_grupo']=z; k=key(r['nombre'])
        if k in out:
            a=out[k]; keep,other=(a,r) if a['puntaje']>=r['puntaje'] else (r,a)
            seen={(c['canal'],c['valor']) for c in keep['contactos']}
            keep['contactos']+= [c for c in other['contactos'] if (c['canal'],c['valor']) not in seen]
            keep['fuentes']=list(dict.fromkeys(keep['fuentes']+other['fuentes']))
            keep['que_dice_la_gente']=list(dict.fromkeys(keep['que_dice_la_gente']+other['que_dice_la_gente']))
            keep['senales_de_necesidad']=list(dict.fromkeys(keep['senales_de_necesidad']+other['senales_de_necesidad']))
            if 'no encontrado' in keep.get('correo_verificado','no encontrado') and 'no encontrado' not in other.get('correo_verificado','no encontrado'):
                keep['correo_verificado']=other['correo_verificado']
            if keep['dueno']['estado']=='desconocido' and other['dueno']['estado']!='desconocido': keep['dueno']=other['dueno']
            print('dup:',a['nombre'],'+',r['nombre'],file=sys.stderr)
            out[k]=keep
        else: out[k]=r
L=sorted(out.values(),key=lambda r:(-r['puntaje'],r['nombre']))
json.dump(L,open(sys.argv[1],'w'),ensure_ascii=False,indent=1)
print(len(L))
