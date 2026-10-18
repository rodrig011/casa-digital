import json,csv,sys,re,os
L=json.load(open(sys.argv[1])); od=sys.argv[2]; os.makedirs(od,exist_ok=True)
def slug(n): return re.sub(r'[^a-z0-9]+','-',n.lower()).strip('-')[:40]
def num(x):
    try: x=int(x)
    except: return '—'
    return f'{x/1e6:.1f}M' if x>=1e6 else (f'{x/1e3:.0f}K' if x>=1e3 else str(x)) if x else '—'
def contacto(r,canales=('WhatsApp','teléfono')):
    for c in r['contactos']:
        if c['canal'] in canales: return c['valor']
    return '—'
def correo(r):
    c=r.get('correo_verificado','no encontrado')
    return '—' if c.startswith('no encontrado') else c.split(' (')[0]
def tt(r):
    t=r['redes']['tiktok']; u=(t.get('usuario') or '').lstrip('@')
    if not u or u=='no confirmado': return '—'
    return f"[@{u}](https://www.tiktok.com/@{u}) · {num(t.get('seguidores'))}"
def resp(r):
    t=r['redes']['tiktok']; c=t.get('comentarios_leidos') or 0
    return f"{t.get('respuestas_de_la_cuenta',0)} de {c}" if c else '—'
def dueno(r):
    d=r['dueno']; 
    if d['estado']=='desconocido' or not d.get('nombre'): return '—'
    return d['nombre']+(' (confirmado)' if d['estado']=='confirmado' else ' (sin confirmar)')
city={'SPS':'San Pedro Sula','TGU':'Tegucigalpa','Otras':'Otras ciudades','Grupos':'Grupos, cadenas y hoteles'}
# CSV
with open(f'{od}/prospectos.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['puntaje','nombre','ciudad','tipo','sucursales','dueño','estado_dueño','whatsapp_o_tel','correo_verificado','tiktok','seguidores_tiktok','video_top_vistas','respuestas_cuenta','comentarios_leidos','sitio_web','delivery','como_contactar','razon_puntaje'])
    for r in L:
        t=r['redes']['tiktok']
        w.writerow([r['puntaje'],r['nombre'],r['ciudad'],r['tipo_comida'],r['sucursales'],r['dueno'].get('nombre',''),r['dueno']['estado'],contacto(r),correo(r),t.get('usuario',''),t.get('seguidores',''),t.get('video_top_vistas',''),t.get('respuestas_de_la_cuenta',''),t.get('comentarios_leidos',''),r['sitio_web'],r['delivery'],r['como_contactarlos_mejor'],r['razon_puntaje']])
json.dump(L,open(f'{od}/datos.json','w'),ensure_ascii=False,indent=1)
# fichas
F=['# Fichas de cada negocio','',f'{len(L)} negocios, ordenados por puntaje. Cada dato lleva su fuente. Lo que dice "sin confirmar" no se debe usar como hecho.','']
for r in L:
    F+= [f"## {r['nombre']}",'',f"**{r['puntaje']}/10** · {r['ciudad']} · {r['tipo_comida']} · sucursales: {r['sucursales']}",'',f"*Por qué este puntaje:* {r['razon_puntaje']}",'']
    F+= [f"- **Dirección:** {r['zona_direccion']}",f"- **Dueño:** {r['dueno'].get('nombre') or 'desconocido'} ({r['dueno']['estado']}){' · fuente: '+r['dueno']['fuente'] if r['dueno'].get('fuente') else ''}",
         f"- **Sitio web:** {r['sitio_web']}",f"- **Delivery:** {r['delivery']}",f"- **Correo:** {r.get('correo_verificado','no encontrado')}",
         f"- **TikTok:** {tt(r)} · video más visto {num(r['redes']['tiktok'].get('video_top_vistas'))} · la cuenta respondió {resp(r)} comentarios leídos",
         f"- **Cómo contactarlos:** {r['como_contactarlos_mejor']}",'','**Contactos**','']
    F+= [f"- {c['canal']}: {c['valor']} ({c['fuente']})" for c in r['contactos']]
    F+= ['','**Señales de que necesitan el sistema**','']+[f'- {s}' for s in r['senales_de_necesidad']]
    if r['que_dice_la_gente']: F+= ['','**Qué dice la gente**','']+[f'- {s}' for s in r['que_dice_la_gente']]
    F+= ['','<details><summary>Fuentes</summary>','']+[f'- {u}' for u in r['fuentes']]+['','</details>','']
open(f'{od}/fichas.md','w').write('\n'.join(F))
# tabla por zona (para README)
def tabla(rows):
    T=['| # | Negocio | Ciudad | WhatsApp / tel. | TikTok | Respondió | Correo |','|---|---|---|---|---|---|---|']
    for r in rows:
        T.append(f"| {r['puntaje']} | **{r['nombre']}** | {r['ciudad']} | {contacto(r)} | {tt(r)} | {resp(r)} | {correo(r)} |")
    return '\n'.join(T)
open(f'{od}/_tablas.md','w').write('\n\n'.join(f'### {city[z]} ({sum(r["_grupo"]==z for r in L)})\n\n'+tabla([r for r in L if r['_grupo']==z]) for z in city))
print(sum(1 for r in L if correo(r)!='—'),'con correo')
