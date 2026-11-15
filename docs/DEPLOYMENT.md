# Persistent Review Dots setup

This recipe runs a local persistent service. It does not deploy a public site or configure HTTPS.

## Start with Docker Compose

```sh
python3 scripts/setup.py
docker compose up -d --build
```

The setup script creates a random `REVIEW_OWNER_KEY` in a private mode-0600 `.env` file and refuses to overwrite an existing file. Read the key locally and use it to open the owner workspace at **http://127.0.0.1:8092**. Do not paste the key into Git, screenshots, URLs, or client handoffs.

The application runs as UID/GID 10001 using Waitress. Its application filesystem is read-only; `/tmp` is temporary; `/data` is the persistent `review-data` named volume. `docker compose down` retains that volume. **`docker compose down -v` deletes it and its client records.**

Normal builds verify TLS when installing dependencies. If your network uses a private trusted CA, pass that certificate bundle as a build secret:

```sh
docker build --secret id=pip_ca,src=/path/to/trusted-ca-bundle.pem -t review-dots-local .
```

The CA bundle is available only during dependency installation. Do not disable certificate verification.

## Backup and restore

A backup contains images, reviewer comments, self-reported names, resolution history, and hashed reviewer keys. Keep it private; encrypt off-machine copies. Preserve the owner key separately in secure storage.

Stop the writer before copying a container database. Use a fresh backup directory:

```sh
umask 077
mkdir review-backup
docker compose stop review-dots
docker compose cp review-dots:/data/review.sqlite3 review-backup/source.sqlite3
python3 scripts/backup.py review-backup/source.sqlite3 review-backup/review.sqlite3
docker compose start review-dots
```

The backup helper uses SQLite's backup API, checks database integrity, creates the destination with mode 0600 and refuses to overwrite existing files. A native installation can use it directly against the live database.

Restore only into a stopped service. First preserve the current database in another private backup. Copy the chosen backup into `/data/review.sqlite3`; set its owner to UID/GID `10001:10001` and mode `0600`; then start the service. Verify an image download, comment history, and a new comment. Restoring an older backup restores its earlier reviewer-key state: rotate keys again if they were revoked after the backup was taken. Revocation cannot erase previously downloaded images or exports.

The automated disposable test demonstrates clean-volume restore without touching your production volumes:

```sh
docker build -t review-dots-acceptance:local .
python3 scripts/container_acceptance.py
```

It uses unique test containers/volumes and the bundled synthetic image, and cleans up its resources afterwards.

## Native WSGI service

```sh
pip install -r requirements.txt
export REVIEW_DATA_DIR=./data
# Set REVIEW_OWNER_KEY from your securely stored random owner key.
python serve.py
```

The default address is `127.0.0.1:8092`. Use your operating system's service manager for automatic startup. Changing the owner key and restarting revokes the previous owner key; reviewer keys are stored in the database and are unaffected.

## Remote reviewers

Compose publishes the port on localhost only. A remote reviewer needs an authorized HTTPS reverse proxy/domain in front of the service, with upload limits and timeouts compatible with a 10 MiB file. Verify access from a second device over HTTPS before announcing it as live. This has not been tested or deployed here.

No domain, TLS certificate, remote host, rate limiting, installation-wide storage quota, email delivery, or verified user identities are provided by this recipe. Anyone holding a reviewer key can read that board and add comments; only the owner can resolve them. The current UI is English; six-language support is pending.
