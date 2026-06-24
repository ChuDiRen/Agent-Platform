def test_user_crud_uses_unified_response(client, response_data):
    create_resp = client.post(
        "/api/v1/users/",
        json={"email": "lifecycle@example.com", "password": "pass123456", "full_name": "Lifecycle User"},
    )
    assert create_resp.status_code == 200
    user = response_data(create_resp)
    assert user["email"] == "lifecycle@example.com"
    assert "password" not in user
    assert "hashed_password" not in user

    duplicate_resp = client.post(
        "/api/v1/users/",
        json={"email": "lifecycle@example.com", "password": "anotherpass"},
    )
    assert duplicate_resp.status_code == 200
    assert duplicate_resp.json()["code"] == 400

    list_resp = client.get("/api/v1/users/")
    users = response_data(list_resp)
    assert [item["email"] for item in users] == ["lifecycle@example.com"]

    update_resp = client.put(
        f"/api/v1/users/{user['id']}",
        json={"email": "changed@example.com", "full_name": "Updated Lifecycle"},
    )
    updated = response_data(update_resp)
    assert updated["email"] == "changed@example.com"
    assert updated["full_name"] == "Updated Lifecycle"

    delete_resp = client.delete(f"/api/v1/users/{user['id']}")
    assert response_data(delete_resp)["email"] == "changed@example.com"

    missing_resp = client.get(f"/api/v1/users/{user['id']}")
    assert missing_resp.status_code == 200
    assert missing_resp.json()["code"] == 404


def test_login_uses_unified_response(client, response_data):
    client.post(
        "/api/v1/users/",
        json={"email": "login@example.com", "password": "mypassword"},
    )

    login_resp = client.post(
        "/api/v1/users/login",
        json={"email": "login@example.com", "password": "mypassword"},
    )
    login = response_data(login_resp)
    assert login["token_type"] == "bearer"
    assert login["access_token"]
    assert login["user"]["email"] == "login@example.com"

    wrong_resp = client.post(
        "/api/v1/users/login",
        json={"email": "login@example.com", "password": "wrongpass"},
    )
    assert wrong_resp.status_code == 200
    assert wrong_resp.json()["code"] == 401
