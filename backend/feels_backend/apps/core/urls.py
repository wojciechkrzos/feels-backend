from django.urls import path
from . import views
from .authentication import AuthView, ProfileView
from .demo_views import DemoView
from .health import HealthCheckView

app_name = 'core'

urlpatterns = [
    # Health check
    path('health/', HealthCheckView.as_view(), name='health'),
    
    # Demo interface
    path('demo/', DemoView.as_view(), name='demo'),
    
    # Authentication endpoints
    path('auth/', AuthView.as_view(), name='auth'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Account endpoints
    path('accounts/', views.AccountView.as_view(), name='accounts'),
    path('accounts/<str:account_id>/', views.AccountView.as_view(), name='account_detail'),
    
    # Post endpoints
    path('posts/', views.PostView.as_view(), name='posts'),
    path('posts/<str:post_id>/', views.PostView.as_view(), name='post_detail'),
    path('users/<str:user_id>/posts/', views.UserPostsView.as_view(), name='user_posts'),
    
    # Feeling endpoints
    path('feelings/', views.FeelingView.as_view(), name='feelings'),
    
    # Friend request endpoints
    path('friend-requests/', views.FriendRequestView.as_view(), name='friend_requests'),
    path('friend-requests/<str:request_id>/', views.FriendRequestView.as_view(), name='friend_request_detail'),
]
