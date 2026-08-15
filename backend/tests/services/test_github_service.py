import io
import zipfile
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import RequestException

from backend.services.github_service import GitHubService


def _zip_bytes(entries: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        for path, content in entries.items():
            z.writestr(path, content)
    buffer.seek(0)
    return buffer.getvalue()


@patch("backend.services.github_service.requests.get")
def test_github_service_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = _zip_bytes(
        {"repo-main/main.py": "def authenticate_user(): pass"}
    )
    mock_get.return_value = mock_response

    service = GitHubService()
    files = service.fetch_repository_files("https://github.com/test/repo")

    assert len(files) == 1
    assert files[0][0] == "main.py"
    assert "def authenticate_user" in files[0][1]


def test_github_service_rejects_malformed_url():
    service = GitHubService()
    with pytest.raises(ValueError, match="not a valid GitHub"):
        service.fetch_repository_files("not-a-url")


def test_github_service_rejects_non_github_url():
    service = GitHubService()
    with pytest.raises(ValueError, match="not a valid GitHub"):
        service.fetch_repository_files("https://gitlab.com/test/repo")


@patch("backend.services.github_service.requests.get")
def test_github_service_falls_back_to_master_branch(mock_get):
    not_found = MagicMock()
    not_found.status_code = 404

    found = MagicMock()
    found.status_code = 200
    found.content = _zip_bytes({"repo-master/app.py": "def run(): pass"})

    mock_get.side_effect = [not_found, found]

    service = GitHubService()
    files = service.fetch_repository_files("https://github.com/test/repo")

    assert len(files) == 1
    assert files[0][0] == "app.py"
    assert mock_get.call_count == 2


@patch("backend.services.github_service.requests.get")
def test_github_service_inaccessible_or_private_repository(mock_get):
    not_found = MagicMock()
    not_found.status_code = 404
    mock_get.return_value = not_found

    service = GitHubService()
    with pytest.raises(ValueError, match="private|not found"):
        service.fetch_repository_files("https://github.com/test/private-repo")


@patch("backend.services.github_service.requests.get")
def test_github_service_unexpected_http_error(mock_get):
    server_error = MagicMock()
    server_error.status_code = 503
    mock_get.return_value = server_error

    service = GitHubService()
    with pytest.raises(ValueError, match="HTTP 503"):
        service.fetch_repository_files("https://github.com/test/repo")


@patch("backend.services.github_service.requests.get")
def test_github_service_network_failure(mock_get):
    mock_get.side_effect = RequestException("connection refused")

    service = GitHubService()
    with pytest.raises(ValueError, match="Network error"):
        service.fetch_repository_files("https://github.com/test/repo")


@patch("backend.services.github_service.requests.get")
def test_github_service_empty_repository_raises_clear_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = _zip_bytes(
        {"repo-main/README.md": "# no python files here"}
    )
    mock_get.return_value = mock_response

    service = GitHubService()
    with pytest.raises(ValueError, match="Python"):
        service.fetch_repository_files("https://github.com/test/empty-repo")


@patch("backend.services.github_service.requests.get")
def test_github_service_corrupt_archive(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"this is not a real zip file"
    mock_get.return_value = mock_response

    service = GitHubService()
    with pytest.raises(ValueError, match="archive"):
        service.fetch_repository_files("https://github.com/test/repo")
