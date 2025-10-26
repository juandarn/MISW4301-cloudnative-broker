import pytest
from datetime import datetime, timedelta, timezone
import uuid
from models.post import PostModel

class TestPostModel:
    def test_create_post(self):
        """Test creating a new post"""
        post_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        
        post = PostModel(
            id=post_id,
            routeId="route-123",
            userId="user-456",
            expireAt=datetime.now(timezone.utc) + timedelta(days=1),
            createdAt=created_at
        )
        
        assert post.routeId == "route-123"
        assert post.userId == "user-456"
        assert post.expireAt > datetime.now(timezone.utc)
        assert post.id == post_id
        assert post.createdAt == created_at

    def test_post_id_is_uuid(self):
        """Test that post ID is a valid UUID string"""
        post_id = str(uuid.uuid4())
        post = PostModel(
            id=post_id,
            routeId="route-123",
            userId="user-456",
            expireAt=datetime.now(timezone.utc) + timedelta(days=1)
        )
        
        # Check that ID is a string
        assert isinstance(post.id, str)
        
        # Check that ID is not empty
        assert len(post.id) > 0
        
        # Check that it's a valid UUID
        try:
            uuid.UUID(post.id)
        except ValueError:
            pytest.fail("Post ID is not a valid UUID")

    def test_post_created_at_is_datetime(self):
        """Test that createdAt is a datetime object"""
        created_at = datetime.now(timezone.utc)
        post = PostModel(
            routeId="route-123",
            userId="user-456",
            expireAt=datetime.now(timezone.utc) + timedelta(days=1),
            createdAt=created_at
        )
        
        assert isinstance(post.createdAt, datetime)

    def test_to_dict_method(self):
        """Test the to_dict method returns proper format"""
        expire_at = datetime.now(timezone.utc) + timedelta(days=1)
        created_at = datetime.now(timezone.utc)
        
        post = PostModel(
            routeId="route-123",
            userId="user-456",
            expireAt=expire_at,
            createdAt=created_at
        )
        
        post_dict = post.to_dict()
        
        assert post_dict['routeId'] == "route-123"
        assert post_dict['userId'] == "user-456"
        assert post_dict['expireAt'] == expire_at.isoformat()
        assert post_dict['createdAt'] == created_at.isoformat()
