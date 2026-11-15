# Review Dots handoff

**Runnable:** local English owner/reviewer image-feedback app. Install requirements and run `python server.py` with a random `REVIEW_OWNER_KEY` of at least 32 ASCII characters. Open http://127.0.0.1:8092. The README includes the exact commands.

**Passed:** 15 Python tests; Chromium image upload → reviewer pin → owner resolve/reopen → JSON history download → reviewer-key revocation. Non-root container restart, image/comment/history backup and clean-volume restore, post-restore writes and token revocation passed. Desktop and 390px mobile screenshots inspected; no horizontal overflow. Image coordinates may also be entered by keyboard. A synthetic poster is bundled for testing.

**Pending:** six interface languages, public HTTPS acceptance, broader name review. A persistent Waitress/Compose setup and backup/restore helper are included; see docs/DEPLOYMENT.md. This is not a finished public release. Do not run tests against real client data. Keep owner/reviewer keys private; keys stay in browser memory, not URLs or localStorage. Back up the SQLite database while the service is stopped. Revocation cannot erase data already downloaded by a reviewer.

**Next action:** implement the six-language interface, then owner review. The owner decides whether to create/publish the independent repository after review. Intended repository: anshuman-pandey/review-dots; not verified public. No push or repository creation performed.
