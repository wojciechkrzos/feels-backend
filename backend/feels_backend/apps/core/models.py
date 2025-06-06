from neomodel import (
    StructuredNode, StringProperty, IntegerProperty, DateTimeProperty,
    FloatProperty, RelationshipTo, RelationshipFrom, Relationship,
    UniqueIdProperty, ArrayProperty, BooleanProperty
)
from datetime import datetime


class FeelingType(StructuredNode):
    """
    Represents different types of feelings categorized by energy and pleasantness
    Examples: 'high_energy_pleasant', 'low_energy_unpleasant', etc.
    """
    name = StringProperty(unique_index=True, required=True)
    description = StringProperty()
    created_at = DateTimeProperty(default_now=True)


class Feeling(StructuredNode):
    """
    Represents a specific feeling/emotion with its color and type
    """
    name = StringProperty(unique_index=True, required=True)
    color = StringProperty(required=True)  # Hex color code like #FF5733
    description = StringProperty()
    created_at = DateTimeProperty(default_now=True)
    
    # Relationship to feeling type
    feeling_type = RelationshipTo(FeelingType, 'HAS_TYPE')


class Account(StructuredNode):
    """
    User account model with statistics tracking
    """
    uid = UniqueIdProperty()
    username = StringProperty(unique_index=True, required=True)
    email = StringProperty(unique_index=True, required=True)
    display_name = StringProperty()
    bio = StringProperty()
    avatar_url = StringProperty()
    password_hash = StringProperty(required=True)  # For authentication
    
    # Statistics
    posts_read_count = IntegerProperty(default=0)
    feelings_shared_count = IntegerProperty(default=0)
    
    # Timestamps
    created_at = DateTimeProperty(default_now=True)
    last_active = DateTimeProperty(default_now=True)
    
    # Relationships
    posts = RelationshipFrom('Post', 'CREATED_BY')
    friends = Relationship('Account', 'FRIENDS_WITH')
    sent_friend_requests = RelationshipTo('Account', 'SENT_FRIEND_REQUEST')
    received_friend_requests = RelationshipFrom('Account', 'SENT_FRIEND_REQUEST')
    chat_participants = RelationshipTo('Chat', 'PARTICIPATES_IN')


class FriendRequest(StructuredNode):
    """
    Represents a friend request between two accounts
    """
    uid = UniqueIdProperty()
    status = StringProperty(choices={
        'pending': 'Pending',
        'accepted': 'Accepted', 
        'rejected': 'Rejected'
    }, default='pending')
    message = StringProperty()
    created_at = DateTimeProperty(default_now=True)
    responded_at = DateTimeProperty()
    
    # Relationships
    sender = RelationshipFrom(Account, 'SENT_FRIEND_REQUEST')
    receiver = RelationshipTo(Account, 'RECEIVED_FRIEND_REQUEST')


class Post(StructuredNode):
    """
    Represents a post sharing an emotion/feeling
    """
    uid = UniqueIdProperty()
    body = StringProperty(required=True)
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty()
    
    # Relationships
    author = RelationshipTo(Account, 'CREATED_BY')
    feeling = RelationshipTo(Feeling, 'EXPRESSES_FEELING')
    read_by = RelationshipFrom(Account, 'READ_POST')


class Chat(StructuredNode):
    """
    Represents a chat conversation between users
    """
    uid = UniqueIdProperty()
    name = StringProperty()
    is_group_chat = BooleanProperty(default=False)
    created_at = DateTimeProperty(default_now=True)
    last_message_at = DateTimeProperty()
    
    # Relationships
    participants = RelationshipFrom(Account, 'PARTICIPATES_IN')
    messages = RelationshipFrom('Message', 'SENT_TO')


class Message(StructuredNode):
    """
    Represents a message in a chat
    """
    uid = UniqueIdProperty()
    text = StringProperty(required=True)
    message_type = StringProperty(choices={
        'text': 'Text',
        'feeling': 'Feeling',
        'image': 'Image'
    }, default='text')
    created_at = DateTimeProperty(default_now=True)
    is_read = BooleanProperty(default=False)
    
    # Relationships
    sender = RelationshipTo(Account, 'SENT_BY')
    chat = RelationshipTo(Chat, 'SENT_TO')
    feeling = RelationshipTo(Feeling, 'EXPRESSES_FEELING')  # OPTIONAL 