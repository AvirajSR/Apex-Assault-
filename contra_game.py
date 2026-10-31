#!/usr/bin/env python3
"""Original run-and-gun cleanup game: files are targets, shots execute chore actions."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import html, json, os, shutil, uuid
from chorequest.executor import Executor
from chorequest.chores import FolderChore
from chorequest.mapping import folder_action

ROOT = Path(__file__).parent; DATA = ROOT / "runtime" / "sandbox_folder"
def reset_data():
    if DATA.exists(): shutil.rmtree(DATA)
    shutil.copytree(ROOT / "sample_data" / "messy_folder", DATA)
reset_data(); session = uuid.uuid4().hex[:8]; chore = FolderChore(DATA, Executor(DATA, session))

def expected_for(item):
    ext = item.suffix.lower()
    return "Archive" if ext in (".zip", ".rar", ".7z") else ("Media" if ext in (".jpg", ".png", ".mp3", ".wav", ".mp4") else "Documents")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global chore, session
        query = parse_qs(urlparse(self.path).query); action = query.get("action", [""])[0]
        if action == "reset":
            reset_data(); session = uuid.uuid4().hex[:8]; chore = FolderChore(DATA, Executor(DATA, session))
        item = chore.next_item(); expected = expected_for(item) if item else None; success = False
        if action in ("a", "s", "d") and item and folder_action(action) == expected:
            chore.apply(action); success = True
        item = chore.next_item(); payload = {"success": success, "complete": not bool(item), "name": item.name if item else "CLEAR", "remaining": len(chore.items), "target": expected_for(item) if item else "CLEAR"}
        if query.get("ajax", [""])[0] == "1":
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(json.dumps(payload).encode()); return
        name = html.escape(payload["name"])
        page = f'''<!doctype html><meta name="viewport" content="width=device-width"><title>Cleanup Assault</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#080808;color:#eee;font:14px ui-monospace,monospace;text-align:center}}main{{max-width:1040px;margin:auto;padding:18px}}h1{{font:700 28px Arial;letter-spacing:5px;margin:4px;color:#fff}}h1 b{{color:#d71920}}p{{color:#aaa}}#wrap{{border:1px solid #444;background:#111;padding:10px;box-shadow:0 0 0 4px #191919}}canvas{{display:block;width:100%;height:auto;background:#050505;cursor:crosshair}}.controls{{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:12px}}button{{background:#111;color:#fff;border:1px solid #777;padding:10px 16px;font:700 12px monospace;cursor:pointer}}button:hover,button.sel{{border-color:#e21b23;color:#ff5151}}.note{{font-size:12px;color:#888}}a{{color:#aaa}}#healthbar{{height:10px;background:#333;border:1px solid #777;max-width:420px;margin:10px auto}}#hp{{height:100%;width:100%;background:#d71920;transition:.2s}}</style>
<main><h1>CLEANUP <b>ASSAULT</b></h1><p>AN ORIGINAL ARCADE CLEANUP MISSION — SHOOT A FILE, EXECUTE A REAL MOVE</p><div id="wrap"><canvas id="game" width="960" height="540"></canvas></div><div id="healthbar"><div id="hp"></div></div><div class="controls"><button id="b0" onclick="weapon(0)">1 · DOCUMENTS</button><button id="b1" onclick="weapon(1)">2 · MEDIA</button><button id="b2" onclick="weapon(2)">3 · ARCHIVE</button><button onclick="resetGame()">RESET MISSION</button></div><p class="note">MOVE: ← → or A/D · JUMP: ↑ or W · FIRE: SPACE or CLICK · SELECT WEAPON: 1/2/3 · HEALTH: <span id="health">100</span>% · FILES LEFT: <span id="remaining">8</span> · SCORE: <span id="score">0</span></p><p><a href="/?action=reset">Open classic sorter</a></p></main>
<script>
const C=document.getElementById('game'),x=C.getContext('2d');let keys={{}},player={{x:110,y:430,vy:0,health:100}},bullets=[],enemyBullets=[],enemy={{x:850,y:420,cool:70}},weaponId=0,lives=5,score=0,done=false,last=0,shake=0,freeze=0,camera=0,jumpBoost=0,killBoost=0,deadFlash=0,targetClass={expected_for(chore.next_item())!r};const names=['DOCUMENTS','MEDIA','ARCHIVE'],codes=['a','s','d'],world=2800,obstacles=[{{x:530,w:54,h:50}},{{x:920,w:74,h:80}},{{x:1410,w:52,h:65}},{{x:2040,w:92,h:90}}],boosts=[{{x:700,type:'JUMP'}},{{x:1260,type:'KILL'}},{{x:1840,type:'JUMP'}},{{x:2450,type:'KILL'}}];
document.addEventListener('keydown',e=>{{keys[e.key.toLowerCase()]=true;if([' ','arrowup','arrowleft','arrowright'].includes(e.key.toLowerCase()))e.preventDefault();if('123'.includes(e.key))weapon(Number(e.key)-1);if(e.key===' ')shoot()}});document.addEventListener('keyup',e=>keys[e.key.toLowerCase()]=false);C.addEventListener('click',shoot);
function weapon(i){{weaponId=i;for(let n=0;n<3;n++)document.getElementById('b'+n).classList.toggle('sel',n===i)}}weapon(0);function resetGame(){{location.href='/?action=reset'}}
function shoot(){{if(done||bullets.length>5)return;bullets.push({{x:player.x+32,y:player.y+10,v:12}})}}
function hit(){{fetch('/?action='+codes[weaponId]+'&ajax=1').then(r=>r.json()).then(d=>{{if(d.success){{score+=killBoost?250:100;document.getElementById('score').textContent=score;document.getElementById('remaining').textContent=d.remaining;targetClass=d.target;deadFlash=28;document.title='TARGET ELIMINATED';enemy.x=player.x+650;enemy.y=420;freeze=35}}else if(d.complete){{done=true}}else{{player.health-=25;document.getElementById('health').textContent=Math.max(0,player.health);document.getElementById('hp').style.width=Math.max(0,player.health)+'%';shake=12;if(player.health<=0)done=true}}if(d.complete)done=true}})}}
function hurt(){{player.health-=10;document.getElementById('health').textContent=Math.max(0,player.health);document.getElementById('hp').style.width=Math.max(0,player.health)+'%';shake=10;if(player.health<=0)done=true}}
function draw(t){{let dt=Math.min((t-last)/16,2);last=t;if(!done){{let left=keys['arrowleft']||keys['a'],right=keys['arrowright']||keys['d'];let speed=jumpBoost?6:4;if(left)player.x-=speed*dt;if(right)player.x+=speed*dt;if((keys['arrowup']||keys['w'])&&player.y>=430)player.vy=jumpBoost?-17:-12;player.vy+=.55*dt;player.y+=player.vy*dt;if(player.y>430){{player.y=430;player.vy=0}}player.x=Math.max(30,Math.min(world-80,player.x));camera=Math.max(0,Math.min(world-960,player.x-280));if(freeze>0)freeze-=dt;else enemy.x-=.45*dt;if(enemy.x<camera+20)enemy.x=camera+850;enemy.cool-=dt;if(enemy.cool<0&&Math.abs(enemy.x-player.x)<700){{enemyBullets.push({{x:enemy.x,y:enemy.y-5,v:-6}});enemy.cool=95}}bullets.forEach(b=>b.x+=b.v*dt);enemyBullets.forEach(b=>b.x+=b.v*dt);if(bullets.some(b=>b.x>enemy.x-20&&b.x<enemy.x+85&&Math.abs(b.y-enemy.y)<55)){{bullets=[];hit()}}if(enemyBullets.some(b=>Math.abs(b.x-player.x)<28&&Math.abs(b.y-player.y)<50)){{enemyBullets=[];hurt()}}bullets=bullets.filter(b=>b.x<world);enemyBullets=enemyBullets.filter(b=>b.x>0);obstacles.forEach(o=>{{if(Math.abs(player.x-o.x)<o.w&&player.y>430-o.h&&player.y<440)player.x=left?o.x+o.w:o.x-30}});boosts.forEach(b=>{{if(!b.got&&Math.abs(player.x-b.x)<35&&player.y>380){{b.got=true;if(b.type==='JUMP'){{jumpBoost=420}}else{{killBoost=420}}}}}});if(jumpBoost>0)jumpBoost-=dt;if(killBoost>0)killBoost-=dt}}
let sx=shake?Math.random()*shake-shake/2:0;shake*=.85;x.save();x.translate(-camera+sx,0);x.fillStyle='#050505';x.fillRect(camera,0,960,540);x.fillStyle='#181818';for(let i=0;i<45;i++)x.fillRect(i*70,390-(i%4)*18,42,70+(i%4)*18);x.fillStyle='#242424';x.fillRect(0,470,world,70);obstacles.forEach(o=>{{x.fillStyle='#555';x.fillRect(o.x,470-o.h,o.w,o.h);x.fillStyle='#aaa';x.fillRect(o.x+8,470-o.h+8,o.w-16,5)}});boosts.forEach(b=>{{if(!b.got){{x.strokeStyle='#fff';x.strokeRect(b.x-17,400,34,34);x.fillStyle='#d71920';x.font='bold 11px monospace';x.fillText(b.type,b.x-15,422)}}}});x.fillStyle='#d71920';x.fillRect(player.x,player.y,28,42);x.fillStyle='#fff';x.fillRect(player.x+19,player.y+9,20,8);x.fillStyle='#aaa';x.fillRect(player.x+7,player.y+42,7,12);x.fillRect(player.x+21,player.y+42,7,14);bullets.forEach(b=>{{x.fillStyle='#fff';x.fillRect(b.x,b.y,16,4)}});enemyBullets.forEach(b=>{{x.fillStyle='#d71920';x.fillRect(b.x,b.y,12,5)}});x.fillStyle='#d71920';x.fillRect(enemy.x,enemy.y-35,86,65);x.fillStyle='#080808';x.fillRect(enemy.x+7,enemy.y-27,72,50);x.fillStyle='#fff';x.font='bold 12px monospace';x.fillText('OPPONENT',enemy.x+12,enemy.y-7);x.fillStyle='#aaa';x.fillText('ARMED FILE',enemy.x+12,enemy.y+10);x.fillStyle='#fff';x.font='bold 16px monospace';x.fillText('WEAPON: '+names[weaponId],camera+24,34);x.fillStyle='#d71920';x.fillText('INCOMING: '+{name!r},camera+24,58);if(done){{x.fillStyle='rgba(0,0,0,.82)';x.fillRect(camera,0,960,540);x.fillStyle='#fff';x.font='bold 34px Arial';x.textAlign='center';x.fillText(player.health?'MISSION COMPLETE':'GAME OVER',camera+480,260);x.font='16px monospace';x.fillText('RESET MISSION TO PLAY AGAIN',camera+480,295);x.textAlign='left'}}x.restore();requestAnimationFrame(draw)}}requestAnimationFrame(draw);
</script>'''
        self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers(); self.wfile.write(page.encode())
    def log_message(self, *_): pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001")); print(f"Cleanup Assault running at http://localhost:{port}"); HTTPServer(("0.0.0.0", port), Handler).serve_forever()
