#!/usr/bin/env python3
"""Uso: python3 -I tt.py <usuario_tiktok> [n_videos_con_comentarios=3]
Imprime JSON: perfil (bio, seguidores, likes, videos, link bio), videos recientes (ids, vistas, fecha, descripcion)
y para los N videos con más vistas: comentarios (texto, likes) y cuántos respondió la cuenta."""
import sys, json, re, urllib.request, time
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36","Accept-Language":"es-HN,es;q=0.9"}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25).read().decode("utf-8","replace")
def rehyd(html):
    m=re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',html,re.S)
    return json.loads(m.group(1)) if m else {}
u=sys.argv[1].lstrip("@"); n=int(sys.argv[2]) if len(sys.argv)>2 else 3
out={"usuario":u}
try:
    d=rehyd(get(f"https://www.tiktok.com/@{u}"))["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]
    us,st=d["user"],d.get("statsV2") or d["stats"]
    out["perfil"]={"nombre":us.get("nickname"),"bio":us.get("signature"),"link_bio":(us.get("bioLink") or {}).get("link"),
      "verificado":us.get("verified"),"seguidores":st.get("followerCount"),"likes":st.get("heartCount"),"videos":st.get("videoCount"),"uid":us.get("id")}
    uid=us.get("id")
except Exception as e:
    out["perfil_error"]=str(e); uid=None
ids=[]
try:
    e=get(f"https://www.tiktok.com/embed/@{u}")
    ids=list(dict.fromkeys(re.findall(r'(\d{18,20})',e)))
    ids=[i for i in ids if i!=uid][:15]
except Exception as ex: out["embed_error"]=str(ex)
vids=[]
for i in ids:
    try:
        d=rehyd(get(f"https://www.tiktok.com/@{u}/video/{i}"))["__DEFAULT_SCOPE__"].get("webapp.video-detail",{})
        it=d.get("itemInfo",{}).get("itemStruct")
        if not it: continue
        s=it.get("statsV2") or it.get("stats")
        vids.append({"id":i,"fecha":time.strftime("%Y-%m-%d",time.gmtime(int(it.get("createTime",0)))),"desc":it.get("desc","")[:200],
          "vistas":int(s.get("playCount",0)),"likes":int(s.get("diggCount",0)),"comentarios":int(s.get("commentCount",0))})
    except Exception: pass
vids.sort(key=lambda v:-v["vistas"]); out["videos"]=vids
for v in vids[:n]:
    cs=[];resp=0
    for cur in (0,50):
        try:
            j=json.loads(get(f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={v['id']}&count=50&cursor={cur}"))
        except Exception: break
        for c in j.get("comments") or []:
            cs.append({"t":c.get("text"),"likes":c.get("digg_count"),"respuestas":c.get("reply_comment_total")})
            for r in c.get("reply_comment") or []:
                if (r.get("user") or {}).get("unique_id","").lower()==u.lower(): resp+=1
        if not j.get("has_more"): break
    cs.sort(key=lambda c:-(c["likes"] or 0))
    v["muestra_comentarios"]=cs[:25]; v["comentarios_leidos"]=len(cs); v["respuestas_visibles_de_la_cuenta"]=resp
print(json.dumps(out,ensure_ascii=False,indent=1))
