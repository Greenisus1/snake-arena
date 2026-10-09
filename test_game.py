import unittest,random,collections
import game
modules={'snake-arena':game}
class Tests(unittest.TestCase):
 def test_arena_reverse(self):
  g=modules['snake-arena'].Arena();g.step((-1,0));self.assertEqual(g.direction,(1,0))
 def test_arena_growth(self):
  g=modules['snake-arena'].Arena();g.food.add((6,5));g.step();self.assertEqual(len(g.snakes[0]),4);self.assertEqual(g.score,1)
 def test_arena_wall(self):
  g=modules['snake-arena'].Arena();g.snakes[0]=[(31,0),(30,0),(29,0)];self.assertTrue(g.step());self.assertFalse(g.alive[0])
 def test_arena_sim(self):
  for seed in range(100):
   g=modules['snake-arena'].Arena(seed=seed)
   for _ in range(200):
    if g.step(random.choice(modules['snake-arena'].DIRS)):break
    for i,s in enumerate(g.snakes):
     if g.alive[i]:self.assertTrue(all(0<=x<g.w and 0<=y<g.h for x,y in s))
if __name__=="__main__":unittest.main()
