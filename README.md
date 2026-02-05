# Bioinformatics-tool

Biotechnology assistant with Python + R backend.

## Features
- Postdoc-level biotech responses with common wet-lab and computational tooling context.
- Built-in sequence tasks (GC content, reverse complement, translation).
- R-backed GC content calculation with Python fallback.

## Run locally
```bash
python app.py
```

Open `http://localhost:8000` in your browser.

## Preview on GitHub Pages
You can publish the static preview in the `docs/` folder with GitHub Pages:
1. Push this repository to GitHub.
2. In the GitHub repo, go to **Settings → Pages**.
3. Under **Build and deployment**, select **Deploy from a branch**.
4. Choose the `main` branch and `/docs` folder, then save.

This preview is static (no backend). For real responses and sequence tasks,
run the local server as described above.

## Notes
- The server uses only Python standard library modules, so no pip install is
  required to start the web app.
- The R backend is optional. If `Rscript` is unavailable, the app automatically
  falls back to Python.
