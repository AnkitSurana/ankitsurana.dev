# Deploying this to GitHub Pages

`index.html` is the whole site. No build step, no dependencies, nothing to install.
Posts and project write-ups are markdown files, each in its own folder with its own
images, fetched and rendered in the browser.

## One-time setup

The site is plain files. No build step, so GitHub Pages can serve the repo directly.

```bash
cd ~/Desktop/portfolio
git init -b main
git add -A
git commit -m "Portfolio site"
gh repo create ankitsurana.dev --public --source=. --push
```

Then **Settings → Pages → Source: Deploy from a branch → `main` / `(root)`**.

The repo name does not matter once a custom domain is attached, so name it after
the domain. A `CNAME` file is already committed with `ankitsurana.dev` in it, which
is what tells Pages the domain belongs to this repo.

## Pointing ankitsurana.dev at it

Two records at your DNS provider. The apex needs A records because a CNAME cannot
sit on a bare domain, and `www` gets a CNAME so both spellings work.

**Apex — four A records on `@`:**

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

Add the AAAA records too if your provider supports IPv6:

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

**www — one CNAME:**

```
www.ankitsurana.dev  CNAME  ankitsurana.github.io
```

Check GitHub's current Pages IPs before you paste those in. They change rarely, but
they do change, and a stale A record is a site that silently does not resolve.

Then in **Settings → Pages → Custom domain**, enter `ankitsurana.dev` and save. GitHub
verifies the DNS, issues a Let's Encrypt certificate, and the **Enforce HTTPS** box
becomes tickable. Tick it.

### .dev is HTTPS-only, which changes the order of operations

`.dev` is on the HSTS preload list built into every browser. There is no plain HTTP
fallback: until the certificate is issued the domain does not load at all, rather than
loading insecurely. So expect a window after the DNS propagates where the site is
genuinely unreachable while GitHub provisions the certificate. That is normal and
usually resolves within the hour. Do not go changing DNS records to fix it.

Verify with:

```bash
dig +short ankitsurana.dev            # should list the four GitHub IPs
curl -sI https://ankitsurana.dev | head -1   # expect HTTP/2 200
```

## Updating it

```bash
git add -A && git commit -m "what changed" && git push
```

Pages redeploys on push. Give it a minute.

## Adding a project

Same system as posts. A folder `projects/<slug>/` with `index.md` and its own assets,
plus an entry in `projects/projects.json`:

```json
{
  "slug": "my-project",
  "name": "My Project",
  "blurb": "One or two sentences, shown on the card and under the title.",
  "status": "Open source",
  "period": "2026",
  "stack": ["Python", "Postgres"],
  "repo": "https://github.com/AnkitSurana/my-project",
  "cover": "cover.svg"
}
```

Run `python3 tools/make-covers.py` afterwards to generate its artwork.

**Leave `repo` empty for private work.** The card then shows a `private source` badge
instead of `public repo`, and the write-up page shows "Source is private" where the
repo button would be. The write-up carries the project either way, so a private repo
is no longer a dead end.

## Search and tag filters

Both grids have a search box and tag chips above them. Search matches title, blurb
and tags; chips filter by tag (posts use `tags`, projects use `stack`) and stack, so
selecting two narrows to items carrying both. Pressing `/` anywhere jumps to the
nearest search box. The chip row shows the eight most common tags so it does not turn
into a wall as content grows.

## Mermaid diagrams

Mermaid is initialised with `theme: "base"` and an explicit `themeVariables` block
built from the same `--diagram-*` variables the hand-drawn diagrams use, so a flowchart
matches the rest of the page in both light and dark. Toggling the theme re-renders
them, because mermaid bakes its colours into the SVG at draw time.

Two practical notes when writing diagrams:

- **Keep decision labels short.** A `{diamond}` node has roughly half the usable width
  of a rectangle, so `{Global model-call ceiling}` spills where `{Global ceiling?}`
  fits. The renderer will not wrap it for you.
- `htmlLabels` is off, so mermaid measures and draws with the same SVG text. With HTML
  labels the two disagree and long words push outside the node.

## Diagrams and theme

Diagrams in a post are fetched and **inlined** rather than left as `<img>`. An `<img>`
SVG is its own document: it cannot see the page's CSS variables, so it would follow
the operating system's light/dark setting even when the reader has toggled the site
the other way. Inlining puts them under the page stylesheet, and they now read from
`--diagram-*` variables with literal fallbacks so they still look right opened on
their own.

Mermaid is initialised with `htmlLabels:false`. With HTML labels, mermaid measures
text one way and draws the node another, so long words push outside the box. SVG text
makes the measurement and the drawing agree.

## Your email address

The address never appears in the served HTML. It is assembled at runtime from parts,
so the usual harvesters find no `name@domain` string and no `mailto:` href. Every
email control is a button: clicking copies the address, shows it in a toast, and opens
your mail client. The copy step matters because a visitor with no mail client
configured otherwise clicks a `mailto:` link and nothing happens at all.

To change the address, edit the `MAIL` array near the top of the script.

## Comments and reactions

