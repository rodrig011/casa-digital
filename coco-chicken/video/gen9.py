#!/usr/bin/env python3
"""Coco Chicken pitch video v4 = v3 plus the numbers (savings example) and the opportunities from their comments.
v3 notes: (2026-10-14): dark, premium, slow. Same track and bar grid as gen6/gen7.
Story: they have the attention -> real TikTok comments asking where they are / if they deliver /
"nunca me responden" -> their WhatsApp answers by itself (full conversation, real menu and prices)
-> everything connected: phone -> kitchen screen -> owner panel -> customer notified -> the real
owner panel -> their promo and TikTok codes -> Casa Digital (made by Hondurans) -> Clientia outro.
Comments are verbatim from redes/tiktok-comentarios.md; conversation and panel numbers are examples."""
import json, os, re, shutil
import gen3, gen6
from gen2 import MARK, words, ribbons, DEPS, HERE
from gen6 import K, P0, BAR, R

SRC = os.path.join(HERE, "coco-src")
OUT = os.path.join(HERE, "videos9")
SCENES = [("intro", 0, 3), ("fame", 3, 7), ("asks", 7, 11), ("meet", 11, 13), ("bot", 13, 21), ("link", 21, 27),
          ("owner", 27, 31), ("money", 31, 36), ("chances", 36, 40), ("extra", 40, 43), ("us", 43, 46), ("end", 46, 50)]
TOTAL = K(50)
GOLD = "#F2B544"


def gold(t):
    return f'<span class="gold">{words(t)}</span>'


