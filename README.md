# explain-labs-site

The landing page at **https://explain-labs.com** — one static HTML page, no framework,
no build step, no JavaScript.

## Layout

```
site/          everything that gets served (this is what deploy-app publishes)
tools/         image pipeline + the original full-size artwork; never shipped
```

## Editing

Edit `site/index.html` and `site/styles.css` directly, commit, push. The server picks it up
on the next deploy.

**Colour rule (there is a comment about this at the top of `styles.css`):** the brand blue
`#003399` (1.8:1 on the page background) and magenta `#CC0099` (3.8:1) are **fill-only**.
Anything small and textual uses `--blue-lit` / `--magenta-lit`.

## Regenerating images

Source artwork lives in `tools/source/`. Both scripts need Pillow with AVIF + WebP support
(Pillow ≥ 11) and run on macOS:

```sh
python3 tools/build-images.py   # site/img/{hero,modeling,monitor}-*.{avif,webp}
python3 tools/build-og.py       # site/img/og.png (1200×630 social card)
```

To swap a screenshot: drop the new PNG into `tools/source/` under the same name, re-run
`build-images.py`, commit both the source and the outputs.

The favicon set is derived from `site/favicon.svg`:

```sh
qlmanage -t -s 512 -o /tmp site/favicon.svg
python3 -c "
from PIL import Image
im = Image.open('/tmp/favicon.svg.png').convert('RGB')
im.save('site/icon-512.png', optimize=True)
im.resize((180,180), Image.LANCZOS).save('site/apple-touch-icon.png', optimize=True)
im.save('site/favicon.ico', sizes=[(16,16),(32,32),(48,48)])"
```

`favicon.svg` carries a dark `#0B0B0F` plate on purpose — the mark's outer ring is white and
would be invisible in a light-mode browser tab without it.

## Preview locally

```sh
python3 -m http.server 8000 --directory site
```

## Deployment

Hosted on the KVM 2 server as the `explain-labs-site` app (`TYPE=static`, no port, no
systemd unit). Caddy serves `/srv/apps/explain-labs-site/current` for `explain-labs.com`;
`www` 301-redirects to the apex.

```sh
ssh kvm2 'sudo deploy-app explain-labs-site'            # deploy main
ssh kvm2 'sudo deploy-app explain-labs-site --status'   # what is live
ssh kvm2 'sudo deploy-app explain-labs-site --rollback' # previous release
```

`deploy.conf` sets `PUBLISH="site/./"`, so only the contents of `site/` land in a release —
`tools/` and its multi-megabyte source PNGs never reach the web root.

## Artwork provenance

The logo, the hero photograph and the product screenshots are © Tim Antonius and are **not**
covered by the MIT licence — see `NOTICE.md`.

The neonatal resuscitation photographs in `Dobutamine/explain-monitor-web`
(`public/Images/*.jpg`) are deliberately **not** used here: they show real clinical staff in a
real hospital room and are not cleared for public marketing use.
