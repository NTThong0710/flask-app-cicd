import pytest
import json
import os
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Create empty chat_history.json for testing
        with open('chat_history.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        # Create a minimal test DATA_CHATBOT.csv if it doesn't exist
        if not os.path.exists('DATA_CHATBOT.csv'):
            with open('DATA_CHATBOT.csv', 'w', encoding='utf-8') as f:
                f.write('CÂU HỎI,CÂU TRẢ LỜI\n')
                f.write('xin chào,Chào bạn! Tôi là chatbot.\n')
                f.write('bạn là ai,Tôi là Flameo Chatbot.\n')
        yield client
        # Clean up after tests
        if os.path.exists('chat_history.json'):
            os.remove('chat_history.json')

def test_index_route(client):
    """Test the main page loads correctly"""
    response = client.get('/error')
    assert response.status_code == 200
    assert b'html' in response.data.lower()  # Should return HTML content

def test_get_response(client):
    """Test the chatbot response endpoint"""
    response = client.post('/get_response', 
                         json={"message": "xin chào"},
                         content_type='application/json')
    json_data = response.get_json()
    assert response.status_code == 200
    assert "response" in json_data
    assert isinstance(json_data["response"], str)

def test_chat_history(client):
    """Test getting chat history"""
    response = client.get('/chat_history.json')
    json_data = response.get_json()
    assert response.status_code == 200
    assert isinstance(json_data, list)

def test_clear_history(client):
    """Test clearing chat history"""
    # First add something to history
    client.post('/get_response', 
               json={"message": "xin chào"},
               content_type='application/json')
    
    # Then clear history
    response = client.post('/clear_history')
    assert response.status_code == 200
    
    # Check if history is cleared
    history_response = client.get('/chat_history.json')
    history_data = history_response.get_json()
    assert len(history_data) == 0

def test_faq_questions(client):
    """Test getting FAQ questions"""
    response = client.get('/faq_questions')
    json_data = response.get_json()
    assert response.status_code == 200
    assert isinstance(json_data, list)
