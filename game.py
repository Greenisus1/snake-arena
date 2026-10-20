#!/usr/bin/env python3
"""Offline rival-snake arena. Original grid game, not an online service."""
import curses,random,time

try:
    import pi18n
except ImportError:
    pi18n = None

# English UI strings; the Translations app owns every language via ~/pi-translations.
DEFAULT_STRINGS = {'HUD': 'SNAKE ARENA  food {score} length {length} rivals {rivals}', 'RESIZE': 'Resize or R to refit (minimum 66x23).', 'GAME_OVER': 'GAME OVER. R restarts', 'RULES': 'Walls wrap. Your own body is safe. Rival bodies still bite - their remains are food.', 'CONTROLS': 'Arrows/WASD turn | Space pause | R restart | Esc/q exit'}
from ui import put,run
DIRS=((1,0),(-1,0),(0,1),(0,-1))
VERSION='1.3.0'
RESPAWN_TICKS=40
class Arena:
 def __init__(self,w=32,h=18,seed=0):
  self.w=w;self.h=h;self.rng=random.Random(seed);self.snakes=[[(5,5),(4,5),(3,5)],[(w-6,5),(w-5,5),(w-4,5)],[(w-6,h-6),(w-5,h-6),(w-4,h-6)]];self.direction=(1,0);self.alive=[True]*3;self.food=set();self.score=0;self.respawn=[0]*3;self.tick=0;self.refill()
 def wrap(self,p):return (p[0]%self.w,p[1]%self.h)
 def dist(self,a,b):
  dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,self.w-dx)+min(dy,self.h-dy)
 def refill(self):
  used={p for s in self.snakes for p in s}|self.food;free=[(x,y) for x in range(self.w) for y in range(self.h) if (x,y) not in used];self.rng.shuffle(free);self.food.update(free[:max(0,18-len(self.food))])
 def respawn_cells(self):
  used={p for s in self.snakes for p in s}|self.food
  for _ in range(60):
   x=self.rng.randrange(self.w);y=self.rng.randrange(self.h);cells=[(x,y),((x-1)%self.w,y),((x-2)%self.w,y)]
   if all(c not in used for c in cells):return cells
  return None
 def step(self,direction=None):
  self.tick+=1
  if direction in DIRS and direction!=(-self.direction[0],-self.direction[1]):self.direction=direction
  for i in range(1,len(self.snakes)):
   if not self.alive[i] and self.tick>=self.respawn[i]:
    cells=self.respawn_cells()
    if cells:self.snakes[i]=cells;self.alive[i]=True
  heads=[]
  for i,snake in enumerate(self.snakes):
   if not self.alive[i]:heads.append(None);continue
   x,y=snake[0]
   if i==0:d=self.direction
   else:
    choices=[d for d in DIRS if self.wrap((x+d[0],y+d[1]))!=snake[1]]
    others={p for j,body in enumerate(self.snakes) if j!=i and self.alive[j] for p in body[:-1]}
    safe=[d for d in choices if self.wrap((x+d[0],y+d[1])) not in others];self.rng.shuffle(safe)
    d=min(safe or choices,key=lambda d:min((self.dist(self.wrap((x+d[0],y+d[1])),f) for f in self.food),default=0))
   heads.append(self.wrap((x+d[0],y+d[1])))
  grow=[h is not None and h in self.food for h in heads]
  dead=[]
  for i,p in enumerate(heads):
   if p is None:continue
   others={c for j,body in enumerate(self.snakes) if j!=i and self.alive[j] for c in (body if grow[j] else body[:-1])}
   if p in others or heads.count(p)>1:dead.append(i)
  for i in dead:
   self.alive[i]=False;self.food.update(self.snakes[i]);self.snakes[i]=[]
   if i>0:self.respawn[i]=self.tick+RESPAWN_TICKS
  for i,p in enumerate(heads):
   if not self.alive[i]:continue
   self.snakes[i].insert(0,p)
   if grow[i]:
    self.food.remove(p)
    if i==0:self.score+=1
   else:self.snakes[i].pop()
  self.refill();return not self.alive[0]
def loop(s):
 S=pi18n.load('snake-arena',DEFAULT_STRINGS) if pi18n else DEFAULT_STRINGS
 s.timeout(40);h,w=s.getmaxyx();g=Arena(max(32,w//2-2),max(18,h-6));last=time.monotonic();direction=None;paused=False;done=False
 while True:
  h,w=s.getmaxyx();key=s.getch();s.erase()
  if key in (27,ord('q')):return
  if key==ord('r'):g=Arena(max(32,w//2-2),max(18,h-6));done=False;paused=False
  if key==ord(' '):paused=not paused
  keys={curses.KEY_UP:(0,-1),curses.KEY_DOWN:(0,1),curses.KEY_LEFT:(-1,0),curses.KEY_RIGHT:(1,0),ord('w'):(0,-1),ord('s'):(0,1),ord('a'):(-1,0),ord('d'):(1,0)}
  if key in keys:direction=keys[key]
  fits=w>=g.w*2+2 and h>=g.h+5
  if fits and not paused and not done and time.monotonic()-last>.16:done=g.step(direction);direction=None;last=time.monotonic()
  put(s,0,1,S['HUD'].format(score=g.score,length=len(g.snakes[0]),rivals=sum(g.alive[1:])),curses.A_BOLD)
  if not fits:put(s,2,1,S['RESIZE'])
  else:
   left=(w-g.w*2)//2;top=2+(h-g.h-5)//2
   for y in range(g.h):put(s,top+y,left,'· '*g.w)
   for x,y in g.food:put(s,top+y,left+x*2,'◇')
   for i,snake in enumerate(g.snakes):
    for j,(x,y) in enumerate(snake):put(s,top+y,left+x*2,('P' if i==0 else str(i)) if j==0 else '█',curses.A_REVERSE if i==0 else 0)
   put(s,h-3,1,S['GAME_OVER'] if done else S['RULES'])
  put(s,h-1,1,S['CONTROLS']);s.refresh()
if __name__=='__main__':
 import sys
 if '--version' in sys.argv:print(VERSION)
 elif '--drift' in sys.argv:
  import drift
  raise SystemExit(run(drift.loop))
 else:raise SystemExit(run(loop))
