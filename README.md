# Keir Starmer's a Wanker

MP's calling for him to go.

## What is this?

A static GitHub Pages site that displays a live-updating list of Labour MPs publicly calling for Keir Starmer to resign as Prime Minister. Data is pulled from a public Google Sheet and enriched with constituency names and Parliament profile links via the official UK Parliament Members API.

## How it works

- **Data source**: [Google Sheet](https://docs.google.com/spreadsheets/d/1OBYlmRwHPlRa9Lsk6nTGlgX7Ixn1C3oX6v-f6ogZDEI) — add an MP's name to the sheet and it appears on the site automatically.
- **Parliament API**: Each MP name is searched against the [UK Parliament Members API](https://members-api.parliament.uk/) to retrieve their constituency and a link to their official profile. No API key required.
- **Hosting**: GitHub Pages — just push to `main` and the site updates.

## Development

### Prerequisites

- Node.js (for rebuilding Tailwind CSS)

### Setup

```bash
npm install -D tailwindcss@3
```

### Rebuilding Tailwind CSS

The site uses a locally-built `tailwind.css` (no CDN). After editing `index.html` and adding new Tailwind utility classes, regenerate it with:

```bash
echo "@tailwind base; @tailwind components; @tailwind utilities;" > input.css
npx tailwindcss -i input.css -o tailwind.css --content './index.html' --minify
```

### Files

| File | Purpose |
|------|---------|
| `index.html` | Main page — all logic is inline JS |
| `tailwind.css` | Minified Tailwind CSS built from `index.html` |
| `banner.png` | Social preview image (Open Graph / Twitter Card) |

### Updating the MP list

Edit the [Google Sheet](https://docs.google.com/spreadsheets/d/1OBYlmRwHPlRa9Lsk6nTGlgX7Ixn1C3oX6v-f6ogZDEI) — one MP name per row. The site fetches it live on every page load, no deploy needed.

bump
