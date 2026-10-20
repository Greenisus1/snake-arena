import math
import unittest
import drift

class Tests(unittest.TestCase):
    def arena(self, seed=0, w=40, h=20, sterile=False):
        g = drift.DriftArena(w=w, h=h, seed=seed)
        if sterile:
            g.orbs = set()
            g.refill = lambda: None
        return g

    def test_turn_changes_heading(self):
        g = self.arena(); h0 = g.player.heading
        g.step(turn=1)
        self.assertAlmostEqual(g.player.heading, h0 + drift.TURN_STEP)
        g.step(turn=-1); g.step(turn=-1)
        self.assertAlmostEqual(g.player.heading, h0 - drift.TURN_STEP)

    def test_movement_follows_heading(self):
        g = self.arena(); g.player.heading = 0.0; x0 = g.player.x
        g.step()
        self.assertGreater(g.player.x, x0)

    def test_boost_is_faster(self):
        g = self.arena(); g.player.heading = 0.0
        x0 = g.player.x; g.step(boost=True); fast = g.player.x - x0
        g = self.arena(); g.player.heading = 0.0
        x0 = g.player.x; g.step(); slow = g.player.x - x0
        self.assertGreater(fast, slow)

    def test_boost_drains_length(self):
        g = self.arena(sterile=True); g.player.target = 30
        g.rivals = []
        t0 = g.player.target
        for _ in range(drift.BOOST_DRAIN_EVERY * 3):
            g.step(turn=1, boost=True)  # tight circle stays inside the border
        self.assertTrue(g.player.alive)
        self.assertLess(g.player.target, t0)
        self.assertGreaterEqual(g.player.target, drift.MIN_LENGTH)

    def test_orb_eating_grows_and_scores(self):
        g = self.arena(sterile=True); g.player.heading = 0.0
        nx = int(round(g.player.x)); ny = int(round(g.player.y))
        for dx in (1, 2, 3): g.orbs.add((nx + dx, ny))
        t0 = g.player.target; s0 = g.score
        for _ in range(8):
            if g.score > s0: break
            g.step()
        self.assertGreaterEqual(g.player.target, t0 + drift.ORB_GROWTH)
        self.assertGreater(g.score, s0)

    def test_border_kills_player(self):
        g = self.arena(w=20, h=20); g.player.x = g.w - 1.2; g.player.heading = 0.0
        done = g.step()
        self.assertTrue(done)
        self.assertFalse(g.player.alive)

    def test_self_trail_is_safe(self):
        g = self.arena()
        for _ in range(300): g.step(turn=1)
        # a tight circle crosses its own trail many times; player must survive self-contact
        self.assertTrue(g.player.alive)

    def test_cut_off_rival_bursts_into_orbs(self):
        g = self.arena()
        p = g.player
        p.cells.clear()
        for i in range(14): p.cells.append((10 + i % 2, 8 + i // 2))  # vertical-ish wall of cells
        p.x, p.y = 10.0, 8.0
        r = g.rivals[0]
        r.x, r.y, r.heading = 9.5, 12.0, 0.0  # heading straight into the player's body
        g.orbs.clear()
        g._steer_rival = lambda s: None  # hold it on the collision course
        orbs_before = len(g.orbs)
        g.step()
        self.assertFalse(r.alive)
        self.assertGreater(len(g.orbs), orbs_before)

    def test_dead_rival_respawns(self):
        g = self.arena()
        r = g.rivals[0]; r.alive = False; r.cells.clear()
        g.respawn[0] = g.tick + 2
        g.player.x, g.player.y = g.w/2, g.h/2  # keep center occupied check honest
        for _ in range(5): g.step(turn=1)
        self.assertTrue(g.rivals[0].alive)

    def test_length_tracks_target(self):
        g = self.arena(sterile=True)
        g.rivals = []
        g.player.target = 20
        for _ in range(40): g.step(turn=1)
        self.assertEqual(g.player.length, 20)

    def test_deterministic_with_seed(self):
        a = self.arena(seed=7); b = self.arena(seed=7)
        for _ in range(60):
            a.step(turn=1); b.step(turn=1)
        self.assertEqual(a.player.head_cell(), b.player.head_cell())
        self.assertEqual(a.orbs, b.orbs)

if __name__ == '__main__':
    unittest.main()
