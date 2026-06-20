# Pelican Bike Enhancements

## Pelican Design (less compact, more bird-like)
- [x] **Larger body** – increase `self.width`/`self.height` so the pelican isn't a tiny blob
- [x] **Long neck** – draw an S-curve neck connecting head to body
- [x] **Realistic orange beak** – upper and lower mandible (two triangles instead of one)
- [x] **Pronounced wings** – darker grey/black wing shapes on the side of the body
- [x] **Tail feathers** – add a small fan of tail feathers at the back
- [x] **Eye position** – adjust eye to be on the head, not the body

## Pedaling Animation (feet move when riding)
- [x] **`pedal_phase`** – a float that increments while `on_ground`
- [x] **Left leg** – position = `sin(pedal_phase)`, sweeps from extended to retracted
- [x] **Right leg** – position = `cos(pedal_phase)`, opposite phase
- [x] **Connect legs to pedals** – draw lines from pelican body to pedal positions on the crank

## Sequential Wheel Jump (front tire first, front lands first)
- [x] **Separate wheel y-offsets** – `wheel_front_offset`, `wheel_back_offset` (0 = on ground, negative = up)
- [x] **On jump:** front offset starts rising immediately; back offset waits ~8 frames then starts rising
- [x] **On ascent:** front wheel leads, back wheel catches up by apex
- [x] **On descent:** front wheel touches ground first (offset reaches 0); back wheel follows ~8 frames later
- [x] **Body tilt** – slightly rotate the pelican based on the difference between front/back wheel heights
- [x] **Ground detection** – both wheels must be at offset ≥ 0 before `on_ground = True`
