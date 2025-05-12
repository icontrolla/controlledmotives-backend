from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import  ArtworkViewSet, FineArtViewSet, ArtistViewSet, ThriftStoreItemViewSet, PaintingViewSet, DrawingViewSet, NotificationViewSet, SubscriptionPlanViewSet, EthereumTransactionViewSet, PostViewSet, AestheticMomentViewSet, CinematographyGalleryViewSet, PhotographyContentViewSet, ArtGalleryViewSet, ArtCategoryViewSet, ConceptualMixedMediaViewSet, FashionArtViewSet, VirtualInteractiveArtViewSet
from . import views
from django.urls import re_path
from .views import ArtworkListAPIView
from .views import ArtistLoginView, LoginView
from .views import FrontendAppView

app_name = 'profiles'

# DRF Router for API endpoints
router = DefaultRouter()
re_path(r'^.*$', FrontendAppView.as_view()),
router.register(r'artworks', ArtworkViewSet, basename='artwork')
router.register(r'fine-arts', FineArtViewSet, basename='fine-art')
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'thrift-items', ThriftStoreItemViewSet, basename='thrift-item')
router.register(r'paintings', PaintingViewSet, basename='painting')
router.register(r'drawings', DrawingViewSet, basename='drawing')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscription-plan')
router.register(r'transactions', EthereumTransactionViewSet, basename='transaction')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'moments', AestheticMomentViewSet, basename='moment')
router.register(r'cinematography', CinematographyGalleryViewSet, basename='cinematography')
router.register(r'photography', PhotographyContentViewSet, basename='photography')
router.register(r'art-galleries', ArtGalleryViewSet, basename='art-gallery')
router.register(r'categories', ArtCategoryViewSet, basename='category')
router.register(r'conceptual-media', ConceptualMixedMediaViewSet, basename='conceptual-media')
router.register(r'fashion-art', FashionArtViewSet, basename='fashion-art')
router.register(r'virtual-art', VirtualInteractiveArtViewSet, basename='virtual-art')

urlpatterns = [
    # Admin and Authentication
    path('', views.home, name='home'),
    path('admin/', admin.site.urls, name='admin'),
    path('accounts/', include('allauth.urls')),  # Allauth for social/standard auth
    path('api/artist-login/', ArtistLoginView.as_view(), name='artist_login'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/artist-signup/', views.artist_signup, name='artist_signup'),  # Artist signup
    path('api/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),  # Logout

    # API Endpoints (via DRF router)
    path('api/', include(router.urls)),

    # Profile-related API Endpoints
    path('api/my-profile/', views.Profile, name='my_profile'),  # Current user profile
    path('api/artist-profile/<int:artist_id>/', views.artist_profile, name='artist_profile'),  # Specific artist profile

    # Post-related API Endpoints
    path('api/create-post/', views.create_post, name='create_post'),  # Create a post
    path('api/delete-post/<int:post_id>/', views.delete_post, name='delete_post'),  # Delete a post
    path('api/flower-post/<int:post_id>/', views.flower_post, name='flower_post'),


    # Artwork and Store API Endpoints
    path('artworks/', ArtworkListAPIView.as_view(), name='artwork-list'),
    path('api/artwork/<int:artwork_id>/buy/', views.buy_artwork, name='buy_artwork'),  # Buy artwork
    path('api/artwork/<int:artwork_id>/toggle-flower/', views.flower_post, name='toggle_flower'),  # Toggle flower
    path('api/process-payment/<int:artwork_id>/<int:price>/', views.process_payment, name='process_payment'),  # Process payment

    # Search API Endpoint
    path('api/search/', views.search, name='search'),  # Search functionality

    # Artist Dashboard API Endpoint
    path('api/artist-dashboard/', views.artist_dashboard, name='artist_dashboard'),  # Artist dashboard data

    # Feedback API Endpoint
    path('api/submit-feedback/', views.submit_feedback, name='submit_feedback'),  # Submit feedback

    # Subscription and Payment API Endpoints
    path('api/subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),  # Subscribe to a plan
    path('api/checkout/subscription/<int:plan_id>/', views.create_checkout_session, name='checkout_subscription'),  # Subscription checkout
    path('api/subscribe/success/', views.subscribe_success, name='subscribe_success'),  # Subscription success
    path('api/cancel-subscription/', views.cancel_subscription, name='cancel_subscription'),  # Cancel subscription
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),  # Stripe webhook
    path('api/create-stripe-product/', views.create_stripe_product, name='create_stripe_product'),  # Create Stripe product

    # Blockchain and Wallet API Endpoints
    path('api/wallet/', views.wallet_page, name='wallet_page'),  # Wallet overview
    path('api/create-ethereum-wallet/', views.create_ethereum_wallet, name='create_ethereum_wallet'),  # Create Ethereum wallet
    path('api/save-wallet/', views.save_wallet, name='save_wallet'),  # Save wallet address
    path('api/send-eth/', views.send_eth_view, name='send_eth'),  # Send Ethereum

    # Home and Static Pages
    path('api/home/', views.home, name='home'),  # Home page data
    path('api/about/', views.about_page, name='about'),  # About page data

    # Notification Management
    path('api/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notifications/delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
    path('api/notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


