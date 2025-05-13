from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from .views import (
    ArtworkViewSet, FineArtViewSet, ArtistViewSet, ThriftStoreItemViewSet,
    PaintingViewSet, DrawingViewSet, NotificationViewSet, SubscriptionPlanViewSet,
    EthereumTransactionViewSet, PostViewSet, AestheticMomentViewSet,
    CinematographyGalleryViewSet, PhotographyContentViewSet, ArtGalleryViewSet,
    ArtCategoryViewSet, ConceptualMixedMediaViewSet, FashionArtViewSet,
    VirtualInteractiveArtViewSet, ArtworkListAPIView, ArtistLoginView,
    LoginView, FrontendAppView, ArtistSignupView
)
from dj_rest_auth.registration.views import RegisterView

app_name = 'profiles'

# DRF Router for ModelViewSets
router = DefaultRouter()
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
    # Admin & Static Pages
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('api/home/', views.home, name='api_home'),
    path('api/about/', views.about_page, name='about'),

    # Auth
    path('accounts/', include('allauth.urls')),
    path('api/', include('dj_rest_auth.urls')),
    path('api/signup/', include('dj_rest_auth.registration.urls')),
    path('auth/registration/', RegisterView.as_view(), name='rest_register'),
    path('login/', LoginView.as_view(), name='login'),
    path('api/artist-login/', ArtistLoginView.as_view(), name='artist_login'),
    path('api/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Profiles & Artist Info
    path('api/my-profile/', views.Profile, name='my_profile'),
    path('api/artist-profile/<int:artist_id>/', views.artist_profile, name='artist_profile'),
    path('api/artist-dashboard/', views.artist_dashboard, name='artist_dashboard'),

    # Posts
    path('api/create-post/', views.create_post, name='create_post'),
    path('api/delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('api/flower-post/<int:post_id>/', views.flower_post, name='flower_post'),

    # Artwork
    path('artworks/', ArtworkListAPIView.as_view(), name='artwork-list'),
    path('api/artwork/<int:artwork_id>/buy/', views.buy_artwork, name='buy_artwork'),
    path('api/artwork/<int:artwork_id>/toggle-flower/', views.flower_post, name='toggle_flower'),

    # Payment & Subscriptions
    path('api/process-payment/<int:artwork_id>/<int:price>/', views.process_payment, name='process_payment'),
    path('api/subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('api/checkout/subscription/<int:plan_id>/', views.create_checkout_session, name='checkout_subscription'),
    path('api/subscribe/success/', views.subscribe_success, name='subscribe_success'),
    path('api/cancel-subscription/', views.cancel_subscription, name='cancel_subscription'),
    path('api/create-stripe-product/', views.create_stripe_product, name='create_stripe_product'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),

    # Ethereum/Blockchain
    path('api/wallet/', views.wallet_page, name='wallet_page'),
    path('api/create-ethereum-wallet/', views.create_ethereum_wallet, name='create_ethereum_wallet'),
    path('api/save-wallet/', views.save_wallet, name='save_wallet'),
    path('api/send-eth/', views.send_eth_view, name='send_eth'),

    # Notifications
    path('api/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notifications/delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
    path('api/notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),

    # Search & Feedback
    path('api/search/', views.search, name='search'),
    path('api/submit-feedback/', views.submit_feedback, name='submit_feedback'),

    # DRF Router Endpoints
    path('api/', include(router.urls)),

    # Catch-All for React Frontend
    path('', FrontendAppView.as_view(), name='frontend'),
]

# Media file serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
