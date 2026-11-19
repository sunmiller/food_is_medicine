# Dependency Vulnerability Triage

## Project-specific dependency notes

Last checked: 2026-11-17.

- `python-jose==3.5.0` was removed from `requirements.txt`. CVE-2026-85394 affects versions through 3.5.0, and a source search found no use of `jose` in this project or installed-package dependents. No fixed PyPI release was available when checked, so removal was preferred to an unverified upgrade.
- `authlib==1.6.1` was updated to `authlib==1.9.8`. Version 1.6.1 was affected by multiple advisories; 1.9.8 was the latest PyPI release checked, and OSV returned no advisories for that version. The app uses Authlib's Starlette OAuth client for Google sign-in (`authorize_access_token` and `parse_id_token`).
- `starlette==0.47.3` was updated to the CVE-2026-54283 fix, `1.3.1`. FastAPI 0.116.1 required `starlette<0.48.0`, so FastAPI was raised to 0.133.0, whose published requirement allows Starlette `>=0.40.0` without that upper bound. OSV returned no advisories for either selected version. The app has no direct `request.form()` calls, but the dependency was updated because the vulnerability affects Starlette/FastAPI form parsing.
- The `python:3.11-slim-bookworm` image includes Debian's `perl-base`. CVE-2026-57433 is fixed in Bookworm at `5.36.0-7+deb12u4`. The Dockerfile now updates apt metadata, upgrades only `perl-base`, and fails the build if the installed Debian package version is below that fix. A scanner path such as `/usr/share/doc/perl-base/copyright` identifies package metadata; the affected component is the `perl-base` package.
- The local virtual environment was updated to Authlib 1.9.8 and `python-jose` was uninstalled. The focused Google OAuth tests passed:

  ```powershell
  .\.venv\Scripts\python.exe -m unittest discover -s tests -p test_google_user.py
  ```

- `pip check` reported existing LangChain dependency conflicts (`langchain-classic` and `langgraph-prebuilt` versus the installed `langchain-core` and `langchain-text-splitters`); these were not part of the Authlib update.
- Authlib 1.9.8 emitted a non-fatal deprecation warning for its `httpx` integration, recommending `httpx2`.

## Future triage and deployment

1. Verify the affected and fixed version ranges using the advisory source (for example, OSV) and confirm the candidate release exists on PyPI.
2. Search project source for direct use and inspect installed-package dependents before deciding whether to upgrade or remove a dependency.
3. Pin the verified version in `requirements.txt`, update the project environment, and run the narrowest relevant tests.
4. Report unrelated `pip check` findings separately; do not silently broaden the dependency upgrade.
5. Rebuild the Docker image and recreate the service after dependency changes. Updating `requirements.txt` alone does not change an already-built image or running container. For this project:

   ```powershell
   docker build --no-cache -t food-search-api .
   docker compose up -d --force-recreate food-search-api
   ```

   If deploying a registry image, push the rebuilt image, then pull it on the server before recreating the service.
