
import requests
import test_api


class FakeResponse:
    def __init__(self, status_code, data=None):
        self.status_code = status_code
        self.data = data
        self.text = str(data)
        self.links = {}

    def json(self):
        return self.data


def test_github_api_without_real_requests(monkeypatch):
    monkeypatch.setenv("GITHUB_USERNAME", "Gar1kk")
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    monkeypatch.setenv("GITHUB_REPO_NAME", "qa-api-test-temp")

    repo = {"id": 123, "private": False}
    deleted = False

    def fake_get(url, **kwargs):
        if url.endswith("/user"):
            return FakeResponse(200, {"login": "Gar1kk"})

        if url.endswith("/user/repos"):
            return FakeResponse(200, [repo])

        if deleted:
            return FakeResponse(404)

        return FakeResponse(200, repo)

    def fake_post(url, **kwargs):
        repo["name"] = kwargs["json"]["name"]
        return FakeResponse(201, repo)

    def fake_delete(url, **kwargs):
        nonlocal deleted
        deleted = True
        return FakeResponse(204)

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(requests, "delete", fake_delete)

    test_api.test_api()

    assert deleted
    print("Проверка GitHub API успешно пройдена!")