Wired to **giscus**, which keeps comments and reactions as GitHub Discussions on your
own repo. This is the honest way to get both on a static site: no backend to run, no
third-party database, and the data stays yours.

Turn it on in three steps:

1. Enable **Discussions** on the repo (Settings → General → Features).
2. Install the [giscus app](https://github.com/apps/giscus) for that repo.
3. Get your `repoId` and `categoryId` from [giscus.app](https://giscus.app) and paste
   them into the `GISCUS` block near the top of the `<script>` in `index.html`.

**On a custom domain you must set `repo` yourself.** The auto-detection reads the
hostname, which only works on a `*.github.io` address; `ankitsurana.dev` tells it
nothing. Set all three:

```js
repo:       "AnkitSurana/ankitsurana.dev",
repoId:     "…",      // from giscus.app
categoryId: "…",      // from giscus.app
```

Until you do, each post shows a short note saying it is wired but not switched on,
rather than pretending.

The thread key is `post/<slug>` or `project/<slug>`, so renaming a post's title does
not orphan its comments, but changing its **slug** does. Pick slugs you can live with.

**On likes specifically:** giscus reactions are the real thing, backed by GitHub. A
plain "like counter" would need a backend or a third-party service. A version stored
in `localStorage` would count only that one browser and reset when it is cleared,
which is a fake number, so it is not built in.

## Showing and hiding things

Every entry takes a `display` field:

```json
"display": "show"     // appears on the site
"display": "hide"     // pulled off the grids
```

A hidden item **stays reachable by its direct link**, so you can write a draft, share
the URL for feedback, and publish it by flipping one word. The page marks it as
unlisted so you never mistake a draft for something that is live. Leave the field out
entirely and it defaults to shown.

## How this holds together as it grows

You asked what stops the design falling apart at thirty posts. Four things, and none
of them need you to remember anything:

**The grid has no fixed column count.** `auto-fill` with a minimum column width means
items reflow on their own: four columns at 1440px, three at 1120, two at 900, one on a
phone. There is no featured tile to rebalance when you add a sixth project.

**Card text is clamped, not trusted.** Titles cut off at two lines and blurbs at
three, so one long entry cannot make its card taller than its neighbours and stagger
the row. Covers are a fixed 16:9 for the same reason.

**Long lists paginate.** Six items per page, with a numbered pager underneath
(`← 1 2 … 7 →`). The pager windows itself, so it stays the same width at two pages
or twenty, and it disappears when everything fits on one page. Change `PAGE_SIZE`
near the top of the script in `index.html` if you want more per page.

Field notes will show a pager as soon as there is a seventh post; with three there is
genuinely nothing to page through.

**A checker enforces the rest.** Run it before you push:

```bash
python3 tools/check.py
```

It verifies every manifest entry has its `index.md`, that covers and in-post images
actually exist, that slugs are unique and well formed, that dates parse, that
`display` is a value the site understands, and that every SVG is valid XML. It also
warns when a title or blurb runs past the length the cards were designed around, which
is the failure mode you would otherwise only notice by eye. It exits non-zero, so it
works in a git hook or CI.

## Previewing locally

Posts are loaded with `fetch`, and browsers block `fetch` on `file://` URLs. Opening
`index.html` by double-clicking will show the site but every post will error. Serve it:

```bash
cd ~/Desktop/portfolio
./serve.command          # or just double-click serve.command in Finder
```

It picks a free port, starts the server, and opens the browser. The page detects the
`file://` case and explains it on screen rather than showing an empty section, so you
will not be left guessing.

## Writing a post

Two steps.

**1. Make a folder in `posts/` named after the slug**, with the writing in `index.md`.
`posts/my-post/index.md` becomes `#post/my-post`.

Every post owns its folder, so its images are namespaced. Ten posts can each have a
`cover.svg` and a `diagram.png` without colliding, and deleting a post deletes its
assets with it.

```
posts/my-post/
  index.md        the writing
  cover.svg       card preview and header image
  diagram.png     anything the post references
```

**2. Add one entry to `posts/posts.json`.** This is the index the Writing section
reads. Newest first.

```json
{
  "slug": "my-post",
  "title": "The title, shown on the card and the post",
  "summary": "One sentence. Shown on the card and as the standfirst.",
  "date": "2026-08-01",
  "tags": ["Postgres", "Concurrency"],
  "cover": "cover.svg"
}
```

`cover` and `header` are **relative to the post folder**. Leave `cover` empty and the
card paints a generated mesh from the slug instead, so it is never a broken image.

**3. Generate the artwork.**

```bash
python3 tools/make-covers.py            # everything
python3 tools/make-covers.py my-post    # one item
```

That is the whole workflow. Title, tags and date come from the manifest, so fixing a
typo in a title or changing a date and re-running updates the art to match. There is
nothing to keep in sync by hand.

### The cover templates

Two files in `tools/` control how every piece of artwork looks:

| File | Size | Where it appears | Carries |
| --- | --- | --- | --- |
| `cover-template.svg` | 1200x675 | Card thumbnail on the grids | Artwork only |
| `header-template.svg` | 1600x460 | Full-bleed banner on a post or project | Artwork only |

**No text is baked into the artwork.** It used to be, and the title had to be stretched
with `textLength` to fit a fixed canvas, which visibly distorted the glyphs. Titles,
subtitles and dates are now real HTML sitting on top of the banner, so they resize with
the viewport, stay selectable, and are readable by search engines without a duplicate
hidden `<h1>`.

Edit either one and re-run `make-covers.py` to restyle **every** item at once. The
tokens (`{{HUE}}`, `{{TITLE_TSPANS}}`, `{{DATE}}` and so on) are documented in a
comment at the top of each template, and that comment is stripped from the output.

Colours come from a hash of the slug, so every item gets its own hue automatically
and the same slug always produces the same colours.

The banner is full-bleed, and the back control, breadcrumb, banner text and article
body all share one container width (`--docw`), so their left edges line up at every
screen size.

`make-covers.py` writes an `"art"` version stamp into each manifest entry, and the
page appends it as `?v=…` to every cover and banner. Regenerated artwork therefore
appears immediately, with no hard refresh and no cache confusion.

Reading time is counted from the markdown. You do not set it.

### What the markdown supports

| Syntax | Renders as |
| --- | --- |
| `# ` through `#### ` | Headings |
| `**bold**`, `*italic*`, `` `code` `` | Inline formatting |
| ` ```lang ` fenced blocks | Code blocks, horizontally scrollable |
| ` ```mermaid ` fenced blocks | Rendered diagrams |
| `> quote` | Pull quote |
| `- item` / `1. item` | Lists |
| `\| a \| b \|` with a `\|---\|` row | Tables |
| `![caption](path.png)` on its own line | Figure, with the alt text as the caption |
| `[text](url)` | Link, external ones open in a new tab |
| Raw HTML or inline `<svg>` | Passed through untouched |

Images use paths **relative to the markdown file**, exactly as in a README. Since each
post and project has its own folder, `![x](./diagram.png)` is all you need and the name
cannot clash with another post's `diagram.png`. An image that fails to load becomes a
labelled placeholder showing the path, rather than a silent broken icon.

The placeholder art shipped in each folder (`cover.svg`, `figure-1.svg`) is there to be
replaced. Both are 1200x675. If you hand-edit an SVG, keep any quotes or ampersands in
the text escaped, or the file stops being valid XML and silently fails to render.

Mermaid is only downloaded when a post actually contains a diagram, and it comes
from a CDN. If it fails to load, the diagram stays readable as its source text.
That is the one external dependency on the whole site.

### Nesting is not supported

The markdown renderer is deliberately small. Nested lists, footnotes, and reference-style
links are not handled. If you need them, the renderer is one function in `index.html`
called `markdown()`.

## What each file is for

| File | Why it is there |
| --- | --- |
| `index.html` | The site, and the markdown renderer. |
| `posts/posts.json` | The post index. Add an entry per post. |
| `posts/<slug>/index.md` | A post, with its images in the same folder. |
| `projects/projects.json` | The project index. |
| `projects/<slug>/index.md` | Project write-ups, so private repos still have a page. |
| `tools/cover-template.svg` | Card artwork template. Edit to restyle every cover. |
| `tools/header-template.svg` | Page header template. |
| `tools/make-covers.py` | Fills the templates from the manifests. |
| `tools/check.py` | Pre-push content check. |
| `serve.command` | Double-click to preview locally. |
| `404.html` | Styled not-found page. Pages picks it up automatically. |
| `.nojekyll` | Stops Pages running Jekyll. Without it, `_`-prefixed paths are silently dropped. |
| `robots.txt` | Lets crawlers index everything. |
| `assets/` | Site-wide images only: portrait, OG image. Post and project art lives with its folder. |

## Before you push

1. **Portrait.** Drop a 4:5 image at `assets/portrait.jpg`, then in the hero
   replace the placeholder span. The holographic foil sits on top of whatever image
   you put there:
   ```html
   <div class="portrait holo" data-holo>
     <img src="assets/portrait.jpg" alt="Ankit Surana">
     <span class="layer film"></span><span class="layer sheen"></span>
     <span class="layer glare"></span><span class="layer edge"></span>
   </div>
   ```
2. **Social preview image.** Add `assets/og.png` at 1200x630 and two lines to `<head>`:
   ```html
   <meta property="og:image" content="https://ankitsurana.dev/assets/og.png">
   <meta name="twitter:image" content="https://ankitsurana.dev/assets/og.png">
   ```
   Without it, links to your site unfurl as a bare text card.
3. **Check the About copy.** Written from your GitHub profile and README. The four
   items under **Now** are guesses. Correct them or delete the panel.
4. **Post dates.** The three posts are real drafts, but the dates are placeholders.
5. **Replace `figure-1.svg` as you go.** Each folder ships one as a stand-in for a real
   screenshot or diagram, so nothing is ever a broken image. The covers and headers are
   generated and can stay as they are.
6. **Project write-ups.** I drafted these from your repo descriptions. The Applyin one
   infers internals from your own post about the ledger race, so read it before it is
   public.
