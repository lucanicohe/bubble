// ===== setup =====
const A={"ch": {"idle": [[4, 4, 50, 47], [55, 5, 50, 46], [106, 6, 50, 45], [157, 5, 50, 46], [208, 4, 50, 47], [259, 4, 50, 47]], "crank": [[4, 110, 52, 47], [57, 108, 52, 49], [110, 110, 52, 47], [163, 112, 52, 45], [216, 110, 52, 47]], "crouch": [4, 172, 52, 35], "air1": [[57, 160, 52, 51], [110, 160, 52, 51], [165, 160, 50, 49], [217, 160, 51, 52]], "air2": [[4, 270, 49, 51], [54, 273, 52, 48], [107, 273, 52, 48], [160, 274, 52, 47]], "squish": [[5, 215, 51, 52], [57, 227, 52, 40], [110, 239, 52, 28], [163, 245, 52, 22]], "shoot": [[216, 54, 52, 51], [269, 55, 52, 50]], "danger": [[355, 103, 51, 47], [409, 103, 51, 47]], "happy": [[253, 227, 102, 100], [358, 229, 102, 98]], "lose": [[253, 335, 98, 90], [354, 335, 98, 90]]}};
const SRC={ch:'assets/hero_character.png',hb:'assets/blob_bubbles.png',fr:'assets/triple_bubble_sprites_-_playfield_frames__1_.png',bb:'assets/triple_bubble_sprites_-_bubbles_and_others.png',neb:'assets/Green_Nebula_07-512x512.png'};
const cv=document.getElementById('c'),ctx=cv.getContext('2d');
const W=514,H=458,C=16,B=30,RH=26,FX=17,FY=39,PX=257,PY=402,LOSE=12,NR=15;
cv.width=W;cv.height=H;
const LET='brgyockp'; // blue red green yellow orange cyan gray purple, # = gold block
// 隣接判定: neighbour offsets, DIRS[rowParity][k] = [dRow,dCol] (3D array)
const DIRS=[[[-1,-1],[-1,0],[0,-1],[0,1],[1,-1],[1,0]],[[-1,0],[-1,1],[0,-1],[0,1],[1,0],[1,1]]];
// 多次元配列: LEVELS[level][row] = string, one char per bubble
const LEVELS=[
["#......#g#.....#","poooo.gg.oooop.","popoooo.g.opoooop","ppooo.gg.gpoopp","yyypppbgogbpppyy","ybbrgg.gg.rbbby",".rrrooo..ooorrr.."],
["bbrrggyybbrrggyy","bbrrggyybbrrggy","ggyybbrrggyybbrr","ggyybbrrggyybbr","..bbrr....ggyy.."],
["rrrrrrrrbbbbbbbb","ooooooooppppppp","ggggggggyyyyyyyy","..rrbbooyyppgg","....rrbbgg.."],
["c.b.c.b.c.b.c.b.","rcrbrcrbrcrbrcr","gygrgygrgygrgygr","popcpopcpopcpop","bbbbrrrrggggyyyy",".ycyoyoyoyoycy."]];
const rl=r=>r&1?C-1:C; // row length: odd rows are shifted and one shorter
const newGrid=v=>Array.from({length:NR},()=>Array(C).fill(v)); // 二次元配列
let landAt={},bump=null,curT=0,nxtT=0,DG=false; // landing squash times, ripple from the last hit, when cur/nxt arrived, stack-in-danger flag
let grid,drop,left,cur,nxt,ang=90,pang=90,crankT=0,overT=0,crushY=0,shot,score=0,round=1,state='title',idle=0,t=0,shootT=0,rot=0,clearT=0,fx=[],falls=[];
const cx=(r,c)=>FX+c*B+B/2+(r&1?B/2:0), cy=r=>FY+(r+drop)*RH+B/2;
const colors=()=>{const s=new Set();grid.forEach(r=>r.forEach(v=>{if(v>=0&&v<8)s.add(v)}));return s};
const pick=()=>{const a=[...colors()];return a.length?a[Math.random()*a.length|0]:0};
const interval=()=>colors().size+2; // ceiling drops sooner when fewer colours remain (approximation)
function load(n){
  grid=newGrid(-1);
  LEVELS[(n-1)%LEVELS.length].forEach((s,r)=>[...s.padEnd(rl(r),'.').slice(0,rl(r))].forEach((ch,c)=>{grid[r][c]=ch=='#'?9:LET.indexOf(ch)}));
  drop=0;left=interval();cur=pick();nxt=pick();curT=nxtT=t;landAt={};bump=null;shot=null;fx=[];falls=[];idle=0;
}
const nb=(r,c)=>DIRS[r&1].map(([a,b])=>[r+a,c+b]).filter(([y,x])=>y>=0&&y<NR&&x>=0&&x<rl(y));
// 再帰: flood fill of same-colour bubbles (連鎖による消去)
function flood(r,c,col,seen,out){
  if(seen[r][c]||grid[r][c]!==col)return;
  seen[r][c]=true;out.push([r,c]);
  nb(r,c).forEach(([y,x])=>flood(y,x,col,seen,out));
}
// 再帰: mark everything still hanging from the ceiling
function anchor(r,c,seen){
  if(seen[r][c]||grid[r][c]<0)return;
  seen[r][c]=true;nb(r,c).forEach(([y,x])=>anchor(y,x,seen));
}
function land(r,c,col){
  grid[r][c]=col;
  const seen=newGrid(false),g=[];flood(r,c,col,seen,g);
  if(g.length>=3){
    g.forEach(([y,x])=>{fx.push({x:cx(y,x),y:cy(y),f:0,c:col});grid[y][x]=-1});
    score+=g.length*10;
    const an=newGrid(false);for(let x=0;x<rl(0);x++)anchor(0,x,an);
    let n=0;
    for(let y=0;y<NR;y++)for(let x=0;x<rl(y);x++)if(grid[y][x]>=0&&grid[y][x]<9&&!an[y][x]){
      falls.push({x:cx(y,x),y:cy(y),vx:(Math.random()-.5)*2,vy:-2,col:grid[y][x]});
      score+=10<<Math.min(++n,11); // 20, 40, 80 ...
      grid[y][x]=-1;
    }
  }
  if(g.length<3){landAt[r*32+c]=t;bump={x:cx(r,c),y:cy(r),t}}
  if(!colors().size){state='clear';clearT=200;return}
  if(--left<=0){drop++;left=interval()}
  if(!colors().has(cur)){cur=pick();curT=t}if(!colors().has(nxt)){nxt=pick();nxtT=t}
  for(let y=0;y<NR;y++)for(let x=0;x<rl(y);x++)if(grid[y][x]>=0&&y+drop>=LOSE)state='over';
}
function hit(x,y){
  if(y<=FY+drop*RH+B/2)return true;
  for(let r=0;r<NR;r++)for(let c=0;c<rl(r);c++)if(grid[r][c]>=0&&(cx(r,c)-x)**2+(cy(r)-y)**2<27*27)return true;
  return false;
}
function snap(){
  let best,bd=1e9;
  for(let r=0;r<NR;r++)for(let c=0;c<rl(r);c++)if(grid[r][c]<0&&(r==0||nb(r,c).some(([y,x])=>grid[y][x]>=0))){
    const d=(cx(r,c)-shot.x)**2+(cy(r)-shot.y)**2;if(d<bd){bd=d;best=[r,c]}
  }
  const col=shot.c;shot=null;idle=0;land(best[0],best[1],col);
}
function fire(auto){
  if(shot||state!='play')return;
  const a=(auto?90:ang)*Math.PI/180;
  shot={x:PX,y:PY,vx:9*Math.cos(a),vy:-9*Math.sin(a),c:cur,age:0};cur=nxt;nxt=pick();curT=nxtT=t;shootT=14;idle=0;
}
function start(){score=0;round=1;load(1);state='play'}
// ===== input =====
const keys={};
addEventListener('keydown',e=>{keys[e.key]=1;if(e.key==' '||e.key=='ArrowUp'){e.preventDefault();if(state=='play')fire();else if(state=='title'||state=='over')start()}if(e.key.startsWith('Arrow'))e.preventDefault()});
addEventListener('keyup',e=>keys[e.key]=0);
function aimAt(e){const r=cv.getBoundingClientRect(),x=(e.clientX-r.left)*W/r.width,y=(e.clientY-r.top)*H/r.height;ang=Math.max(12,Math.min(168,Math.atan2(PY-y,x-PX)*180/Math.PI))}
cv.addEventListener('pointermove',aimAt);
cv.addEventListener('pointerdown',e=>{aimAt(e);if(state=='play')fire();else if(state=='title'||state=='over')start()});
// ===== update =====
const lowRow=()=>{let m=0;grid.forEach((row,r)=>row.forEach(v=>{if(v>=0)m=Math.max(m,r+drop)}));return m};
const SQ=n=>A.ch.squish[n<26?0:n<36?1:n<46?2:3]; // scared look up, squashed, flatter, dead with X eyes
function step(){
  t++;rot=0;
  if(state=='play'){
    if(keys.ArrowLeft){ang=Math.min(168,ang+1.6);rot=1}
    if(keys.ArrowRight){ang=Math.max(12,ang-1.6);rot=-1}
    if(!shot&&++idle>=600)fire(true); // auto fire after 10 s
    if(shot)shot.age++;
    for(let k=0;k<3&&shot;k++){
      shot.x+=shot.vx/3;shot.y+=shot.vy/3;
      if(shot.x<FX+B/2){shot.x=FX+B/2;shot.vx*=-1}
      if(shot.x>FX+C*B-B/2){shot.x=FX+C*B-B/2;shot.vx*=-1}
      if(hit(shot.x,shot.y))snap();
    }
  }
  if(state=='clear'&&--clearT<=0){round++;load(round);state='play'}
  if(state=='over'){overT++;const f=SQ(overT),tgt=Math.max(0,H-19-f[3]-(FY+lowRow()*RH+B));crushY+=(tgt-crushY)*.2}else{overT=0;crushY=0} // formation presses down on him as he flattens
  if(shootT>0)shootT--;
  if(bump&&t-bump.t>22)bump=null;
  if(Math.abs(ang-pang)>.01)crankT=10;else if(crankT>0)crankT--;
  pang=ang;
  fx.forEach(f=>f.f++);fx=fx.filter(f=>f.f<18);
  falls.forEach(f=>{f.vy+=.45;f.y+=f.vy;f.x+=f.vx});falls=falls.filter(f=>f.y<H+20);
}
// ===== draw =====
const im={};
const spr=(k,r,x,y,s=1)=>ctx.drawImage(im[k],r[0],r[1],r[2],r[3],Math.round(x),Math.round(y),r[2]*s,r[3]*s);
// ===== bubble characters: blob sheet = 8 colours (rows) x 28 frames (columns) of 32x32 =====
const BF={idle:0,blink:4,look:5,scared:8,grin:10,roll:11,land:15,fall:18,wave:20,pop:22}; // first frame of each animation
const chr=(c,f,x,y)=>ctx.drawImage(im.hb,f*32,c*32,32,32,Math.round(x)-16,Math.round(y)-17,32,32);
// stable per-cell random number: every character keeps its own timing so the stack never moves in lockstep
const hsh=(r,c)=>{let h=Math.imul(r+1,73856093)^Math.imul(c+1,19349663);h=Math.imul(h^h>>>15,2246822519);return(h^h>>>13)>>>0};
// frame for a character sitting in the stack: breathing bob, blinks, glances, shivers when the stack is low, smirks on game over
function restFrame(r,c){
  const h=hsh(r,c),la=landAt[r*32+c];
  if(la!=null){const a=t-la;if(a<12)return BF.land+(a/4|0);delete landAt[r*32+c]} // squash, stretch, settle
  if(state=='over')return BF.grin;
  if(DG)return BF.scared+((t>>2)+h&1); // shiver
  if((t+h)%(200+(h>>8)%160)<7)return BF.blink;
  if((t+(h>>4))%520<46)return BF.look+(h&2?0:2); // quick glance left or right
  return BF.idle+((((t+(h&1023))/9)|0)%4);
}
// ripple: the stack wobbles away from the spot where a shot landed
function jig(x,y){
  if(!bump)return[0,0];const a=t-bump.t,dx=x-bump.x,dy=y-bump.y,d=Math.hypot(dx,dy);
  if(d<1||d>110)return[0,0];const m=3*Math.exp(-d/40)*(1-a/22)*Math.sin(a*.8);
  return[Math.round(dx/d*m),Math.round(dy/d*m)];
}
// loaded character: hops in after a shot, then watches where you aim
function readyFrame(){
  const a=t-curT;if(a<12)return BF.land+(a/4|0);
  if(t%230<6)return BF.blink;
  return BF.look+(ang<78?2:ang>102?0:1);
}
// next character: hops in, then waves from beside the sign
function waitFrame(){const a=t-nxtT;return a<12?BF.land+(a/4|0):BF.wave+(t>>4&1)}
function txt(s,x,y,al='left',sz=14){
  ctx.font=sz+'px "Press Start 2P",monospace';ctx.textAlign=al;ctx.textBaseline='middle';
  ctx.lineWidth=4;ctx.strokeStyle='#103010';ctx.lineJoin='round';ctx.strokeText(s,x,y);ctx.fillStyle='#4cf04c';ctx.fillText(s,x,y);
}
function block(x,y){ // gold ceiling block, concentric pixel octagons
  [[1,28,9,'#6a4a10'],[3,24,8,'#d8b040'],[6,18,6,'#f4dc80'],[9,12,4,'#c8982c'],[12,6,2,'#f4dc80']].forEach(([i,s,k,c])=>{
    ctx.fillStyle=c;for(let j=0;j<s;j++){const d=Math.max(0,k-Math.min(j,s-1-j));ctx.fillRect(x+i+d,y+i+j-1,s-2*d,1)}
  });
}
function draw(){
  ctx.imageSmoothingEnabled=false;DG=lowRow()>=LOSE-3;
  const o=(t*.12)%256;for(let x=-o;x<W;x+=256)for(let y=-o;y<H;y+=256)ctx.drawImage(bg,Math.round(x),Math.round(y));
  // wooden frame from the playfield sheet
  const top=[153,267,514,17];spr('fr',top,0,22);spr('fr',top,0,H-17);
  [0,W-17].forEach(x=>{for(let y=39;y<H-17;y+=346)ctx.drawImage(im.fr,40,10,17,346,x,y,17,Math.min(346,H-17-y))});
  ctx.save();ctx.beginPath();const cH=drop*RH+Math.round(crushY);ctx.rect(FX,FY,C*B,cH);ctx.clip();
  for(let y=FY;y<FY+cH;y+=17)ctx.drawImage(im.fr,153,267,C*B,17,FX,y,C*B,17);ctx.restore();
  ctx.fillStyle='#e8c020';ctx.fillRect(FX,FY+LOSE*RH,C*B,2);
  let low=0;ctx.save();ctx.translate(0,Math.round(crushY));
  for(let r=0;r<NR;r++)for(let c=0;c<rl(r);c++){const v=grid[r][c];if(v<0)continue;low=Math.max(low,r+drop);if(v==9)block(cx(r,c)-B/2,cy(r)-B/2);else{const x=cx(r,c),y=cy(r),j=jig(x,y);chr(v,restFrame(r,c),x+j[0],y+j[1])}}
  ctx.restore();falls.forEach(f=>chr(f.col,BF.fall+(t>>3&1),f.x,f.y)); // screaming as they drop
  fx.forEach(f=>chr(f.c,BF.pop+(f.f/3|0),f.x,f.y)); // surprise, flash, burst
  // aim guide dots (bounces off walls like the real shot)
  if(state=='play'){
    let x=PX,y=PY,a=ang*Math.PI/180,vx=Math.cos(a)*4,vy=-Math.sin(a)*4;
    for(let i=0;i<110;i++){x+=vx;y+=vy;if(x<FX+B/2||x>FX+C*B-B/2)vx*=-1;if(hit(x,y))break;if(i>6&&i%4==0){ctx.fillStyle='#101820';ctx.fillRect(x-1,y-1,3,3)}}
  }
  // launcher: wheel, arrow, loaded + next bubble
  ctx.save();ctx.translate(PX-41,406);ctx.rotate((ang*3|0)*Math.PI/180);spr('bb',[298,364,63,63],-31.5,-31.5);ctx.restore();
  chr(cur,readyFrame(),PX,PY);
  ctx.save();ctx.translate(PX,PY);ctx.rotate(((90-ang)/2|0)*2*Math.PI/180);spr('bb',[291,259,49,89],-24,-52);ctx.restore();
  spr('bb',[369,377,43,50],PX+60,PY-10);chr(nxt,waitFrame(),PX+84,PY+22);
  // red blob character
  const ch=A.ch;let a,flip=0;
  let hop=0;
  if(state=='over')a=SQ(overT);
  else if(state=='clear'){ // jump for joy: crouch, stretched air frames while hopping, crouch on landing, alternate frame sets each hop
    const u=200-clearT,ph=u%64,k=u/64|0;
    if(ph<8||ph>=56)a=ch.crouch;else{const q=(ph-8)/48;hop=Math.sin(Math.PI*q)*44;a=(k&1?ch.air2:ch.air1)[Math.min(3,q*4|0)]}
  }
  else if(shootT>0)a=ch.shoot[shootT>7?0:1];else if(crankT>0)a=ch.crank[(Math.floor(ang*3/9)%5+5)%5]; // side view pushing the wheel, frame follows the wheel angle
  else if(low>=LOSE-3)a=ch.danger[t>>4&1];else a=ch.idle[(t>>4)%6];
  const s=a[2]>80?.5:1;
  ctx.save();ctx.translate(171,H-19-a[3]*s-hop);if(flip)ctx.scale(-1,1);ctx.drawImage(im.ch,a[0],a[1],a[2],a[3],-a[2]*s/2,0,a[2]*s,a[3]*s);ctx.restore();
  if(shot){const k=shot.age/3&3;chr(shot.c,BF.roll+(shot.vx<0?3-k:k),shot.x,shot.y)} // tumbling through the air
  // HUD
  txt('P1',20,10);txt(String(score),W/2-40,10,'center');txt('ROUND '+round,W/2+90,10);
  if(state!='play'&&!(state=='over'&&overT<50)){
    ctx.fillStyle='rgba(0,0,0,.55)';ctx.fillRect(FX,FY+110,C*B,120);
    const msg={title:'PUZZLE BOBBLE',over:'GAME OVER',clear:'ROUND CLEAR!'}[state];
    txt(msg,W/2,FY+150,'center',22);
    if(state!='clear'&&(t>>5&1))txt('PRESS SPACE',W/2,FY+195,'center',14);
  }
}
let last=0,acc=0;
function loop(ts){acc+=Math.min(ts-last,100);last=ts;while(acc>=16.667){step();acc-=16.667}draw();requestAnimationFrame(loop)}
// pixel-art nebula: downsample, 6 levels per channel, Bayer dither, 2x blocks
function makeBG(img){
  const s=document.createElement('canvas');s.width=s.height=128;const x=s.getContext('2d');x.drawImage(img,0,0,128,128);
  const d=x.getImageData(0,0,128,128),M=[0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5];
  for(let i=0;i<d.data.length;i+=4){const p=i/4,j=M[(p%128&3)|((p/128|0)&3)<<2]/16-.5;for(let k=0;k<3;k++)d.data[i+k]=Math.max(0,Math.min(255,Math.round((d.data[i+k]*.8+j*51)/51)*51))}
  x.putImageData(d,0,0);
  bg=document.createElement('canvas');bg.width=bg.height=256;const b=bg.getContext('2d');b.imageSmoothingEnabled=false;b.drawImage(s,0,0,256,256);
}
let bg;
Promise.all(Object.keys(SRC).map(k=>new Promise(ok=>{const i=new Image();i.onload=ok;i.src=SRC[k];im[k]=i}))).then(()=>{
  makeBG(im.neb);load(1);document.fonts&&document.fonts.load('14px "Press Start 2P"');requestAnimationFrame(loop);
});
