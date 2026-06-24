def test_api_automation_create_list_copy_delete(client, response_data):
    cases_response = client.get("/api/v1/api-automation/cases", params={"project_id": 1})
    assert cases_response.status_code == 200
    assert response_data(cases_response) == []

    detail_response = client.get("/api/v1/api-automation/cases/10001")
    assert detail_response.status_code == 200
    assert detail_response.json()["code"] == 404
