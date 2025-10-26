import pytest
from datetime import datetime, timedelta, timezone
import uuid
from app import create_app
from db import db
from models.post import PostModel

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def sample_post_data():
    """Sample post data for testing."""
    return {
        "routeId": str(uuid.uuid4()),
        "userId": str(uuid.uuid4()),
        "expireAt": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    }

class TestPostEndpoints:
    def test_create_post_success(self, client, sample_post_data):
        """Test successful post creation"""
        response = client.post('/posts', json=sample_post_data)
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        assert data['userId'] == sample_post_data['userId']

    def test_create_post_invalid_expire_date(self, client):
        """Test post creation with invalid expire date"""
        post_data = {
            "routeId": str(uuid.uuid4()),
            "userId": str(uuid.uuid4()),
            "expireAt": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        }
        response = client.post('/posts', json=post_data)
        assert response.status_code == 412
        assert "La fecha expiración no es válida" in response.get_json()['msg']

    def test_get_posts_empty(self, client):
        """Test getting posts when none exist"""
        response = client.get('/posts')
        assert response.status_code == 200
        data = response.get_json()
        assert data == []

    def test_get_posts_with_filter(self, client, sample_post_data):
        """Test getting posts with filters"""
        # Create a post first
        create_response = client.post('/posts', json=sample_post_data)
        created_post = create_response.get_json()
        
        # Test filter by route using the actual routeId from the created post
        response = client.get(f'/posts?route={sample_post_data["routeId"]}')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['routeId'] == sample_post_data['routeId']

    def test_get_post_by_id(self, client, sample_post_data):
        """Test getting a specific post by ID"""
        # Create a post first
        create_response = client.post('/posts', json=sample_post_data)
        post_id = create_response.get_json()['id']
        
        # Get the post
        response = client.get(f'/posts/{post_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == post_id

    def test_get_post_by_invalid_id(self, client):
        """Test getting a post with invalid ID format"""
        response = client.get('/posts/invalid-uuid')
        assert response.status_code == 400

    def test_get_post_not_found(self, client):
        """Test getting a post that doesn't exist"""
        fake_id = str(uuid.uuid4())
        response = client.get(f'/posts/{fake_id}')
        assert response.status_code == 404

    def test_delete_post(self, client, sample_post_data):
        """Test deleting a post"""
        # Create a post first
        create_response = client.post('/posts', json=sample_post_data)
        post_id = create_response.get_json()['id']
        
        # Delete the post
        response = client.delete(f'/posts/{post_id}')
        assert response.status_code == 200
        assert "la publicación fue eliminada" in response.get_json()['msg']

    def test_delete_post_invalid_id(self, client):
        """Test deleting a post with invalid ID format"""
        response = client.delete('/posts/invalid-uuid')
        assert response.status_code == 400

    def test_delete_post_not_found(self, client):
        """Test deleting a post that doesn't exist"""
        fake_id = str(uuid.uuid4())
        response = client.delete(f'/posts/{fake_id}')
        assert response.status_code == 404

    def test_count_posts(self, client, sample_post_data):
        """Test counting posts"""
        # Initially should be 0
        response = client.get('/posts/count')
        assert response.status_code == 200
        assert response.get_json()['count'] == 0
        
        # After creating a post should be 1
        client.post('/posts', json=sample_post_data)
        response = client.get('/posts/count')
        assert response.status_code == 200
        assert response.get_json()['count'] == 1

    def test_ping_endpoint(self, client):
        """Test ping endpoint"""
        response = client.get('/posts/ping')
        assert response.status_code == 200
        assert response.get_json() == "pong"

    def test_reset_endpoint(self, client, sample_post_data):
        """Test reset endpoint"""
        # Create a post first
        client.post('/posts', json=sample_post_data)
        
        # Verify post exists
        response = client.get('/posts/count')
        assert response.get_json()['count'] == 1
        
        # Reset database
        response = client.post('/posts/reset')
        assert response.status_code == 200
        assert "Todos los datos fueron eliminados" in response.get_json()['msg']
        
        # Verify post is gone
        response = client.get('/posts/count')
        assert response.get_json()['count'] == 0
