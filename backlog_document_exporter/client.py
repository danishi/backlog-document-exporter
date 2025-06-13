import os
import time
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv


class RateLimiter:
    def __init__(self, interval: float = 1.1):
        """Simple rate limiter to wait between API calls."""
        self.interval = interval
        self._last_call = 0.0

    def wait(self) -> None:
        now = time.time()
        sleep_time = self._last_call + self.interval - now
        if sleep_time > 0:
            time.sleep(sleep_time)
        self._last_call = time.time()


class BacklogClient:
    def __init__(self, space_domain: str, api_key: str, project_key: str):
        self.space_domain = space_domain
        self.api_key = api_key
        self.project_key = project_key
        self.base_url = f"https://{space_domain}/api/v2"
        self.rate_limiter = RateLimiter()

    @classmethod
    def from_env(cls) -> "BacklogClient":
        load_dotenv()
        api_key = os.getenv("BACKLOG_API_KEY")
        project_key = os.getenv("BACKLOG_PROJECT_KEY")
        space_domain = os.getenv("BACKLOG_SPACE_DOMAIN")
        if not api_key or not project_key or not space_domain:
            raise ValueError(
                "BACKLOG_API_KEY, BACKLOG_PROJECT_KEY and "
                "BACKLOG_SPACE_DOMAIN must be set"
            )
        return cls(space_domain, api_key, project_key)

    def _request(
        self,
        method: str,
        path: str,
        params: Dict[str, Any] | None = None,
        raw: bool = False,
    ) -> Any:
        """Perform an API request.

        If ``raw`` is True, return the ``requests.Response`` object.
        """
        self.rate_limiter.wait()
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        response = requests.request(
            method, f"{self.base_url}{path}", params=params
        )
        response.raise_for_status()
        if raw:
            return response
        if response.headers.get("Content-Type", "").startswith(
            "application/json"
        ):
            return response.json()
        return response.content

    def get_project_id(self) -> int:
        statuses = self._request(
            "GET", f"/projects/{self.project_key}/statuses"
        )
        if not statuses:
            raise RuntimeError("No statuses found for project")
        return int(statuses[0]["projectId"])

    def get_document_list(self, project_id: int) -> List[Dict[str, Any]]:
        return self._request(
            "GET", "/documents", {"projectId[]": project_id}
        )

    def get_document_tree(self, project_id: int) -> Dict[str, Any]:
        return self._request(
            "GET", "/documents/tree", {"projectIdOrKey": project_id}
        )

    def get_document_info(self, document_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/documents/{document_id}")

    def get_document_attachments(
        self, document_id: str
    ) -> List[Dict[str, Any]]:
        return self._request("GET", f"/documents/{document_id}/attachments")

    def download_attachment(
        self, document_id: str, attachment_id: int, output_dir: str
    ) -> str:
        response = self._request(
            "GET",
            f"/documents/{document_id}/attachments/{attachment_id}",
            raw=True,
        )
        disposition = response.headers.get("Content-Disposition", "")
        filename = None
        if "filename=" in disposition:
            filename = disposition.split("filename=")[-1].strip("\"")
        if not filename:
            filename = str(attachment_id)
        path = os.path.join(output_dir, filename)
        with open(path, "wb") as f:
            f.write(response.content)
        return path
