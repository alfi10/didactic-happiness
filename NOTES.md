# Notes

Working notes for didactic-happiness.

Use this file to capture what you observe while playing, reviewing, or testing. Keep it lightweight. `Detectado` is for raw findings. `Estudiado` is for the AI-written task formulation that can feed a milestone in [ROADMAP.md](ROADMAP.md). When the work is actually done, move the historical result to [DONE.md](DONE.md).

## Detectado

- [ ] Example: UI text overflow on the combat result screen
  Brief detail: the label can wrap or clip when the window is narrow.

## Estudiado

- [ ] Example: combat result layout needs more vertical space
  Cause: the current placement competes with the score summary and buttons.
  Task: move the button stack down or compress the header block, then validate the result screen at narrow window sizes.
