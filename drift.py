#!/usr/bin/env python3
"""Drift mode: free-direction orb arena with rival snakes. Original game, not based on any existing brand."""
import curses,math,random,time
from collections import deque

try:
    import pi18n
except ImportError:
    pi18n = None

# English UI strings; the Translations app owns every language via ~/pi-translations.
DEFAULT_STRINGS = {
 'DRIFT_HUD': 'DRIFT  orbs {score}  length {length}  rivals {rivals}{boost}',
 'DRIFT_BOOST_ON': '  BOOST',
 'DRIFT_OVER': 'WRECKED. R restarts',
 'DRIFT_RULES': 'The border bites. Your own trail is safe. Cut rivals off and eat what spills.',
 'DRIFT_CONTROLS': 'Left/Right or A/D steer | hold Space to boost | P pause | R restart | Esc/q exit',
 'DRIFT_PAUSED': 'Paused',
 'DRIFT_RESIZE': 'Resize or R to refit (minimum 66x23).',
}
TURN_STEP = math.radians(16)
BASE_SPEED = 0.45
BOOST_SPEED = 0.9
SUBSTEP = 0.3
BOOST_DRAIN_EVERY = 16
MIN_LENGTH = 6
ORB_COUNT = 24
ORB_MAX = 60
ORB_GROWTH = 3
START_LENGTH = 12
RIVALS = 3
RIVAL_RESPAWN_TICKS = 90

def make_body(x, y, heading, length, w=10**6, h=10**6):
    cells = deque()
    for i in range(length):
        c = (min(max(int(round(x - math.cos(heading)*i)), 1), w-2), min(max(int(round(y - math.sin(heading)*i)), 1), h-2))
        if not cells or c != cells[-1]: cells.append(c)
    return cells

class DriftSnake:
    def __init__(self, x, y, heading, length):
        self.x = x; self.y = y; self.heading = heading
        self.cells = make_body(x, y, heading, length)
        self.target = length
        self.alive = True
        self.boosting = False
        self.cruise = BASE_SPEED
    def head_cell(self): return self.cells[0]
    @property
    def length(self): return len(self.cells)
    def advance(self):
        speed = BOOST_SPEED if self.boosting else self.cruise
        remaining = speed
        while remaining > 0:
            step = min(SUBSTEP, remaining); remaining -= step
            self.x += math.cos(self.heading)*step; self.y += math.sin(self.heading)*step
            c = (int(round(self.x)), int(round(self.y)))
            if c != self.cells[0]: self.cells.appendleft(c)
        while len(self.cells) > self.target: self.cells.pop()

class DriftArena:
    def __init__(self, w=40, h=20, seed=0):
        self.w = w; self.h = h; self.rng = random.Random(seed)
        self.tick = 0; self.score = 0
        self.player = DriftSnake(self.w/2, self.h/2, 0.0, START_LENGTH)
        self.rivals = []
        for i in range(RIVALS):
            a = 2*math.pi*i/RIVALS
            r = DriftSnake(self.w/2 + math.cos(a)*self.w/4, self.h/2 + math.sin(a)*self.h/4, a + math.pi, START_LENGTH)
            r.cells = make_body(r.x, r.y, r.heading, START_LENGTH, self.w, self.h)
            r.cruise = BASE_SPEED*0.85
            self.rivals.append(r)
        self.respawn = [0]*RIVALS
        self.orbs = set()
        self.refill()
    def free_cell(self, taken):
        for _ in range(80):
            c = (self.rng.randrange(1, self.w-1), self.rng.randrange(1, self.h-1))
            if c not in taken: return c
        return None
    def refill(self):
        taken = set(self.orbs)
        for s in [self.player] + self.rivals: taken.update(s.cells)
        while len(self.orbs) < ORB_COUNT:
            c = self.free_cell(taken)
            if c is None: break
            self.orbs.add(c); taken.add(c)
    def _steer_rival(self, s):
        s.heading += self.rng.uniform(-0.08, 0.08)
        if self.orbs:
            tx, ty = min(self.orbs, key=lambda o: (o[0]-s.x)**2 + (o[1]-s.y)**2)
            diff = (math.atan2(ty-s.y, tx-s.x) - s.heading + math.pi) % (2*math.pi) - math.pi
            s.heading += max(-0.12, min(0.12, diff))
        margin = 5; cx = cy = 0.0
        if s.x < margin: cx += 1
        if s.x > self.w-1-margin: cx -= 1
        if s.y < margin: cy += 1
        if s.y > self.h-1-margin: cy -= 1
        ac = (int(round(s.x + math.cos(s.heading)*2.2)), int(round(s.y + math.sin(s.heading)*2.2)))
        others = {c for o in [self.player] + self.rivals if o.alive and o is not s for c in list(o.cells)[2:]}
        if ac in others: cx += -math.cos(s.heading); cy += -math.sin(s.heading)
        if cx or cy:
            diff = (math.atan2(cy, cx) - s.heading + math.pi) % (2*math.pi) - math.pi
            s.heading += max(-0.3, min(0.3, diff))
    def _burst(self, s):
        if len(self.orbs) >= ORB_MAX: s.cells.clear(); s.target = START_LENGTH; return
        for c in list(s.cells)[::2]:
            if 0 < c[0] < self.w-1 and 0 < c[1] < self.h-1: self.orbs.add(c)
        s.cells.clear(); s.target = START_LENGTH
    def step(self, turn=0, boost=False):
        self.tick += 1
        p = self.player
        if p.alive:
            p.heading += turn*TURN_STEP
            p.boosting = boost and p.length > MIN_LENGTH
            if p.boosting and self.tick % BOOST_DRAIN_EVERY == 0:
                p.target = max(MIN_LENGTH, p.target-1)
        for i, r in enumerate(self.rivals):
            if not r.alive and self.tick >= self.respawn[i]:
                occupied = {c for o in [p] + self.rivals if o.alive for c in o.cells}
                for _ in range(8):
                    a = self.rng.uniform(0, 2*math.pi)
                    rx = self.w/2 + math.cos(a)*self.w/4; ry = self.h/2 + math.sin(a)*self.h/4
                    body = make_body(rx, ry, a + math.pi, r.target, self.w, self.h)
                    if not (set(body) & occupied):
                        r.x, r.y, r.heading, r.cells, r.alive = rx, ry, a + math.pi, body, True
                        break
                else:
                    self.respawn[i] = self.tick + 20
        for r in self.rivals:
            if r.alive: self._steer_rival(r)
        for s in [p] + self.rivals:
            if s.alive: s.advance()
        for s in [p] + self.rivals:
            if not s.alive: continue
            c = s.head_cell()
            if c in self.orbs:
                self.orbs.discard(c); s.target += ORB_GROWTH
                if s is p: self.score += 1
        for s in [p] + self.rivals:
            if not s.alive: continue
            if not (0 < s.x < self.w-1 and 0 < s.y < self.h-1):
                s.alive = False
                if s is not p: self._burst(s)
        bodies = {id(o): set(list(o.cells)[3:]) for o in [p] + self.rivals if o.alive}
        for s in [p] + self.rivals:
            if not s.alive: continue
            c = s.head_cell()
            for o in [p] + self.rivals:
                if o is s or not o.alive: continue
                if c in bodies.get(id(o), ()):
                    s.alive = False
                    if s is not p: self._burst(s)
                    break
        self.refill()
        return not p.alive

