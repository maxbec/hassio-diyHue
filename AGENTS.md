# Agent instructions

<!-- prettier-ignore-start -->
<!-- pipeline:start -->

## Pipeline

CI is `maxbec/pipeline`, called SHA-pinned from `.github/workflows/ci.yaml`. Flaiky renders that caller and this section
(`provisioning/migrate-repos.ts` in `maxbec/flaiky`); never edit either by hand. Behaviour is configured only in
`.github/pipeline.yaml`.

- Three jobs: `Guard` enforces the branch rules and a conventional PR title; `Check` runs secret scan, lint, test and
  build and is the single required status (`pipeline / Check`); `Deploy` runs only on a published GitHub release
  (prerelease to `preview`, stable to `production`). Pushes never deploy.
- Branch off `main` and target `main`; squash merge. There is no `dev` here.
- Conventional PR titles (`type(scope): summary`): the version is derived from them. Never edit a version, tag or
  changelog by hand; Flaiky keeps one Release PR per branch and merging it is the release.
- A pull request merges only when `pipeline / Check` is green, the head is signed and every review thread is resolved.
  Fix a red pipeline at the root; never weaken or skip a check.

<!-- pipeline:end -->
<!-- prettier-ignore-end -->