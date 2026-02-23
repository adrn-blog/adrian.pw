The source code for [adrian.pw](https://adrian.pw).

To trigger a new build, go to [the Actions page](https://github.com/adrn-blog/adrian.pw/actions/workflows/build.yml) and use the workflow dispatch.

## Architecture overview

The site is built with [Hugo](https://gohugo.io/) using the
[gioia](https://github.com/adrn-blog/hugo-gioia) theme (included as a git submodule).
Static pages (about, research, visualizations) live in `content/` and are written as
plain Markdown. Blog posts are Jupyter notebooks that live in separate repositories
under the [`adrn-blog`](https://github.com/adrn-blog) GitHub organization, each named
`post--<slug>`.

The publishing pipeline works in three stages:

1. Post repos: Each `adrn-blog/post--<slug>` repo contains a `post.ipynb` notebook, a
   `metadata.yml` with Hugo front-matter fields, and dependency information. Older posts
   (pre-2024) use `requirements.txt`; new posts created from the template use
   `pyproject.toml` with [uv](https://docs.astral.sh/uv/). A GitHub Actions workflow in
   each repo calls the shared
   [execute-post](https://github.com/adrn-blog/execute-post) composite action, which
   uses `uv sync` to install dependencies.
2. Notebook execution: The `execute-post` action installs dependencies, runs pre-commit,
   executes the notebook with `jupyter nbconvert --execute`, and force-pushes the
   fully-executed notebook to the repo's `executed` branch.
3. Site build: The build workflow in *this* repo (`adrian.pw`) runs
   `scripts/render-notebooks.py`, which queries the GitHub API for every `adrn-blog`
   repo whose name starts with `post--`, clones each repo's `executed` branch, converts
   the notebook to Markdown (with a custom nbconvert template), writes the result to
   `content/blog/`, and copies images to `static/blog/`. Hugo then builds the full site
   and deploys it to `adrn.github.io` (served at `adrian.pw`).

## How to create and publish a new blog post

### Prerequisites

- Python 3.12+
- [copier](https://copier.readthedocs.io) (`pipx install copier`)
- [uv](https://docs.astral.sh/uv/)
- Git + SSH access to the `adrn-blog` GitHub organization

### Steps

1. **Scaffold the post** using the
   [template](https://github.com/adrn-blog/template) repo:
   ```bash
   copier copy gh:adrn-blog/template post--<slug>
   cd post--<slug>
   ```
   You will be prompted for the title, date, slug, and Python version.

2. **Initialize the repo and install dependencies:**
   ```bash
   uv venv
   uv sync
   git init .
   uv run pre-commit install
   git add .
   git commit -m "Initial commit"
   ```

3. **Create a matching empty repo on GitHub** at
   https://github.com/organizations/adrn-blog/repositories/new (name it `post--<slug>`,
   don't check any boxes), then push:
   ```bash
   git remote add origin git@github.com:adrn-blog/post--<slug>.git
   git branch -M main
   git push -u origin main
   ```

4. **Write the post.** Edit `post.ipynb` locally. To add Python dependencies, add them
   to `pyproject.toml` under `[project] dependencies` and run `uv sync`.

5. **Push to `main`.** The post repo's GitHub Actions workflow will automatically
   execute the notebook and push the result to the `executed` branch. Check the
   [Actions tab](https://github.com/adrn-blog) on the post repo to confirm it succeeded.

6. **Trigger a site build.** Go to the
   [adrian.pw Actions page](https://github.com/adrn-blog/adrian.pw/actions/workflows/build.yml)
   and click **Run workflow** (workflow dispatch). The build will pick up all posts
   (including the new one) and deploy the updated site.

## How to add a text-only blog post (no notebook)

If your post is plain prose with no executable code, you can skip the post-repo pipeline
and commit a Markdown file directly to this repo.

1. **Create the file** at `content/blog/<slug>.md` with Hugo front matter:
   ```markdown
   ---
   title: "My Post Title"
   date: 2026-02-23
   slug: "my-post-slug"
   math: false
   ---

   Your post content goes here.
   ```

2. **Preview locally** (optional):
   ```bash
   hugo server -D
   ```

3. **Push to `main`** (or open a PR). The site build will pick it up automatically — no
   workflow dispatch needed.

## How to deploy text or style changes (no new blog posts)

If you are only changing static pages, the Hugo config, theme styles, or layouts — and
**not** adding or updating a blog post — you don't need to touch any post repos.

1. **Make your changes** in this repo. Common files to edit:
   - `content/about.md`, `content/research.md`, `content/viz.md` — static pages
   - `config.toml` — site title, menus, social links, footer, etc.
   - `themes/gioia/` — theme templates and stylesheets (or push changes to the
     [hugo-gioia](https://github.com/adrn-blog/hugo-gioia) repo and update the
     submodule)
   - `static/` — images and other static assets

2. **Test locally** (optional but recommended):
   ```bash
   hugo server -D
   ```
   Then open http://localhost:1313 to preview.

3. **Push to `main`** (or open a PR). The build workflow runs automatically on push and
   will deploy the updated site. For PRs, a preview deploy goes to GitHub Pages so you
   can check the result before merging.

## Blog posts

- [![Build post](https://github.com/adrn-blog/post--fisher-information-toy/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--fisher-information-toy/actions/workflows/build.yml) - fisher-information-toy
- [![Build post](https://github.com/adrn-blog/post--hierarchical-models-2/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--hierarchical-models-2/actions/workflows/build.yml) - hierarchical-models-2
- [![Build post](https://github.com/adrn-blog/post--hierarchical-models-1/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--hierarchical-models-1/actions/workflows/build.yml) - hierarchical-models-1
- [![Build post](https://github.com/adrn-blog/post--probabilistic-graphical-models/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--probabilistic-graphical-models/actions/workflows/build.yml) - probabilistic-graphical-models
- [![Build post](https://github.com/adrn-blog/post--flexible-density-model-jax/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--flexible-density-model-jax/actions/workflows/build.yml) - flexible-density-model-jax
- [![Build post](https://github.com/adrn-blog/post--matplotlib-rasterize/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--matplotlib-rasterize/actions/workflows/build.yml) - matplotlib-rasterize
- [![Build post](https://github.com/adrn-blog/post--nyc-weather/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--nyc-weather/actions/workflows/build.yml) - nyc-weather
- [![Build post](https://github.com/adrn-blog/post--fitting-a-line/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--fitting-a-line/actions/workflows/build.yml) - fitting-a-line
- [![Build post](https://github.com/adrn-blog/post--python-literature/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--python-literature/actions/workflows/build.yml) - python-literature
- [![Build post](https://github.com/adrn-blog/post--sunset-local-time/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--sunset-local-time/actions/workflows/build.yml) - sunset-local-time
- [![Build post](https://github.com/adrn-blog/post--astropy-eclipse/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--astropy-eclipse/actions/workflows/build.yml) - astropy-eclipse
- [![Build post](https://github.com/adrn-blog/post--yearly-sun-graph/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--yearly-sun-graph/actions/workflows/build.yml) - yearly-sun-graph
- [![Build post](https://github.com/adrn-blog/post--matplotlib-transparent-animation/actions/workflows/build.yml/badge.svg)](https://github.com/adrn-blog/post--matplotlib-transparent-animation/actions/workflows/build.yml) - matplotlib-transparent-animation
