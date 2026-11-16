# ankitsurana.dev

Source for my portfolio and field notes.

![HTML](https://img.shields.io/badge/HTML-E34F26?style=flat-square&logo=html5&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) ![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)

Hand-built, no framework and no build step. Project write-ups and field notes are markdown files rendered in the browser.

**Live at [ankitsurana.dev](https://ankitsurana.dev)**

## Structure

```
index.html        the whole site (HTML, CSS, JS)
projects/         one folder per project write-up: index.md + images
posts/            one folder per field note: index.md + images
tools/            cover generator and link checker
assets/           portrait and shared images
```

## Run locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000. Deployment is GitHub Pages from `main`; see [DEPLOY.md](DEPLOY.md).

---

## License

MIT. See [LICENSE](LICENSE).

## Author

**Ankit Surana** · Data & AI Engineer · [ankitsurana.dev](https://ankitsurana.dev) · [LinkedIn](https://www.linkedin.com/in/ankitsurana002/) · [GitHub](https://github.com/AnkitSurana)