CSS8 = r'''
html,body,#root,.scene{background:#070708;}
#root{color:#F5F5F7;}
.sp{position:absolute;border-radius:50%;pointer-events:none;}
.sp-red{background:radial-gradient(closest-side,rgba(216,38,28,.26),rgba(7,7,8,0));}
.sp-gold{background:radial-gradient(closest-side,rgba(242,181,68,.16),rgba(7,7,8,0));}
.sp-green{background:radial-gradient(closest-side,rgba(37,211,102,.16),rgba(7,7,8,0));}
.h1{font-weight:600;font-size:108px;line-height:1.03;letter-spacing:-.045em;color:#F5F5F7;}
.h1.m{font-size:84px;}
.gold .w{background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;padding-bottom:.08em;}
.eb{font-size:26px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:#8E8E93;margin-bottom:26px;}
.eb.g{color:#E3A94A;}
.sub{font-size:36px;font-weight:500;line-height:1.3;letter-spacing:-.015em;color:#8E8E93;margin-top:34px;}
.left{width:900px;}
.lgrp{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);}
.demo{position:absolute;right:110px;bottom:46px;font-size:18px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#4E4E53;}
.hair{position:absolute;left:150px;right:150px;height:1px;background:rgba(255,255,255,.06);}
/* intro */
.cd{color:#F5F5F7;}
.sub-g{color:#8E8E93;}
.ilogo{width:210px;height:210px;border-radius:50%;overflow:hidden;margin-top:46px;box-shadow:0 0 0 3px rgba(242,181,68,.65),0 30px 90px rgba(216,38,28,.35);}
.ilogo img{width:100%;height:100%;object-fit:cover;object-position:50% 30%;}
.iname{margin-top:40px;font-family:"Display";text-transform:uppercase;font-size:118px;line-height:1;letter-spacing:-.01em;color:#F5F5F7;}
/* fame */
.stats{margin-top:64px;display:flex;gap:64px;}
.st b{display:block;font-size:72px;font-weight:600;letter-spacing:-.04em;line-height:1;font-variant-numeric:tabular-nums;color:#F5F5F7;}
.st span{display:block;margin-top:12px;font-size:24px;color:#8E8E93;font-weight:500;}
.vid{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}
.tagv{position:absolute;left:1250px;top:1010px;width:430px;text-align:center;font-size:20px;color:#6E6E73;font-weight:500;}
/* real comments */
.cms{position:absolute;left:1060px;top:0;bottom:0;width:720px;display:flex;flex-direction:column;justify-content:center;gap:22px;}
.cm{background:linear-gradient(180deg,#161618,#111113);border-radius:28px;padding:26px 32px 24px;box-shadow:0 0 0 1px rgba(255,255,255,.07),0 30px 70px rgba(0,0,0,.5);}
.cm-h{display:flex;align-items:center;gap:12px;font-size:19px;color:#6E6E73;font-weight:500;}
.cm-h i{width:30px;height:30px;border-radius:50%;background:#2C2C2E;}
.cm p{margin-top:12px;font-size:36px;line-height:1.25;font-weight:500;letter-spacing:-.015em;color:#F5F5F7;}
.cm-l{margin-top:12px;font-size:20px;color:#8E8E93;font-weight:500;}
.cm-l b{color:#FF375F;font-weight:600;}
/* meet */
.wa-pill{display:inline-flex;align-items:center;gap:14px;margin-bottom:44px;padding:14px 26px;border-radius:40px;background:rgba(37,211,102,.12);box-shadow:0 0 0 1px rgba(37,211,102,.35);font-size:26px;font-weight:600;color:#25D366;}
.wa-pill i{width:14px;height:14px;border-radius:50%;background:#25D366;box-shadow:0 0 0 6px rgba(37,211,102,.22);}
/* WhatsApp inside the phone */
.wa{position:absolute;inset:0;background:#0B141A;color:#E9EDEF;font-family:"IT",sans-serif;}
.wa-h{position:absolute;left:0;right:0;top:0;height:128px;padding:62px 18px 0;background:#1F2C34;display:flex;align-items:center;gap:12px;z-index:4;}
.wa-h .bk{font-size:34px;color:#8696A0;margin-right:2px;line-height:1;}
.wa-av{width:44px;height:44px;border-radius:50%;overflow:hidden;flex:none;}
.wa-av img{width:100%;height:100%;object-fit:cover;object-position:50% 30%;}
.wa-h b{display:block;font-size:19px;font-weight:600;}
.wa-h span{display:block;font-size:14px;color:#8696A0;margin-top:1px;}
.wa-msgs{position:absolute;left:12px;right:12px;bottom:86px;display:flex;flex-direction:column;}
.slot{overflow:hidden;height:0;display:flex;flex-direction:column;}
.wb{max-width:82%;font-size:18px;line-height:1.34;padding:9px 13px 10px;border-radius:14px;margin-top:8px;}
.wb.in{align-self:flex-start;background:#202C33;border-top-left-radius:4px;}
.wb.out{align-self:flex-end;background:#005C4B;border-top-right-radius:4px;}
.wb small{display:block;text-align:right;font-size:11px;color:rgba(233,237,239,.55);margin-top:3px;}
.typ{align-self:flex-start;background:#202C33;border-radius:14px;padding:13px 16px;margin-top:8px;display:flex;gap:6px;}
.typ i{width:8px;height:8px;border-radius:50%;background:#8696A0;}
.ocard{align-self:flex-start;width:300px;background:#202C33;border-radius:14px;border-top-left-radius:4px;margin-top:8px;overflow:hidden;}
.oc-in{padding:12px 14px 10px;}
.oc-k{font-size:13px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#25D366;}
.oc-t{font-size:20px;font-weight:600;margin-top:4px;}
.oc-s{font-size:14px;color:#8696A0;margin-top:2px;}
.oc-r{display:flex;justify-content:space-between;font-size:17px;margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08);}
.oc-r b{font-weight:600;}
.oc-b{position:relative;text-align:center;font-size:17px;font-weight:600;color:#53BDEB;padding:12px 0;border-top:1px solid rgba(255,255,255,.08);}
.oc-b i{position:absolute;inset:0;background:rgba(83,189,235,.18);opacity:0;}
.wa-in{position:absolute;left:10px;right:10px;bottom:22px;height:50px;border-radius:26px;background:#1F2C34;display:flex;align-items:center;padding:0 20px;font-size:17px;color:#8696A0;}
.ph-stage{left:1100px;}
/* connected devices */
.dev{position:absolute;}
.dcap{position:absolute;left:0;right:0;text-align:center;font-size:24px;font-weight:600;letter-spacing:-.01em;color:#F5F5F7;}
.dcap span{display:block;font-size:19px;font-weight:500;color:#8E8E93;margin-top:4px;}
.mini{width:250px;height:520px;border-radius:48px;padding:9px;background:linear-gradient(145deg,#3A3A3C,#0C0C0D 40%,#1C1C1E 70%,#48484A);box-shadow:0 40px 90px rgba(0,0,0,.6);}
.mini-s{position:relative;width:100%;height:100%;border-radius:40px;overflow:hidden;background:#0B141A;}
.mini .wa-h{height:92px;padding:40px 12px 0;}
.mini .wa-h b{font-size:15px;}.mini .wa-h span{font-size:11px;}.mini .wa-av{width:32px;height:32px;}
.mini .ocard{position:absolute;left:10px;top:250px;width:200px;margin:0;}
.mini .oc-in{padding:9px 11px;}.mini .oc-t{font-size:15px;}.mini .oc-s{font-size:11px;}.mini .oc-k{font-size:10px;}
.mini .wb{position:absolute;right:10px;top:200px;font-size:13px;margin:0;}
.mnot{position:absolute;left:8px;right:8px;top:44px;z-index:6;background:rgba(40,40,44,.96);border-radius:18px;padding:10px 12px;display:flex;gap:9px;align-items:center;box-shadow:0 12px 30px rgba(0,0,0,.5);}
.mnot .ic{width:30px;height:30px;border-radius:8px;background:#25D366;flex:none;}
.mnot b{display:block;font-size:12px;}.mnot span{display:block;font-size:12px;color:#C7C7CC;line-height:1.25;}
.tab{width:660px;height:440px;border-radius:30px;padding:12px;background:#1C1C1E;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 40px 90px rgba(0,0,0,.6);}
.tab-s{position:relative;width:100%;height:100%;border-radius:20px;overflow:hidden;background:#F3F3F3;color:#181818;}
.tab-h{height:52px;background:#fff;border-bottom:1px solid #E5E5E5;display:flex;align-items:center;justify-content:space-between;padding:0 18px;font-size:17px;font-weight:600;}
.tab-h span{font-weight:500;color:#706E6B;font-size:15px;}
.kcols{display:flex;gap:10px;padding:12px;}
.kcol{flex:1;}
.kcol h4{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#706E6B;margin:2px 4px 8px;}
.tk{background:#fff;border-radius:10px;padding:10px 12px;margin-bottom:8px;box-shadow:0 0 0 1px #E5E5E5;font-size:13px;}
.tk b{display:flex;justify-content:space-between;font-size:15px;color:#0176D3;}
.tk b em{font-style:normal;color:#706E6B;font-weight:500;font-size:12px;}
.tk p{margin-top:4px;color:#181818;}
.tk.new{position:absolute;left:12px;top:92px;width:198px;box-shadow:0 0 0 2px #F2B544,0 10px 30px rgba(242,181,68,.35);}
.tk .ok{display:inline-block;margin-top:6px;font-size:11px;font-weight:700;color:#2E844A;background:#CDEFC4;padding:2px 8px;border-radius:10px;}
.lap{width:540px;}
.lap-s{width:540px;height:340px;border-radius:18px 18px 0 0;padding:10px;background:#1C1C1E;box-shadow:0 0 0 1px rgba(255,255,255,.08);}
.lap-in{width:100%;height:100%;border-radius:8px;overflow:hidden;background:#F3F3F3;color:#181818;}
.lap-b{height:16px;margin:0 -30px;border-radius:0 0 14px 14px;background:linear-gradient(#3A3A3C,#1C1C1E);box-shadow:0 30px 70px rgba(0,0,0,.6);}
.lp-h{height:40px;background:#fff;border-bottom:1px solid #E5E5E5;display:flex;align-items:center;gap:10px;padding:0 14px;font-size:14px;font-weight:600;}
.lp-h i{width:20px;height:20px;border-radius:5px;background:#D8261C;}
.kp{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:10px;}
.kpi2{background:#fff;border-radius:8px;padding:10px 12px;box-shadow:0 0 0 1px #E5E5E5;}
.kpi2>span{display:block;font-size:11px;color:#706E6B;}
.kpi2 b{display:block;font-size:24px;font-weight:500;margin-top:2px;font-variant-numeric:tabular-nums;}
.kpi2.hot{box-shadow:0 0 0 2px #F2B544;}
.lbars{margin:0 10px;background:#fff;border-radius:8px;padding:10px 12px;box-shadow:0 0 0 1px #E5E5E5;}
.lb{display:flex;align-items:center;gap:8px;font-size:11px;color:#3E3E3C;margin-top:5px;}
.lb span{width:96px;}
.lb div{flex:1;height:8px;border-radius:4px;background:#ECEBEA;overflow:hidden;}
.lb div i{display:block;height:100%;background:#0176D3;transform-origin:0 50%;}
.wires{position:absolute;inset:0;width:1920px;height:1080px;overflow:visible;}
.wires .base{fill:none;stroke:rgba(255,255,255,.14);stroke-width:2;stroke-dasharray:4 8;}
.wires .run{opacity:0;fill:none;stroke:#F2B544;stroke-width:4;stroke-linecap:round;filter:drop-shadow(0 0 10px rgba(242,181,68,.9));}
.ttl{position:absolute;left:0;right:0;top:96px;text-align:center;}
/* owner panel */
.shot{position:absolute;left:770px;top:200px;width:1040px;border-radius:22px;overflow:hidden;background:#1C1C1E;padding:12px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 60px 140px rgba(0,0,0,.7);}
.shot img{display:block;width:1016px;height:635px;border-radius:12px;}
.blt{margin-top:46px;display:flex;flex-direction:column;gap:20px;}
.bl{display:flex;align-items:center;gap:18px;font-size:30px;font-weight:500;color:#D1D1D6;letter-spacing:-.01em;}
.bl i{flex:none;width:10px;height:10px;border-radius:50%;background:#F2B544;box-shadow:0 0 0 6px rgba(242,181,68,.16);}
#owner .left{width:600px;}
#owner .h1.m{font-size:70px;}
#extra .left{width:780px;}
/* extras */
.stamp{position:absolute;left:1000px;top:170px;width:780px;height:360px;border-radius:40px;background:radial-gradient(120% 120% at 15% 0%,#E8352A,#8E120B);color:#fff;padding:40px 46px;box-shadow:0 50px 120px rgba(216,38,28,.28);}
.stamp-k{font-size:20px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#FFD21F;}
.stamp-t{font-family:"Display";text-transform:uppercase;font-size:46px;line-height:1;margin-top:12px;}
.stamp-row{display:flex;gap:26px;margin-top:36px;}
.spt{position:relative;width:100px;height:100px;border-radius:50%;border:3px dashed rgba(255,255,255,.5);}
.spt b{position:absolute;inset:-3px;border-radius:50%;background:#FFD21F;color:#8E120B;display:flex;align-items:center;justify-content:center;font-size:44px;font-weight:700;}
.spt.free b{background:#fff;font-size:21px;letter-spacing:.04em;}
.stamp-s{position:absolute;right:46px;top:44px;font-size:20px;opacity:.85;}
.tkc{position:absolute;left:1000px;top:570px;width:780px;background:linear-gradient(180deg,#161618,#111113);border-radius:36px;padding:32px 40px;box-shadow:0 0 0 1px rgba(255,255,255,.07),0 40px 90px rgba(0,0,0,.5);}
.tkc h3{font-size:26px;font-weight:600;letter-spacing:-.01em;}
.tkr{display:flex;align-items:center;gap:18px;margin-top:20px;font-size:22px;}
.tkr .cd2{flex:none;font-size:15px;font-weight:700;letter-spacing:.08em;color:#F2B544;background:rgba(242,181,68,.12);padding:6px 10px;border-radius:8px;width:118px;text-align:center;}
.tkr .nm{width:330px;color:#D1D1D6;}
.tkr .tr{flex:1;height:10px;border-radius:5px;background:#2C2C2E;overflow:hidden;}
.tkr .tr i{display:block;height:100%;border-radius:5px;background:linear-gradient(90deg,#D98E1C,#F2B544);transform-origin:0 50%;}
.tkr .v{width:90px;text-align:right;color:#8E8E93;font-size:18px;}
/* us */
.whys2{margin-top:50px;display:flex;flex-direction:column;gap:22px;}
.wy2{display:flex;gap:20px;align-items:center;font-size:34px;font-weight:500;letter-spacing:-.015em;color:#E5E5EA;}
.wy2 i{flex:none;width:44px;height:44px;border-radius:50%;background:rgba(242,181,68,.14);color:#F2B544;font-style:normal;font-size:22px;font-weight:700;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 1px rgba(242,181,68,.35);}
.cta2{position:absolute;left:1220px;top:250px;width:560px;height:580px;border-radius:56px;background:linear-gradient(180deg,#18181A,#0F0F10);box-shadow:0 0 0 1px rgba(255,255,255,.09),0 60px 140px rgba(0,0,0,.7);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}
.cta2 .ic{width:130px;height:130px;border-radius:36px;background:#F5F5F7;color:#0B0B0C;display:flex;align-items:center;justify-content:center;}
.cta2 .ic .house{width:78px;height:78px;}
.cta2 .t{margin-top:32px;font-size:48px;font-weight:600;letter-spacing:-.03em;}
.cta2 .s{margin-top:8px;font-size:28px;color:#8E8E93;}
.cta2 .wa2{margin-top:40px;background:#25D366;color:#fff;font-weight:600;font-size:36px;padding:20px 40px;border-radius:50px;letter-spacing:-.01em;}
.cta2 .wa2 span{display:block;font-size:18px;font-weight:500;opacity:.85;}
.cta2 .who{margin-top:26px;font-size:20px;color:#6E6E73;}

/* the numbers */
#money .left,#chances .left{width:780px;}
.calc{position:absolute;left:1000px;top:150px;width:800px;background:linear-gradient(180deg,#161618,#0F0F10);border-radius:40px;padding:44px 52px 40px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 60px 140px rgba(0,0,0,.7);}
.cr{display:flex;align-items:baseline;gap:26px;padding:18px 0;border-bottom:1px solid rgba(255,255,255,.07);}
.cr b{flex:none;width:210px;font-size:54px;font-weight:600;letter-spacing:-.035em;font-variant-numeric:tabular-nums;color:#F5F5F7;}
.cr span{font-size:25px;line-height:1.3;color:#A1A1A6;font-weight:500;}
.cr span em{display:block;font-style:normal;color:#F5F5F7;font-weight:600;font-size:27px;}
.cres{margin-top:30px;}
.cres .k{font-size:22px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#8E8E93;}
.cres .big{font-size:132px;font-weight:600;letter-spacing:-.05em;line-height:1;margin-top:8px;font-variant-numeric:tabular-nums;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
.cres .yr{margin-top:14px;font-size:34px;font-weight:600;color:#F5F5F7;letter-spacing:-.02em;}
.cres .yr span{color:#8E8E93;font-weight:500;}
.foot{position:absolute;left:150px;bottom:46px;font-size:18px;font-weight:500;color:#5A5A5F;}
.tiles{position:absolute;left:1020px;top:0;bottom:0;width:760px;display:flex;flex-direction:column;justify-content:center;gap:22px;}
.tile{display:flex;align-items:center;gap:34px;background:linear-gradient(180deg,#161618,#111113);border-radius:32px;padding:30px 40px;box-shadow:0 0 0 1px rgba(255,255,255,.07),0 30px 80px rgba(0,0,0,.5);}
.tile b{flex:none;width:170px;font-size:104px;font-weight:600;letter-spacing:-.05em;line-height:1;font-variant-numeric:tabular-nums;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
.tile>span{font-size:30px;line-height:1.25;font-weight:500;color:#E5E5EA;letter-spacing:-.01em;}
.tile>span em{display:block;font-style:normal;font-size:22px;color:#8E8E93;margin-top:6px;}
'''


