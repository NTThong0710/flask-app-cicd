import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    json_data = response.get_json()
    assert response.status_code == 200
    assert "Hello from Flask" in json_data['message']

def test_health(client):
    response = client.get('/health')
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['status'] == 'healthy'