# Review Dots handoff

**Runnable:** local six-language owner/reviewer image-feedback app. Install requirements and run `python server.py` with a random `REVIEW_OWNER_KEY` of at least 32 ASCII characters. Open http://127.0.0.1:8092. The README includes the exact commands.

**Passed:** 16 Python tests; Chromium image upload → reviewer pin → owner resolve/reopen → JSON history download → reviewer-key revocation. Non-root container restart, image/comment/history backup and clean-volume restore, post-restore writes and token revocation passed. Desktop and 390px mobile screenshots inspected; no horizontal overflow. Image coordinates may also be entered by keyboard. A synthetic poster is bundled for testing.

**Pending:** public HTTPS acceptance, native-speaker review, and owner name/publication approval. A persistent Waitress/Compose setup and backup/restore helper are included; see docs/DEPLOYMENT.md. This is not a finished public release. Do not run tests against real client data. Keep owner/reviewer keys private; keys stay in browser memory, not URLs or localStorage. Back up the SQLite database while the service is stopped. Revocation cannot erase data already downloaded by a reviewer.

**Next action:** owner reviews the local package and creates the independent repository if approved. The owner decides whether to create/publish the independent repository after review. Intended repository: anshuman-pandey/review-dots; not verified public. No push or repository creation performed.

Six-language Chromium checks pass: regional browser preferences, saved choice, blocked storage, selected upload, reviewer draft/coordinates, unchanged image canvas, literal client content, localized access denial and mobile overflow. A mobile CSS bug hiding the translated lock label was found during visual review, fixed, and regression-checked.

[Open the prefilled repository creation form](https://github.com/new?name=review-dots&description=Open-source%20alternative%20to%20MarkUp.io%20for%20image%20feedback.%20Pin%20comments%20on%20PNG%2FJPEG%20designs%2C%20resolve%20reviews%2C%20revoke%20access%2C%20and%20export%20records.%20Self-hosted%2C%20six%20languages%2C%20MIT%20licensed.&visibility=public). Create an empty repository without adding a README, license, or .gitignore. This form does not publish the prepared code. Publication still needs the owner's go-ahead.