def build():
    proj = os.path.join(OUT, R["slug"])
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    A = lambda *p: os.path.join(proj, "assets", *p)
    shutil.copy(os.path.join(HERE, "musica2.mp3"), A("musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), A("gsap.min.js"))
    shutil.copy(os.path.join(DEPS, "@fontsource", "archivo-black", "files", R["fonts"]["displayFile"]), A("fonts", "display.woff2"))
    for w in (300, 400, 500, 600, 700):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter-tight", "files", f"inter-tight-latin-{w}-normal.woff2"), A("fonts", f"it-{w}.woff2"))
    for n in ("tiktok.mp4", "logo.png"):
        shutil.copy(os.path.join(SRC, n), A(n))
    shutil.copy(os.path.join(SRC, "panel", "pv-hoy.png"), A("pv-hoy.png"))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "coco-chicken-v4", "name": "Casa Digital x Coco Chicken"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    vid = (f'<video id="tkvid" class="vid" src="assets/tiktok.mp4" data-start="{K(3)}" data-duration="{round(K(7) - K(3), 3)}" '
           f'data-media-start="0" data-track-index="2" muted playsinline></video>')
    stats = [("204.9K", "seguidores en TikTok"), ("3.1M", "me gusta"), ("127K", "en Facebook")]
    stats_html = "".join(f'<div class="st" id="st{i}"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(stats))
    # verbatim from redes/tiktok-comentarios.md, with their like counts
    comments = [("Incluye refresco ese combo ?", "3,071"), ("Y al fin bro dnd Estan ubicados", "50"),
                ("Hacen envíos??", None), ("Yo quierooooooo pero nunca me responden 😞😞", None)]
    cms = "".join(f'<div class="cm" id="cm{i}"><div class="cm-h"><i></i>Comentario en su TikTok</div><p>{t}</p>'
                  + (f'<div class="cm-l"><b>♥</b> {l} me gusta</div>' if l else "") + '</div>' for i, (t, l) in enumerate(comments))

    head = ('<div class="wa-h"><span class="bk">‹</span><div class="wa-av"><img src="assets/logo.png"></div>'
            '<div><b>Coco Chicken</b><span>en línea</span></div></div>')
    order = ('<div class="oc-in"><div class="oc-k">Pedido #4132</div><div class="oc-t">Colonia Satélite</div>'
             '<div class="oc-s">Para recoger · listo en unos 15 min</div>'
             '<div class="oc-r"><span>2 × Cadera y tajadas</span><b>L170</b></div>'
             '<div class="oc-s" style="margin-top:6px">Paga al recoger, en efectivo o tarjeta</div></div>')
    msgs = [("m1", '<div class="wb out">Buenas, ¿dónde están ubicados?<small>5:02 p. m.</small></div>'),
            ("t1", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m2", '<div class="wb in">¡Hola! Tenemos 3 sucursales: Barrio Cabañas, Colonia Satélite y Barrio Medina. '
                   'Abrimos de lunes a domingo, de 9 am a 10 pm.<small>5:02 p. m.</small></div>'),
            ("m3", '<div class="wb in">¿Le preparo algo para recoger? Así no hace fila.<small>5:02 p. m.</small></div>'),
            ("m4", '<div class="wb out">Sí, 2 cadera y tajadas en la Satélite<small>5:03 p. m.</small></div>'),
            ("t2", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m5", f'<div class="ocard">{order}<div class="oc-b"><i id="okbtn"></i>Confirmar pedido</div></div>'),
            ("m6", '<div class="wb out">Confirmar pedido<small>5:03 p. m.</small></div>'),
            ("t3", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m7", '<div class="wb in">¡Listo! Ya está en la cocina de la Satélite. Le escribo cuando esté listo.<small>5:03 p. m.</small></div>')]
    wa = (f'<div class="wa">{head}<div class="wa-msgs">' + "".join(f'<div class="slot" id="{i}">{h}</div>' for i, h in msgs)
          + '</div><div class="wa-in">Mensaje</div></div>')

    tickets_old = {0: [("#4130", "1 × Ala y tajadas")], 1: [("#4128", "1 × Pierna y tajadas"), ("#4129", "2 × Ala y tajadas")], 2: []}
    kcols = "".join(f'<div class="kcol"><h4>{t}</h4>' + "".join(f'<div class="tk"><b>{a}<em>hace {4 + j * 6 + c * 3} min</em></b><p>{b}</p></div>' for j, (a, b) in enumerate(tickets_old[c])) + '</div>'
                    for c, t in enumerate(["Nuevos", "En cocina", "Listos"]))
    tab = (f'<div class="tab"><div class="tab-s"><div class="tab-h">Cocina · Colonia Satélite<span>5:03 pm</span></div>'
           f'<div class="kcols">{kcols}</div>'
           '<div class="tk new" id="tnew"><b>#4132<em>WhatsApp</em></b><p>2 × Cadera y tajadas</p><span class="ok" id="tok">Listo</span></div></div></div>')
    bars = [("Barrio Cabañas", 72), ("Colonia Satélite", 86), ("Barrio Medina", 64)]
    lap = ('<div class="lap"><div class="lap-s"><div class="lap-in"><div class="lp-h"><i></i>Panel Coco Chicken · Inicio</div>'
           '<div class="kp"><div class="kpi2 hot" id="kv"><span>Ventas de hoy</span><b><span id="nv">L52,105</span></b></div>'
           '<div class="kpi2" id="kr"><span>Pedidos para recoger</span><b><span id="nr">37</span></b></div>'
           '<div class="kpi2"><span>Comisión a las apps</span><b>L5,849</b></div>'
           '<div class="kpi2"><span>Pollo en Satélite</span><b>10.8</b></div></div>'
           '<div class="lbars">' + "".join(f'<div class="lb"><span>{n}</span><div><i id="lb{i}" style="width:{v}%"></i></div></div>' for i, (n, v) in enumerate(bars))
           + '</div></div></div><div class="lap-b"></div></div>')
    mini = (f'<div class="mini"><div class="mini-s">{head}'
            '<div class="wb out">Confirmar pedido</div>'
            f'<div class="ocard">{order}</div>'
            '<div class="mnot" id="mnot"><div class="ic"></div><div><b>Coco Chicken</b><span>Su pedido #4132 ya está listo. ¡Lo esperamos en la Satélite!</span></div></div></div></div>')
    # wire paths (phone right edge -> tablet left, tablet right -> laptop left, tablet top arc back to phone)
    wires = ('<svg class="wires" viewBox="0 0 1920 1080">'
             '<path class="base" d="M 374 560 C 440 560 480 580 556 580"/><path class="run" id="wa" d="M 374 560 C 440 560 480 580 556 580"/>'
             '<path class="base" d="M 1228 580 C 1255 580 1270 560 1298 560"/><path class="run" id="wb" d="M 1228 580 C 1255 580 1270 560 1298 560"/>'
             '<path class="base" d="M 890 352 C 820 230 450 220 270 300"/><path class="run" id="wc" d="M 890 352 C 820 230 450 220 270 300"/>'
             '</svg>')

    tks = [("¿Pollos A 15 lempiras?", "POLLO15", 96, "871.5K"), ("36 Alitas A 600 Lempiras", "ALITAS36", 100, "933.4K"),
           ("Gracias Por Su Cariño Gente De Choloma", "CHOLOMA", 34, "169.6K")]
    tkc = ('<div class="tkc" id="tkc"><h3>¿Qué video vendió más esta semana?</h3>' + "".join(
        f'<div class="tkr"><span class="cd2">{c}</span><span class="nm">{t}</span><div class="tr"><i id="tkb{i}" style="width:{w}%"></i></div><span class="v">{v}</span></div>'
        for i, (t, c, w, v) in enumerate(tks)) + '</div>')
    whys = ["Ya lo armamos con su menú y sus 3 sucursales.", "Se instala en 14 días.", "Soporte por WhatsApp, en español."]
    whys_html = "".join(f'<div class="wy2" id="wy{i}"><i>✓</i><span>{words(t)}</span></div>' for i, t in enumerate(whys))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f'''
          <div class="sp sp-red" style="left:260px;top:-520px;width:1400px;height:1400px"></div>
          <div class="sp sp-gold" style="left:560px;top:520px;width:800px;height:800px"></div>
          <div class="center">
            <div class="cd" id="icd">{gen3.HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("una propuesta para")}</div>
            <div class="ilogo" id="ilogo"><img src="assets/logo.png"></div>
            <div class="iname" id="iname">Coco Chicken</div>
          </div>'''),
        scene("fame", f'''
          <div class="sp sp-red" style="left:900px;top:-300px;width:1500px;height:1500px"></div>
          <div class="tagv" id="tagv">Su video fijado · 871.5K vistas</div>
          <div class="left">
            <div class="eb" id="f0">TikTok · @cocochiken1</div>
            <div class="h1" id="f1">{words("Ya tienen")}</div>
            <div class="h1" id="f2">{words("lo más difícil:")}</div>
            <div class="h1" id="f3">{gold("la atención.")}</div>
            <div class="stats">{stats_html}</div>
          </div>'''),
        scene("asks", f'''
          <div class="sp sp-gold" style="left:900px;top:-200px;width:1400px;height:1400px"></div>
          <div class="cms">{cms}</div>
          <div class="left">
            <div class="lgrp" id="ag1"><div class="eb" id="a0">Comentarios reales</div><div class="h1" id="a1">{words("Todos los días")}</div><div class="h1" id="a2">{words("les preguntan.")}</div></div>
            <div class="lgrp" id="ag2"><div class="h1" id="a3">{words("¿Y quién")}</div><div class="h1" id="a4">{gold("les contesta?")}</div></div>
          </div>'''),
        scene("meet", f'''
          <div class="sp sp-green" style="left:260px;top:-300px;width:1400px;height:1400px"></div>
          <div class="center">
            <div class="wa-pill" id="mp"><i></i>WhatsApp · Coco Chicken</div>
            <div class="h1" id="me1" style="font-size:124px">{words("Su WhatsApp,")}</div>
            <div class="h1" id="me2" style="font-size:124px">{gold("que contesta solo.")}</div>
          </div>'''),
        scene("bot", f'''
          <div class="sp sp-green" style="left:950px;top:-250px;width:1400px;height:1400px"></div>
          <div class="ph-stage">{gen3.phone(wa, "phw", dark=True)}</div>
          <div class="left">
            <div class="lgrp" id="bg1"><div class="eb g" id="b10">Al instante, a cualquier hora</div><div class="h1" id="b11">{words("Contesta")}</div><div class="h1" id="b12">{gold("sus preguntas.")}</div></div>
            <div class="lgrp" id="bg2"><div class="eb g" id="b20">Sin llamadas, sin esperar</div><div class="h1" id="b21">{words("Toma el pedido")}</div><div class="h1" id="b22">{gold("completo.")}</div></div>
            <div class="lgrp" id="bg3"><div class="eb g" id="b30">Directo a la sucursal</div><div class="h1" id="b31">{words("Y lo manda")}</div><div class="h1" id="b32">{gold("a la cocina.")}</div></div>
          </div>
          <div class="demo" id="bdemo">Conversación de ejemplo · menú y precios reales</div>'''),
        scene("link", f'''
          <div class="sp sp-gold" style="left:360px;top:-200px;width:1200px;height:1200px"></div>
          <div class="ttl"><div class="h1 m" id="lk1">{words("Y todo")} {gold("queda conectado.")}</div></div>
          {wires}
          <div class="dev" id="dv0" style="left:120px;top:300px">{mini}<div class="dcap" style="top:546px">El cliente pide<span>por WhatsApp</span></div></div>
          <div class="dev" id="dv1" style="left:560px;top:360px">{tab}<div class="dcap" style="top:486px">La cocina lo ve<span>al instante, en una pantalla</span></div></div>
          <div class="dev" id="dv2" style="left:1300px;top:390px">{lap}<div class="dcap" style="top:400px">Usted lo ve todo<span>en su panel</span></div></div>
          <div class="demo" id="ldemo">Datos de ejemplo</div>'''),
        scene("owner", f'''
          <div class="sp sp-red" style="left:700px;top:-300px;width:1500px;height:1500px"></div>
          <div class="shot" id="shot"><img src="assets/pv-hoy.png"></div>
          <div class="left">
            <div class="eb g" id="o0">Panel del dueño</div>
            <div class="h1 m" id="o1">{words("Sus 3 sucursales,")}</div>
            <div class="h1 m" id="o2">{gold("en un solo lugar.")}</div>
            <div class="blt">
              <div class="bl" id="ob0"><i></i><span>{words("Ventas por sucursal")}</span></div>
              <div class="bl" id="ob1"><i></i><span>{words("PedidosYa y Bip Bip, con su comisión")}</span></div>
              <div class="bl" id="ob2"><i></i><span>{words("Caja y pollo de cada noche")}</span></div>
            </div>
          </div>
          <div class="demo" id="odemo">Datos de ejemplo</div>'''),
        scene("money", f'''
          <div class="sp sp-gold" style="left:900px;top:-300px;width:1500px;height:1500px"></div>
          <div class="calc" id="calc">
            <div class="cr" id="cr0"><b>300</b><span><em>pedidos al mes</em>que pasan de la app a recoger por WhatsApp: 10 al día entre las 3 sucursales</span></div>
            <div class="cr" id="cr1"><b>× L140</b><span><em>por pedido</em>el precio de Pierna, cadera y tajadas</span></div>
            <div class="cr" id="cr2"><b>× 25%</b><span><em>de comisión</em>lo que cobra una app, más o menos</span></div>
            <div class="cres" id="cres"><div class="k">Se quedan en Coco Chicken, cada mes</div><div class="big"><span id="nsav">L0</span></div><div class="yr" id="cyr">L126,000 <span>al año</span></div></div>
          </div>
          <div class="left">
            <div class="eb g" id="y0">Los números</div>
            <div class="h1 m" id="y1">{words("Menos comisión,")}</div>
            <div class="h1 m" id="y2">{gold("más ganancia.")}</div>
            <div class="sub" id="y3">{words("PedidosYa y Bip Bip siguen para domicilio. Lo que pasa a recoger ya no paga comisión.")}</div>
          </div>
          <div class="foot" id="yfoot">Ejemplo con supuestos. La comisión real depende de su contrato con cada app.</div>'''),
        scene("chances", f'''
          <div class="sp sp-red" style="left:900px;top:-200px;width:1400px;height:1400px"></div>
          <div class="tiles">
            <div class="tile" id="ti0"><b><span class="cnt" data-n="87">0</span></b><span>comentarios piden una sucursal en su ciudad<em>Tegucigalpa, El Progreso, Comayagua, La Ceiba…</em></span></div>
            <div class="tile" id="ti1"><b><span class="cnt" data-n="56">0</span></b><span>preguntan el precio o qué trae el combo<em>El bot les contesta y les toma el pedido.</em></span></div>
            <div class="tile" id="ti2"><b><span class="cnt" data-n="25">0</span></b><span>preguntan dónde están<em>El bot les manda las 3 sucursales.</em></span></div>
          </div>
          <div class="left">
            <div class="eb g" id="h0">Oportunidades</div>
            <div class="h1 m" id="h1">{words("Lo que sus clientes")}</div>
            <div class="h1 m" id="h2">{gold("ya les piden.")}</div>
            <div class="sub" id="h3">{words("Y el bot anota de qué ciudad le escriben, para saber dónde abrir la próxima.")}</div>
          </div>
          <div class="foot" id="hfoot">Conteo de 506 comentarios reales de su TikTok, octubre 2026.</div>'''),
        scene("extra", f'''
          <div class="sp sp-red" style="left:900px;top:-200px;width:1300px;height:1300px"></div>
          <div class="stamp" id="stamp"><div class="stamp-k">Su promo, en WhatsApp</div><div class="stamp-t">Pagas 3,<br>el 4 es gratis</div>
            <div class="stamp-s">Cada compra suma un sello</div>
            <div class="stamp-row">{"".join(f'<div class="spt{" free" if i == 3 else ""}"><b id="sb{i}">{"GRATIS" if i == 3 else "✓"}</b></div>' for i in range(4))}</div></div>
          {tkc}
          <div class="left">
            <div class="h1 m" id="x1">{words("Su promo")}</div>
            <div class="h1 m" id="x2">{words("y sus videos,")}</div>
            <div class="h1 m" id="x3">{gold("vendiendo.")}</div>
            <div class="sub" id="x4">{words("Cada TikTok lleva su código, y el panel dice cuál trajo más pedidos.")}</div>
          </div>
          <div class="demo" id="xdemo">Vistas reales · pedidos de ejemplo</div>'''),
        scene("us", f'''
          <div class="sp sp-gold" style="left:900px;top:-200px;width:1400px;height:1400px"></div>
          <div class="left">
            <div class="eb g" id="u0">Casa Digital</div>
            <div class="h1 m" id="u1">{words("Hecho por hondureños,")}</div>
            <div class="h1 m" id="u2">{gold("para negocios hondureños.")}</div>
            <div class="whys2">{whys_html}</div>
          </div>
          <div class="cta2" id="cta">
            <div class="ic">{gen3.HOUSE}</div>
            <div class="t">Casa Digital</div>
            <div class="s">Se lo mostramos en 15 minutos.</div>
            <div class="wa2"><span>WhatsApp</span>{gen3.WHATSAPP}</div>
            <div class="who">Rodrigo Herrera</div>
          </div>'''),
        scene("end", f'''
          <div class="endglow" id="eglow"></div>
          <div class="ribwrap">{ribbons("re", ["#3E7BFA", "#8E7CFF", "#5AC8FA", "#FFFFFF", "#BF5AF2", "#64D2FF"])}</div>
          <div class="center">
            <div class="mark-wrap" id="mwrap">
              <svg class="mark" viewBox="{MARK["viewBox"]}">
                <defs>
                  <linearGradient id="sweepg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
                  <linearGradient id="markfill" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#C9D6FF"/><stop offset=".55" stop-color="#FFFFFF"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
                  <clipPath id="mclip">{mark_paths}</clipPath>
                </defs>
                <g id="mstroke" fill="none" stroke="#fff" stroke-width="1.6" stroke-linejoin="round">{mark_paths}</g>
                <g id="mfill" fill="url(#markfill)">{mark_paths}</g>
                <g clip-path="url(#mclip)"><rect id="msweep" x="-200" y="0" width="160" height="600" fill="url(#sweepg)" transform="rotate(20)"/></g>
              </svg>
            </div>
            <div class="lockup"><span class="by" id="lby">by</span> <span class="ct">{"".join(f'<span class="lt">{ch if ch != " " else "&nbsp;"}</span>' for ch in "Clientia Tech")}</span></div>
          </div>''', "endscene"),
        f'<div class="ph-stage" id="fstage" style="opacity:0;left:1080px">{gen3.phone(vid, "phv", dark=True)}</div>',
    ])

    css = (gen3.CSS.replace("$heroB", "#2a0806").replace("$hero", "#D8261C").replace("$acc", GOLD).replace("$pri", GOLD)
           .replace("$washA", "rgba(0,0,0,0)").replace("$washB", "rgba(0,0,0,0)").replace("$sitebg", "#0B141A").replace("$siteink", "#fff")
           .replace("$dweight", "400").replace("$dcase", "uppercase").replace("$dtrack", "-0.01em")
           .replace("$italface", "").replace("$ital", '"Display"').replace("$introsizepx", "118px"))
    css += CSS8
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    j6 = gen6.JS
    js = (j6[:j6.index("// 1 · intro")] + JS8 + re.sub(r"K\((\d+(?:\.\d+)?)\)", lambda m: f"K({float(m.group(1)) + 9:g})", j6[j6.index("// 11 · outro"):])).replace("$scenes", scenes_js).replace("$P0", str(P0)).replace("$BAR", str(BAR))
    html = (gen3.HTML.replace("$title", "Casa Digital x Coco Chicken").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)).replace('data-fade-out="2.5"', 'data-fade-out="4"'))
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


JS8 = r'''
function show(id, t) { // grow a chat slot open, then fade its bubble in
  tl.fromTo("#" + id, { height: 0 }, { height: "auto", duration: .55, ease: "power2.out" }, t);
  tl.fromTo("#" + id + " > *", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .6, ease: SOFT }, t + .15);
}
function hide(id, t) { tl.to("#" + id, { height: 0, duration: .35, ease: "power2.in" }, t); }
function dots(id, t) { tl.fromTo("#" + id + " i", { opacity: .25 }, { opacity: 1, duration: .3, stagger: .12, repeat: 3, yoyo: true, ease: "sine.inOut" }, t); }
function wire(id, t, d) {
  const p = document.getElementById(id), L = p.getTotalLength(), seg = 90;
  p.style.strokeDasharray = seg + " " + (L + seg); p.style.strokeDashoffset = seg;
  tl.set(p, { opacity: 1 }, t);
  tl.fromTo(p, { strokeDashoffset: seg }, { strokeDashoffset: -L, duration: d || 1.1, ease: "power1.inOut" }, t);
  tl.set(p, { opacity: 0 }, t + (d || 1.1));
}
function count(id, from, to, t, fmt) {
  const el = document.getElementById(id), o = { v: from };
  tl.fromTo(o, { v: from }, { v: to, duration: 1.2, ease: FINE, onUpdate: () => { el.textContent = fmt(Math.round(o.v)); } }, t);
}
const Lf = n => "L" + n.toLocaleString("en-US");

// 1 · intro
rise("#icd", 0.4, { d: 2 });
rise("#ipres .w", K(.9), { d: 1.6, st: .12 });
tl.fromTo("#ilogo", { opacity: 0, scale: .86, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(1.3));
tl.fromTo("#iname", { opacity: 0, y: 30, filter: "blur(20px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.4, ease: SOFT }, K(1.7));

// 2 · they already have the attention (their pinned TikTok plays in the phone)
rise("#f0", K(3), { d: 1.2 }); rise("#f1 .w", K(3) + .2); rise("#f2 .w", K(3) + .55); rise("#f3 .w", K(3) + .9);
tl.set("#fstage", { opacity: 1 }, K(3)); tl.set("#fstage", { opacity: 0 }, K(7));
tl.fromTo("#phv", { y: 700, rotationY: -18, rotationX: 8 }, { y: 0, rotationY: -8, rotationX: 2, duration: 2.6, ease: SOFT }, K(3));
tl.to("#phv", { rotationY: 6, rotationX: 0, duration: K(7) - K(4), ease: "sine.inOut" }, K(4));
rise("#tagv", K(4), { d: 1.4 });
[4.4, 4.9, 5.4].forEach((k, i) => rise("#st" + i, K(k), { y: 30, d: 1.4 }));

// 3 · real comments: everyone asks, nobody answers
rise("#a0", K(7), { d: 1.2 }); rise("#a1 .w", K(7) + .3); rise("#a2 .w", K(7) + .6);
[7.3, 7.8, 8.3, 8.8].forEach((k, i) => rise("#cm" + i, K(k), { y: 40, d: 1.6 }));
out("#ag1", K(9.4) - .8);
rise("#a3 .w", K(9.4)); rise("#a4 .w", K(9.4) + .45, { d: 1.8 });

// 4 · meet their WhatsApp
rise("#mp", K(11), { d: 1.4 });
rise("#me1 .w", K(11) + .3, { d: 1.8, st: .12 });
rise("#me2 .w", K(11.7), { d: 2, st: .12 });

// 5 · the bot, step by step
tl.fromTo("#phw", { y: 700, rotationY: -16, rotationX: 6 }, { y: 0, rotationY: -6, rotationX: 2, duration: 2.4, ease: SOFT }, K(13));
tl.to("#phw", { rotationY: 4, rotationX: 0, duration: K(21) - K(14), ease: "sine.inOut" }, K(14));
rise("#bdemo", K(13.5), { d: 1.2 });
rise("#b10", K(13), { d: 1.2 }); rise("#b11 .w", K(13) + .3); rise("#b12 .w", K(13) + .6);
show("m1", K(13.5)); show("t1", K(14)); dots("t1", K(14) + .3); hide("t1", K(14.5)); show("m2", K(14.5)); show("m3", K(15.2));
out("#bg1", K(15.9) - .8);
rise("#b20", K(15.9), { d: 1.2 }); rise("#b21 .w", K(15.9) + .3); rise("#b22 .w", K(15.9) + .6);
show("m4", K(16.3)); show("t2", K(16.8)); dots("t2", K(16.8) + .3); hide("t2", K(17.3)); show("m5", K(17.3));
tl.fromTo("#okbtn", { opacity: 0 }, { opacity: 1, duration: .25, yoyo: true, repeat: 1 }, K(18.4));
out("#bg2", K(18.6) - .8);
rise("#b30", K(18.6), { d: 1.2 }); rise("#b31 .w", K(18.6) + .3); rise("#b32 .w", K(18.6) + .6);
show("m6", K(18.6)); show("t3", K(19.1)); dots("t3", K(19.1) + .3); hide("t3", K(19.6)); show("m7", K(19.6));

// 6 · everything connected: phone -> kitchen -> panel -> back to the customer
rise("#lk1 .w", K(21), { d: 1.6 });
[21.2, 21.5, 21.8].forEach((k, i) => tl.fromTo("#dv" + i, { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(k)));
rise("#ldemo", K(22), { d: 1.2 });
wire("wa", K(22.4), 1.2);
tl.fromTo("#tnew", { opacity: 0, x: -40, scale: .96 }, { opacity: 1, x: 0, scale: 1, duration: 1, ease: SOFT }, K(22.4) + 1.1);
wire("wb", K(23.2), 1);
count("nv", 52105, 52275, K(23.2) + .9, Lf); count("nr", 37, 38, K(23.2) + .9, n => String(n));
tl.fromTo("#lb1", { scaleX: 1 }, { scaleX: 1.04, duration: 1.2, ease: FINE }, K(23.2) + .9);
tl.fromTo("#tok", { opacity: 0 }, { opacity: 1, duration: .3 }, K(24.4));
tl.to("#tnew", { x: 414, duration: 1.4, ease: "power3.inOut" }, K(24.4) + .3);
tl.fromTo("#tok", { scale: .6 }, { scale: 1, duration: .5, ease: "back.out(2)" }, K(24.4));
wire("wc", K(25.2), 1.4);
tl.fromTo("#mnot", { y: -120, opacity: 0 }, { y: 0, opacity: 1, duration: .9, ease: "back.out(1.3)" }, K(25.2) + 1.3);

// 7 · the real owner panel
tl.fromTo("#shot", { opacity: 0, y: 80, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(27) + .2);
tl.fromTo("#shot img", { scale: 1 }, { scale: 1.035, duration: K(31) - K(27), ease: "none", transformOrigin: "30% 30%" }, K(27));
rise("#o0", K(27), { d: 1.2 }); rise("#o1 .w", K(27) + .3); rise("#o2 .w", K(27) + .6);
[28.2, 28.7, 29.2].forEach((k, i) => rise("#ob" + i + " .w, #ob" + i + " i", K(k), { st: .04, d: 1.3 }));
rise("#odemo", K(27.6), { d: 1.2 });

// 8a · the numbers: commission they keep
rise("#y0", K(31), { d: 1.2 }); rise("#y1 .w", K(31) + .3); rise("#y2 .w", K(31) + .6, { d: 1.8 });
rise("#y3 .w", K(32.2), { st: .03 });
tl.fromTo("#calc", { opacity: 0, y: 70, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(31) + .3);
[31.6, 32.2, 32.8].forEach((k, i) => rise("#cr" + i, K(k), { y: 24, d: 1.3 }));
rise("#cres", K(33.4), { y: 30, d: 1.4 });
count("nsav", 0, 10500, K(33.5), Lf);
rise("#cyr", K(34.4), { y: 20, d: 1.4 });
rise("#yfoot", K(32), { d: 1.2 });

// 8b · opportunities: what their own comments ask for
rise("#h0", K(36), { d: 1.2 }); rise("#h1 .w", K(36) + .3); rise("#h2 .w", K(36) + .6, { d: 1.8 });
rise("#h3 .w", K(37.2), { st: .03 });
[36.3, 36.8, 37.3].forEach((k, i) => rise("#ti" + i, K(k), { y: 40, d: 1.6 }));
document.querySelectorAll("#chances .cnt").forEach((el, i) => {
  const o = { v: 0 }, n = +el.dataset.n;
  tl.fromTo(o, { v: 0 }, { v: n, duration: 1.4, ease: FINE, onUpdate: () => { el.textContent = Math.round(o.v); } }, K(36.5 + i * .5));
});
rise("#hfoot", K(37), { d: 1.2 });

// 8 · their promo and their videos
rise("#x1 .w", K(40)); rise("#x2 .w", K(40) + .3); rise("#x3 .w", K(40) + .6, { d: 1.8 });
rise("#x4 .w", K(41), { st: .03 });
tl.fromTo("#stamp", { opacity: 0, y: 70, rotation: -2 }, { opacity: 1, y: 0, rotation: 0, duration: 2, ease: SOFT }, K(40) + .2);
[40.7, 40.95, 41.2, 41.5].forEach((k, i) => tl.fromTo("#sb" + i, { opacity: 0, scale: 1.6 }, { opacity: 1, scale: 1, duration: .6, ease: "back.out(2)" }, K(k)));
tl.fromTo("#tkc", { opacity: 0, y: 70 }, { opacity: 1, y: 0, duration: 2, ease: SOFT }, K(40.6));
[0, 1, 2].forEach(i => tl.fromTo("#tkb" + i, { scaleX: 0 }, { scaleX: 1, duration: 1.6, ease: FINE }, K(41.2) + i * .25));
rise("#xdemo", K(40.8), { d: 1.2 });

// 9 · Casa Digital
rise("#u0", K(43), { d: 1.2 }); rise("#u1 .w", K(43) + .3); rise("#u2 .w", K(43) + .7, { d: 1.8 });
[43.9, 44.4, 44.9].forEach((k, i) => rise("#wy" + i + " .w, #wy" + i + " i", K(k), { st: .04, d: 1.3 }));
tl.fromTo("#cta", { opacity: 0, y: 90, scale: .95 }, { opacity: 1, y: 0, scale: 1, duration: 2.2, ease: SOFT }, K(43.5));
float("#cta", K(44.4), K(46) - K(44.4));

'''

if __name__ == "__main__":
    print(build())
