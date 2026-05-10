def test_create_user(client):
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "password": "testpass123", "full_name": "Test User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_read_users(client):
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
