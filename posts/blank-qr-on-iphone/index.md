The QR generator on NoByte draws to a canvas and lets you download a PNG. I wanted that download to be crisp when someone prints it or drops it on a slide, so the export renders large, around a 4K longest side, rather than at the size you see on screen.

On my laptop it worked. The download was sharp. On a phone it came back as a blank square.

## What actually happened

Not an error. No exception, nothing in the console, a perfectly valid PNG of the right dimensions, and entirely blank. The on-screen preview, drawn to a smaller canvas, was fine on the same phone. Only the big export failed, and only on mobile Safari.

The size I was proud of was the problem. A 4K longest side on a square code is roughly 4096 by 4096, which is a shade under 17 million pixels. Mobile Safari refuses to keep a canvas backing store past about 16.7 million pixels, and it does not tell you. It hands back a canvas that reports the size you asked for and holds nothing. You draw into a void and export the void.

> The limit is on total area, width times height, not on either side on its own. I had been thinking about the longest side, which is exactly the number that does not matter here.

## The fix

Clamp the export by area, not by edge. Work out the pixel budget, and if the requested canvas is over it, scale both sides down by the square root of the ratio so the whole thing fits under the ceiling while keeping its shape.

```
maxArea = 16.7e6             // mobile Safari's canvas ceiling, near enough
area = w * h
if (area > maxArea) {
  scale = Math.sqrt(maxArea / area)
  w = Math.floor(w * scale)
  h = Math.floor(h * scale)
}
```

A square QR export now lands near 4080 a side instead of 4096, which nobody can see, and it renders. A very wide, barcode-shaped canvas is allowed to stay wide, because it is the area that has to fit, and the code finally checks the thing the browser is actually checking.

## The bit worth keeping

I lost an hour looking for a bug in the drawing code, because the drawing code was fine. The failure was a platform limit that reports success and returns nothing, which is the worst way for a limit to behave.

Since then, anything on NoByte that sizes a canvas from user input goes through the same area clamp, whether or not I think it will ever get near the ceiling. The one time it does, there is no error to catch, only a blank picture and a confused person.
