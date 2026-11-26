# Review Dots

### Point to what matters.

Collect precise feedback on images, resolve comments, and keep a portable review record. A focused, self-hosted alternative to MarkUp.io for PNG and JPEG reviews.

[![CI](https://github.com/anshuman-pandey/review-dots/actions/workflows/check.yml/badge.svg)](https://github.com/anshuman-pandey/review-dots/actions/workflows/check.yml) · [MIT license](LICENSE) · Python + SQLite · Self-hosted

![Review Dots: actual application workspace](docs/assets/workspace.png)

**Public source preview.** The local workflow and container recovery have been tested. There is no hosted demo or tagged product release yet; public HTTPS acceptance remains pending.

## How it works

1. Upload a PNG or JPEG and share a private reviewer key.
2. Reviewers place numbered pins by clicking the image or entering coordinates.
3. Resolve or reopen comments, then export the image and JSON review history.

## Try it locally

Requires Git, Python 3 and Docker with the Compose plugin.

```sh
git clone https://github.com/anshuman-pandey/review-dots.git
cd review-dots
python3 scripts/setup.py
docker compose up --build -d
```

Open **http://127.0.0.1:8092**. Read the generated private `.env` file locally and use its `REVIEW_OWNER_KEY` value to unlock the owner workspace. Setup retains any existing `.env`; do not commit or share this file.

The app binds to localhost and stores data in a persistent Docker volume. Links pointing to localhost work only on your computer. For remote sharing, follow the [HTTPS deployment and backup guide](docs/DEPLOYMENT.md). Avoid `docker compose down -v` unless you intend to delete the stored data.

## Included

- Owner controls for board creation, review resolution and reviewer-key rotation.
- Keyboard-accessible pin coordinates and layouts for desktop and mobile.
- Images normalized to PNG with metadata removed.

**Interface languages:** English, German, Spanish, Japanese, Simplified Chinese and Traditional Chinese. Native-speaker review is still pending. User-authored content is never translated.

## Know the boundaries

Images are limited to 10 MiB and 16 megapixels; each board allows 1,000 comments. There is no total storage quota. Reviewer names are self-reported. Anyone with a board key can view its image, read/export comments and add feedback. Only the owner can resolve comments or rotate access. No PDF, video, website annotation, email or threaded discussions.

Private links and reviewer keys grant access to whoever holds them. Keep the owner key separate from participant credentials. This project covers the workflow above, not the full feature set of its commercial reference.

## Development and checks

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The published baseline passed **16 Python tests**. Recorded browser acceptance covers: image upload, pin placement, resolution/reopening, history export and key revocation. Container restart and clean-volume backup/restore were also checked. See the [validation record](artifacts/validation.json) for the exact evidence and remaining acceptance gates.

Bug reports should include reproduction steps and browser/runtime versions, with private keys and client data removed. Focused fixes and improvements are welcome through [issues](https://github.com/anshuman-pandey/review-dots/issues) and pull requests.

## Documentation

[Deployment & backups](docs/DEPLOYMENT.md) · [Scope & comparison](docs/SCOPE.md) · [Validation evidence](artifacts/validation.json) · [License](LICENSE)

## Current verification

See the [26 November audit checkpoint](docs/AUDIT.md) for the verified repository, release links, fresh core test result and remaining deployment/browser gates. Earlier validation records remain dated evidence.
