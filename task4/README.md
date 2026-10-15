# Simple Platformer (Pygame)

Run: `pip install pygame` then `python main.py`

Controls: Left/Right or A/D to move, Space/Up/W to jump.
On the Game Over screen: 1 = Easy, 2 = Medium, 3 = Hard, Q or Esc = exit.

## Task 1 - Collision
Cause: gravity had no cap and collision was only tested at the player's final
position each frame, so after a long fall one frame of movement could carry the
player from above a platform to below it with no overlap ever detected.
Fix (`game/player.py`): swept collision. Each frame the whole vertical path is
tested against every platform, landing on the highest top crossed (and bumping
heads on undersides when rising). Fall speed is also capped at 20 px/frame, and
a 6-frame jump buffer makes jumps pressed just before landing still fire.

## Task 2 - Game over
Falling off the bottom or touching the hazard shows a "GAME OVER" overlay with
the final score (goals reached) and waits for input - no console printing.

## Task 3 - Replay
Pick Easy / Medium / Hard (gravity and jump strength) or exit.

| Difficulty | Gravity | Jump strength |
|------------|---------|---------------|
| Easy       | 0.45    | -13           |
| Medium     | 0.60    | -12           |
| Hard       | 0.80    | -11           |

## Task 4 - Sound
`game/sound.py` synthesises jump, goal and death sounds in code (no audio
files). If no audio device exists the game runs silently.

## Level change
The hazard was narrowed from 100px to 60px (x=260). At 100px the platform it
sits on had no safe landing spot and the jump over it was out of reach.
