import io
import re
import zipfile

import requests
from requests.exceptions import RequestException

# Only accept https://github.com/<owner>/<repo> (optionally with a trailing
# slash or ".git" suffix, both stripped before matching). Anything else is
# rejected up front instead of being sent to GitHub and producing a
# confusing downstream error.
GITHUB_URL_PATTERN = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)$"
)

# Branches attempted, in order, when downloading the repository archive.
CANDIDATE_BRANCHES = ("main", "master")


class GitHubService:
    def fetch_repository_files(self, repo_url: str) -> list[tuple[str, str]]:
        """
        Fetches a public GitHub repository zip archive and extracts all Python files.
        Returns a list of (filepath, source_code) tuples.

        Raises ValueError with a clear, user-facing message for every failure
        mode: malformed URL, non-GitHub URL, inaccessible/private repository,
        network failure, corrupt archive, or a repository with no parseable
        Python source.
        """
        clean_url = (repo_url or "").strip().rstrip("/")
        clean_url = clean_url.removesuffix(".git")

        match = GITHUB_URL_PATTERN.match(clean_url)
        if not match:
            raise ValueError(
                f"'{repo_url}' is not a valid GitHub repository URL. Expected "
                "a format like https://github.com/owner/repository."
            )

        owner, repo = match.group("owner"), match.group("repo")

        response = None
        last_error: str | None = None
        for branch in CANDIDATE_BRANCHES:
            zip_url = f"{clean_url}/archive/refs/heads/{branch}.zip"
            try:
                candidate = requests.get(zip_url, timeout=15)
            except RequestException as e:
                raise ValueError(f"Network error connecting to GitHub: {e}") from e

            if candidate.status_code == 200:
                response = candidate
                break
            if candidate.status_code == 404:
                last_error = (
                    f"Repository '{owner}/{repo}' was not found on the "
                    f"'{branch}' branch, is private, or does not exist."
                )
            else:
                last_error = (
                    f"GitHub returned HTTP {candidate.status_code} while "
                    f"fetching '{repo_url}'."
                )

        if response is None:
            raise ValueError(
                last_error or f"Could not fetch repository from {repo_url}."
            )

        files = []
        try:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                for filename in z.namelist():
                    if filename.endswith(".py") and not any(
                        part.startswith(".") for part in filename.split("/")
                    ):
                        parts = filename.split("/")[1:]
                        relative_path = "/".join(parts)
                        if relative_path:
                            with z.open(filename) as f:
                                code = f.read().decode("utf-8", errors="ignore")
                                files.append((relative_path, code))
        except (zipfile.BadZipFile, KeyError, OSError) as e:
            raise ValueError(f"Failed to parse repository archive: {e}") from e

        if not files:
            raise ValueError(
                f"Repository '{owner}/{repo}' does not contain any parseable "
                "Python (.py) files."
            )

        return files


github_service = GitHubService()
