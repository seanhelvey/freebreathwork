# freebreathwork.org

Simple mobile-first static site for free community breathwork events in Arcata, CA.

## Development

- Push directly to `main` — no feature branches needed
- GitHub Actions deploys automatically on every push to `main`
- No build step; plain HTML/CSS/JS

## Updating the event schedule

Open `index.html` and edit the `SCHEDULE` config near the top of the `<script>` tag.
Each entry is `{ date: "Month D, YYYY", cancelled: false }`.
To mark a weekend you're out of town set `cancelled: true` and add an optional `note`.
