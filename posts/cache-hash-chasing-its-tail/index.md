Every asset on NoByte is served with a `?v=` stamp on the end, and the stamp is a hash of that file's own bytes. Change the file and the URL changes, so a browser cannot hand you yesterday's copy. Leave it alone and the stamp holds, so the browser keeps the copy it already has. That is how the CSS and JS can be cached for a year while a redeploy still shows up the moment it lands.

I wrote the stamping pass, watched a deploy pick up my changes, and moved on.

## What actually happened

A while later I edited a shared module, one that several tool files import. I deployed. The tool pages kept running the old version.

The hash on the shared file was correct. It had changed, its URL had changed, and the browser fetched the new bytes. The problem was one level up. A page does not link the shared module directly, it links a tool file that imports it. That tool file had not changed a single byte, so its hash had not moved, so its URL had not moved, so the browser served the tool file it already had. And that cached file still imported the old version of the shared module, by its old stamped URL.

> A content hash tells you a file's bytes changed. It does not tell you that something the file depends on changed, and a browser only re-fetches what the URL tells it to.

The stamp was doing exactly what it promised. I had just assumed one pass was enough, and one pass only ever looks at each file's own bytes.

## The fix

The hash of a file that imports other files has to depend on the hashes of those imports. Which is circular: you cannot know an importer's final hash until its imports are stamped, and you cannot stamp the importer until you know that hash.

So the build stops trying to do it in one shot. It stamps every reference, re-hashes everything, and repeats.

```
do
  stamp every reference with the current hash of its target
  recompute every hash
while some hash changed this pass    // capped, so a cycle cannot spin forever
```

Stamping the shared module changes its URL, which changes the bytes of the tool file that imports it, which changes that tool file's hash, which changes its URL. The next pass carries the change up to the page. Each round moves fewer files, and when a full pass changes nothing, the hashes have settled and the build stops.

It is a fixed-point iteration, which sounds grander than it is. The plain version: keep stamping until stamping stops changing anything. The cap is there because a genuine import cycle would otherwise loop forever, and I would rather the build fail loudly than hang.

## The bit worth keeping

The bug was invisible until a shared file changed and its importers did not. A tool that imports nothing was always fine, and most of them import nothing, which is exactly why it took a shared edit to surface it.

The lesson I took was not about hashing. It was that "this file changed" and "what this file depends on changed" are two different questions, and a cache built to answer the first will happily lie about the second.
