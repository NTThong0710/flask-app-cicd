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

def test_chatbot_interface(client):
    response = client.get('/chatbot')
    assert response.status_code == 200
    assert b'Flameo Chatbot' in response.data

def test_chatbot_api(client):
    response = client.post('/api/chat',
                         json={"message": "Hello"},
                         content_type='application/json')
    json_data = response.get_json()
    assert response.status_code == 200
    assert "response" in json_data
    assert "timestamp" in json_data