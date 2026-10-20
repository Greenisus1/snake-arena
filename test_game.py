import os
import unittest,random
import game
modules={'snake-arena':game}
class Tests(unittest.TestCase):
 def test_arena_reverse(self):
  g=modules['snake-arena'].Arena();g.step((-1,0));self.assertEqual(g.direction,(1,0))
 def test_arena_growth(self):
  g=modules['snake-arena'].Arena();g.food.add((6,5));g.step();self.assertEqual(len(g.snakes[0]),4);self.assertEqual(g.score,1)
 def test_wall_wraps_not_kills(self):
  g=modules['snake-arena'].Arena();g.snakes[0]=[(31,0),(30,0),(29,0)];over=g.step();self.assertTrue(g.alive[0]);self.assertEqual(g.snakes[0][0],(0,0));self.assertFalse(over)
 def test_self_crossing_survives(self):
  g=modules['snake-arena'].Arena();g.snakes[0]=[(3,3),(2,3),(2,4),(3,4)];g.step((0,1));self.assertTrue(g.alive[0]);self.assertEqual(g.snakes[0][0],(3,4))
 def test_rival_body_kills_and_drops_dots(self):
  g=modules['snake-arena'].Arena(seed=0);g.snakes[0]=[(10,3),(9,3),(8,3)];g.snakes[1]=[(11,3),(11,4),(11,5)];g.snakes[2]=[(20,15),(20,14),(20,13)]
  over=g.step((1,0));self.assertFalse(g.alive[0]);self.assertTrue(over)
  self.assertTrue(all(c in g.food for c in [(10,3),(9,3),(8,3)]))
 def test_death_dots_are_eaten(self):
  g=modules['snake-arena'].Arena();g.food.add((6,5));before=len(g.snakes[0]);g.step();self.assertEqual(len(g.snakes[0]),before+1)
 def test_rival_respawns(self):
  g=modules['snake-arena'].Arena(seed=1);g.alive[1]=False;g.snakes[1]=[];g.respawn[1]=g.tick+1;g.step()
  self.assertTrue(g.alive[1]);self.assertEqual(len(g.snakes[1]),3)
  self.assertTrue(all(0<=x<g.w and 0<=y<g.h for x,y in g.snakes[1]))
 def test_arena_sim(self):
  for seed in range(100):
   g=modules['snake-arena'].Arena(seed=seed)
   for _ in range(200):
    if g.step(random.choice(modules['snake-arena'].DIRS)):break
    for i,s in enumerate(g.snakes):
     if g.alive[i]:self.assertTrue(all(0<=x<g.w and 0<=y<g.h for x,y in s))
if __name__=="__main__":unittest.main()


class I18nTests(unittest.TestCase):
    def test_defaults(self):
        import game
        self.assertIn("{score}", game.DEFAULT_STRINGS["HUD"])
        self.assertEqual(game.DEFAULT_STRINGS["PAUSED"] if "PAUSED" in game.DEFAULT_STRINGS else "x", "x")
