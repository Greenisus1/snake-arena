## Languages

Works with the Translations app: pick a language there and the HUD and help lines switch to it (English, Espanol, Francais, Deutsch). With no Translations app installed it runs in English as usual.

## Run
# snake-arena 1.1.0

Offline grid snake arena with two computer rivals. Walls wrap endlessly and your own body is harmless: only another snake (a rival body, or a head-on) can kill you. Dead snakes drop their whole body as edible food dots at the exact cells where they died. Rivals respawn so the arena never runs out. Not slither.io, not online.

Terminal-first fullscreen curses interface, no desktop, accounts, network, ads or saved personal data. Python3 with curses and an interactive Unicode-capable monospace terminal required. Game instructions are displayed on screen. Esc or q exits; terminal state restores through curses.wrapper. Narrow windows clip safely, gameplay pauses where space is too small; resize or restart to refit. No fallback pretending to play on noninteractive input.

    bash app-store.sh install
    bash app-store.sh run
    python3 game.py --version
    python3 -m unittest -v

Stdlib only. Install checks source; it does not run sudo or add packages. On Linux systems without Python3/curses, install the distribution's Python3 package first. No hardware/display requirement beyond terminal. Linux tests and real PTY previews checked; physical Raspberry Pi and non-Linux untested. Changelog: 1.1.0: wrap-around walls (no wall death), self-crossing harmless, death only from other snakes, death dots edible at their death cells, rivals respawn, game starts without prompting. 1.0.0: first release.

Root category marker: games. Trivia's Learning games category requires a supporting Store update; it must not fall silently into normal Games.

MIT license. Original code, no copied game assets. This is unrelated to the named commercial inspiration.
