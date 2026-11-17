
import os
import uuid
import requests
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(Path(__file__).parent / ".env")


def test_api():
    username = os.getenv("GITHUB_USERNAME")
    token = os.getenv("GITHUB_TOKEN")
    base_name = os.getenv("GITHUB_REPO_NAME")

    # Проверяем настройки
    assert username and token and base_name, "Заполни файл .env"
    assert base_name == "qa-api-test-temp"

    # Каждый запуск создаёт репозиторий с новым именем
    repo_name = base_name + "-" + uuid.uuid4().hex[:8]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    api = "https://api.github.com"
    repo_url = f"{api}/repos/{username}/{repo_name}"

    # Проверяем аккаунт
    user = requests.get(f"{api}/user", headers=headers, timeout=15)
    assert user.status_code == 200, user.text
    assert user.json()["login"].lower() == username.lower()

    created_id = None

    try:
        # 1. Создаём публичный репозиторий
        response = requests.post(
            f"{api}/user/repos",
            headers=headers,
            json={"name": repo_name, "private": False},
            timeout=15
        )

        assert response.status_code == 201, response.text
        created = response.json()
        created_id = created["id"]

        assert created["name"] == repo_name
        assert created["private"] is False

        print("Репозиторий создан:", repo_name)

        # 2. Проверяем наличие в списке репозиториев
        url = f"{api}/user/repos"
        params = {"per_page": 100, "affiliation": "owner"}
        found = False

        while url:
            response = requests.get(
                url, headers=headers, params=params, timeout=15
            )
            assert response.status_code == 200, response.text

            found = any(
                repo["id"] == created_id
                for repo in response.json()
            ) or found

            if found:
                break

            url = response.links.get("next", {}).get("url")
            params = None

        assert found, "Репозиторий не найден в списке"
        print("Репозиторий найден в списке!")

    finally:
        # 3. Удаляем только созданный этим тестом репозиторий
        if created_id is not None:
            check = requests.get(
                repo_url, headers=headers, timeout=15
            )

            # Проверяем ответ GitHub перед удалением
            assert check.status_code == 200, (
                f"Не удалось проверить репозиторий перед удалением: {check.status_code}"
            )

            # Проверяем ID, чтобы не удалить чужой репозиторий
            assert check.json()["id"] == created_id

            # Удаляем репозиторий
            response = requests.delete(
                repo_url, headers=headers, timeout=15
            )

            assert response.status_code == 204, response.text

            # Проверяем, что репозиторий больше не существует
            response = requests.get(
                repo_url, headers=headers, timeout=15
            )

            assert response.status_code == 404, "Репозиторий всё ещё существует"

            print("Тестовый репозиторий успешно удалён и проверен!")
