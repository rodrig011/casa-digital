import re,html,json,sys,time,urllib.request,urllib.parse
UA={"User-Agent":"Mozilla/5.0 Chrome/124"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25).read().decode('utf-8','replace')
out={}
for term in sys.argv[1:]:
    i=0
    while True:
        u=f"https://directorio.ccg.gt/Indice?C.Order=Name&F.Name={urllib.parse.quote(term)}"+(f"&C.Index={i}" if i else "")
        try: h=get(u)
        except Exception as e:
            print('err',term,i,e,file=sys.stderr); break
        m=re.search(r'Mostrando (\d+) de (\d+)',h); tot=int(m.group(2)) if m else 0
        blocks=re.split(r'(?=href="/Miembro\?id=\d+")',h)
        for b in blocks[1:]:
            mid=re.match(r'href="/Miembro\?id=(\d+)"',b).group(1)
            txt=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','|',b)))
            parts=[p.strip() for p in txt.split('|') if p.strip()]
            r=out.setdefault(mid,{'id':mid,'partes':[],'correos':set(),'busqueda':term})
            r['correos'].update(re.findall(r'Enviar correo a ([^"\s]+@[^"\s]+)',b))
            if len(parts)>len(r['partes']): r['partes']=parts[:14]
        i+=1
        if i*10>=tot or i>30: break
        time.sleep(0.5)
for r in out.values(): r['correos']=sorted(r['correos'])
json.dump(list(out.values()),open('ccg/ccg.json','w'),ensure_ascii=False,indent=0)
print(len(out))
