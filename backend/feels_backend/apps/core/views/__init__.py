"""
Views package for the core application.
This package contains all view classes organized in separate modules.
"""

from .account_view import AccountView
from .post_view import PostView
from .feeling_view import FeelingView
from .friend_request_view import FriendRequestView
from .user_posts_view import UserPostsView
from .chat_view import ChatView, MessageView

__all__ = [
    'AccountView',
    'PostView', 
    'FeelingView',
    'FriendRequestView',
    'UserPostsView',
    'ChatView',
    'MessageView'
]
