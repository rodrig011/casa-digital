"""Uso: python3 -I sitio.py URL [URL...]  -> JSON por sitio: correos, wa.me, teléfonos, redes, título."""
import sys,re,json,urllib.request,urllib.parse,html,ssl
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"es-GT,es;q=0.9"}
def get(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=20)
    return r.geturl(), r.read(1500000).decode("utf-8","replace")
BAD=('example','sentry','wixpress','domain.com','.png','.jpg','.webp','.gif','@2x','godaddy','yourdomain','email.com','u003e')
def scan(h,acc):
    t=html.unescape(urllib.parse.unquote(h))
    for e in re.findall(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+',t):
        if not any(b in e.lower() for b in BAD): acc['correos'].add(e.lower().strip('.'))
    for w in re.findall(r'(?:wa\.me/|api\.whatsapp\.com/send\?phone=|whatsapp\.com/send/\?phone=)\+?(\d{8,15})',t): acc['whatsapp'].add(w)
    for s in re.findall(r'https?://(?:www\.)?(?:instagram|facebook|tiktok)\.com/[^\s"\'<>?]+',t): acc['redes'].add(s.rstrip('/\\'))
    for p in re.findall(r'href="tel:([^"]+)"',h): acc['tel'].add(p)
out=[]
for u in sys.argv[1:]:
    acc={'url':u,'correos':set(),'whatsapp':set(),'redes':set(),'tel':set()}
    try:
        final,h=get(u); acc['final']=final
        m=re.search(r'<title[^>]*>(.*?)</title>',h,re.S); acc['titulo']=html.unescape(m.group(1).strip())[:90] if m else ''
        scan(h,acc)
        links=set(re.findall(r'href="([^"]*(?:contact|contacto|nosotros|sucursal|ubicacion|about)[^"]*)"',h,re.I))
        for l in list(links)[:4]:
            try: scan(get(urllib.parse.urljoin(final,l))[1],acc)
            except Exception: pass
    except Exception as e: acc['error']=str(e)[:80]
    out.append({k:(sorted(v) if isinstance(v,set) else v) for k,v in acc.items()})
print(json.dumps(out,ensure_ascii=False,indent=0))