def loop(s):
    from ui import put
    S = pi18n.load('snake-arena', DEFAULT_STRINGS) if pi18n else DEFAULT_STRINGS
    s.timeout(30); h, w = s.getmaxyx()
    g = DriftArena(max(30, w//2-4), max(16, h-7))
    last = time.monotonic(); turn = 0; boost = False; last_boost = 0.0; paused = False; done = False
    while True:
        h, w = s.getmaxyx(); key = s.getch(); s.erase()
        if key in (27, ord('q')): return
        if key == ord('r'): g = DriftArena(max(30, w//2-4), max(16, h-7)); done = False; paused = False
        if key == ord('p'): paused = not paused
        if key in (curses.KEY_LEFT, ord('a')): turn = -1
        elif key in (curses.KEY_RIGHT, ord('d')): turn = 1
        if key == ord(' '): last_boost = time.monotonic()
        boost = time.monotonic() - last_boost < 0.18
        fits = w >= g.w*2+4 and h >= g.h+6
        if fits and not paused and not done and time.monotonic()-last > 0.07:
            done = g.step(turn, boost); turn = 0; last = time.monotonic()
        boost_tag = S['DRIFT_BOOST_ON'] if g.player.boosting and not done else ''
        put(s, 0, 1, S['DRIFT_HUD'].format(score=g.score, length=g.player.length, rivals=sum(r.alive for r in g.rivals), boost=boost_tag), curses.A_BOLD)
        if not fits: put(s, 2, 1, S['DRIFT_RESIZE'])
        else:
            left = (w - g.w*2)//2; top = 2 + (h - g.h - 5)//2
            for x in range(-2, g.w*2+2, 2): put(s, top-1, left+x, '#'); put(s, top+g.h, left+x, '#')
            for y in range(g.h): put(s, top+y, left-2, '#'); put(s, top+y, left+g.w*2, '#')
            for x, y in g.orbs: put(s, top+y, left+x*2, '*', curses.A_BOLD)
            for i, r in enumerate(g.rivals):
                if not r.alive: continue
                for j, (x, y) in enumerate(r.cells): put(s, top+y, left+x*2, str(i+1) if j == 0 else '~')
            if g.player.alive:
                for j, (x, y) in enumerate(g.player.cells): put(s, top+y, left+x*2, 'O' if j == 0 else '@', curses.A_REVERSE if j == 0 else 0)
            msg = S['DRIFT_OVER'] if done else (S['DRIFT_PAUSED'] if paused else S['DRIFT_RULES'])
            put(s, h-3, 1, msg)
        put(s, h-1, 1, S['DRIFT_CONTROLS']); s.refresh()
