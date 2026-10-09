#!/usr/bin/env python3
"""Offline rival-snake arena. Original grid game, not an online service."""
import curses,random,time
from ui import put,run
DIRS=((1,0),(-1,0),(0,1),(0,-1))
class Arena:
 def __init__(self,w=32,h=18,seed=0):
  self.w=w;self.h=h;self.rng=random.Random(seed);self.snakes=[[(5,5),(4,5),(3,5)],[(w-6,5),(w-5,5),(w-4,5)],[(w-6,h-6),(w-5,h-6),(w-4,h-6)]];self.direction=(1,0);self.alive=[True]*3;self.food=set();self.score=0;self.refill()
 def refill(self):
  used={p for s in self.snakes for p in s}|self.food;free=[(x,y) for x in range(self.w) for y in range(self.h) if (x,y) not in used];self.rng.shuffle(free);self.food.update(free[:max(0,18-len(self.food))])
 def step(self,direction=None):
  if direction in DIRS and direction!=(-self.direction[0],-self.direction[1]):self.direction=direction
  heads=[]
  for i,snake in enumerate(self.snakes):
   if not self.alive[i]:heads.append(None);continue
   x,y=snake[0]
   if i==0:d=self.direction
   else:
    choices=[d for d in DIRS if (x+d[0],y+d[1])!=snake[1]];self.rng.shuffle(choices)
    occupied={p for body in self.snakes for p in body[:-1]}
    safe=[d for d in choices if 0<=x+d[0]<self.w and 0<=y+d[1]<self.h and (x+d[0],y+d[1]) not in occupied]
    d=min(safe or choices,key=lambda d:min((abs(x+d[0]-fx)+abs(y+d[1]-fy) for fx,fy in self.food),default=0))
   heads.append((x+d[0],y+d[1]))
  occupied={p for i,body in enumerate(self.snakes) if self.alive[i] for p in (body if heads[i] in self.food else body[:-1])}
  dead=[]
  for i,p in enumerate(heads):
   if p is None:continue
   if not(0<=p[0]<self.w and 0<=p[1]<self.h) or p in occupied or heads.count(p)>1:dead.append(i)
  for i in dead:self.alive[i]=False;self.food.update(self.snakes[i]);self.snakes[i]=[]
  for i,p in enumerate(heads):
   if not self.alive[i]:continue
   grow=p in self.food;self.snakes[i].insert(0,p)
   if grow:
    self.food.remove(p)
    if i==0:self.score+=1
   else:self.snakes[i].pop()
  self.refill();return not self.alive[0] or not any(self.alive[1:])
def loop(s):
 s.timeout(40);h,w=s.getmaxyx();g=Arena(max(32,w//2-2),max(18,h-6));last=time.monotonic();direction=None;paused=True;done=False
 while True:
  h,w=s.getmaxyx();key=s.getch();s.erase()
  if key in (27,ord('q')):return
  if key==ord('r'):g=Arena(max(32,w//2-2),max(18,h-6));done=False;paused=True
  if key==ord(' '):paused=not paused
  keys={curses.KEY_UP:(0,-1),curses.KEY_DOWN:(0,1),curses.KEY_LEFT:(-1,0),curses.KEY_RIGHT:(1,0),ord('w'):(0,-1),ord('s'):(0,1),ord('a'):(-1,0),ord('d'):(1,0)}
  if key in keys:direction=keys[key];paused=False
  fits=w>=g.w*2+2 and h>=g.h+5
  if fits and not paused and not done and time.monotonic()-last>.16:done=g.step(direction);direction=None;last=time.monotonic()
  put(s,0,1,'SNAKE ARENA  food '+str(g.score)+' length '+str(len(g.snakes[0]))+' rivals '+str(sum(g.alive[1:])),curses.A_BOLD)
  if not fits:put(s,2,1,'Resize or R to refit (minimum66x23).' )
  else:
   left=(w-g.w*2)//2;top=2+(h-g.h-5)//2
   for y in range(g.h):put(s,top+y,left,'· '*g.w)
   for x,y in g.food:put(s,top+y,left+x*2,'◇')
   for i,snake in enumerate(g.snakes):
    for j,(x,y) in enumerate(snake):put(s,top+y,left+x*2,('P' if i==0 else str(i)) if j==0 else '█',curses.A_REVERSE if i==0 else 0)
   put(s,h-3,1,'YOU WIN! R restarts' if done and g.alive[0] else 'GAME OVER. R restarts' if done else 'Press arrow/Space to start.' if paused else 'You are P. Avoid walls and every snake body; rivals become food.')
  put(s,h-1,1,'Arrows/WASD turn | Space pause | R restart | Esc/q exit');s.refresh()
if __name__=='__main__':
 import sys
 if '--version' in sys.argv:print('1.0.0')
 else:raise SystemExit(run(loop))
