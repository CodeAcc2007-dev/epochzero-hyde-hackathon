# Private repository publication and sharing record

Date: **17 October 2026 (IST)**.

Status: **COMPLETE — private repository created, plans pushed, remote commit/tree and exclusions verified.**

## Authorized scope

Create a private GitHub repository containing the plans and four teammate folders. Keep environment/dependency trees, raw datasets, downloaded papers, credentials and sample-row previews local. Preserve dataset source links and provenance metadata in the repository. No SSH or teammate invitations are included; usernames were not supplied.

## Local preparation

- Initialize a separate Git repository at the project root on `main`. The organizer checkout remains untouched inside ignored `shared-local/`.
- Add a root README with team entry points, sources and environment reuse instructions, plus a research-resource access guide.
- Preserve the four original numbered plans/reports and every teammate's context, research brief and findings worksheet.
- Keep `.env`, `.env.*`, virtual environments, installed packages, `shared-local/`, `research/downloads/`, preview-row JSONs, private keys and local secret directories excluded by `.gitignore`.
- Stage an explicit reviewed file list; check the staged blobs for token/key signatures and the actual PAT before any commit/push.
- Use HTTPS authentication; never embed a PAT in a remote URL, Git config, committed file or command-line argument.

## PAT input

The user's local `.env` has `GITHUB_TOKEN` and `GITHUB_REPO_NAME`. Its mode is `0600`; Git ignores the file. Read it as data rather than sourcing shell code. Do not print its contents or include it in screenshots, reports or Git history.

A classic PAT needs the `repo` scope for private repository creation/access. Fine-grained tokens need repository-creation permission and contents write access covering the new repository; exact available permissions depend on the token/account configuration. See [GitHub repository creation documentation](https://docs.github.com/en/rest/repos/repos#create-a-repository-for-the-authenticated-user) and [PAT management](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). No token is reproduced here.

## Remote verification record

- Authenticated GitHub account: `CodeAcc2007-dev`.
- Repository: [epochzero-hyde-hackathon](https://github.com/CodeAcc2007-dev/epochzero-hyde-hackathon). The name was taken from the user's local configuration.
- Explicit private visibility on creation and authenticated reread: **verified private**.
- Pushed branch: `main`. Initial context commit: `a0fd90114015e4b8257d43b32b12b8c6fc3737a0`; this completion record is published in a follow-up documentation commit.
- Remote file tree matched against local committed paths: **verified, 37 files**. The authenticated GitHub commit/tree matched the local commit/tree.
- Environment/secret/raw-download exclusions in the remote tree: **verified**. No `.env`, environment/dependency directory, raw dataset, downloaded paper or sample-row preview is tracked.
- Staged-content checks: token/key/service-credential signature checks and a literal check for the actual PAT passed before publication. The token was not embedded in Git config, the HTTPS remote or subprocess arguments.
- Local `.env` remains ignored with mode `0600`. The temporary HTTPS authentication helper was removed after each push; no global Git credential store was changed.
- Teammate invitations: not sent; share access only with intended teammates after their usernames are known.

## Scope stop

Publication does not perform the assigned Phase 1 research or create bots. Existing context is shared as context, including explicit findings-pending status. Local setup logs and raw downloaded resources remain available on the original computer only.

## Sharing entry point

Send intended teammates the private [repository URL](https://github.com/CodeAcc2007-dev/epochzero-hyde-hackathon) after granting them access in GitHub repository settings. The root README links their individual briefs and the dataset sources. No environment or token needs to be sent to them.
