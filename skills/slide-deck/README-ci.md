# Deck repos: build and release in CI

A deck repo holds only its content: `slides.md`, `figures/`, and optionally `canvas/` with its Excalidraw file and diagram code. The tooling comes from this repo as a git submodule at `slidegen/`. CI builds the HTML and PDF on every push and pull request, uploads both as workflow artifacts, and refreshes a `latest` release on pushes to `main`.

`examples/demo-deck` in this repo uses the same build script and release step. Its workflow is `.github/workflows/example-deck.yml`.

## Set up a deck repo

Run these from the deck repo's root. Replace `OWNER/DECK` with the deck repo.

1. Add the tooling as a submodule:

   ```sh
   git submodule add git@github.com:dbanks12/claude-authoring-tools.git slidegen
   ```

2. Copy the workflow:

   ```sh
   mkdir -p .github/workflows
   cp slidegen/skills/slide-deck/ci/deck.yml .github/workflows/deck.yml
   ```

3. Ignore the build outputs. CI produces them:

   ```sh
   printf '*.html\n*.pdf\n__pycache__/\n' >> .gitignore
   ```

4. Give CI read access to this private repo. The default `GITHUB_TOKEN` cannot read another private repo, so use a read-only deploy key:

   ```sh
   ssh-keygen -t ed25519 -N "" -C "DECK CI" -f /tmp/slidegen_key
   gh repo deploy-key add /tmp/slidegen_key.pub -R dbanks12/claude-authoring-tools --title "DECK CI (read-only)"
   gh secret set SLIDEGEN_DEPLOY_KEY -R OWNER/DECK < /tmp/slidegen_key
   rm /tmp/slidegen_key /tmp/slidegen_key.pub
   ```

   Deploy keys are read-only unless created with `--allow-write`. Use one key per deck repo, so you can revoke each one separately.

5. Commit and push to `main`. The Actions tab shows the build. The `latest` release holds `<name>.html` and `<name>.pdf`, where `<name>` is the repo directory name.

## Work locally

```sh
python3 slidegen/skills/slide-deck/assets/watch.py .     # rebuild HTML and PDF on every save
slidegen/skills/slide-deck/assets/ci-build.sh .          # one build, exactly as CI runs it
```

The output name is the deck directory's name. Keep the local clone's directory name equal to the repo name, so local and CI files match.

## Update the tooling in a deck

```sh
git -C slidegen pull origin master
git add slidegen && git commit -m "Update slidegen"
```

A deck pins one tool commit, so old decks keep building the same way until you update them.

## Requirements

- Python 3 with Pillow. `ci-build.sh` installs Pillow when it is missing.
- Chromium or Google Chrome for `pdf.py`. GitHub's `ubuntu-latest` runners include Chrome.
- The Liberation fonts on Linux stand in for Arial. The workflow installs them.
