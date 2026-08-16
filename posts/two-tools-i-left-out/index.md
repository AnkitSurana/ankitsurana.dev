NoByte has 63 tools. It nearly had 65. I built two of them in my head, worked out what they would actually do, and dropped them before writing a line. Those two decisions shaped the site more than most of the ones I kept.

## The speed test

An internet speed test is one of the most searched tools there is. It would have been the most visited page on the site by a wide margin. So I sat down to build one, and stopped.

A browser cannot honestly measure a fast connection. To read a gigabit line you have to pour gigabits through it, from a server near enough that the network is the limit rather than the distance, for long enough to get past the slow start, on a machine that is not busy doing something else. A tab on a shared host has none of that. It would produce a number, the number would be confidently wrong, and it would be wrong in the direction that makes a slow result look like your fault instead of the test's. A tool that returns a wrong number with a straight face is worse than no tool.

## The currency converter

Same shape, different cause. A live currency converter needs live rates, and the free rate feeds update once a day. So the "live" figure is yesterday's, presented as now. For a traveller checking whether a price is roughly fair, close enough. For anyone who trusts it with a real amount it is a quiet lie, and I would have had no honest way to mark which reading was fresh and which was a day stale, because the feed does not really tell me.

> The test for whether a tool ships was never "can I build it". Both of these I could build in an afternoon. It was "can it tell the truth", and neither could.

## The bit worth keeping

Leaving things out is not the interesting part. Anyone can keep a short list. The interesting part was that the two tools most worth cutting were the two that would have brought the most people, and the pull to ship them anyway, dressed up with a disclaimer nobody reads, was real.

The rule that held the line was cheap to state. If a tool cannot be honest inside a browser, it does not go on a site whose whole promise is that it does the real thing, locally, without lying to you. The two tools that reach the network at all, the DNS lookup and the dictionary, say so on their own pages for the same reason.
