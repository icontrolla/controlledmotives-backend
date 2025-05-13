from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Artwork, FineArt, Artist, ThriftStoreItem, Painting, DrawingArtwork,
    AbstractArtwork, AestheticMoment, Notification, SubscriptionPlan,
    UserSubscription, BlockchainWallet, EthereumTransaction, Post, Like,
    Feedback, CinematographyGallery, PhotographyContent, ArtGallery,
    ArtCategory, Profile, ConceptualMixedMedia, FashionArt, VirtualInteractiveArt
)

# Utility for building full image/video URLs
def build_absolute_uri(context, file):
    if file and context.get('request'):
        return context['request'].build_absolute_uri(file.url)
    return None

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'email': {'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

# Basic user serializer for nested representation
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

# Profile serializer linking to the above UserSerializer
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'profile_picture', 'location', 'website']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

# Base image serializer mixin
class ImageFieldSerializerMixin(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return build_absolute_uri(self.context, getattr(obj, 'image', None))

# Core Artwork serializers
class FineArtSerializer(ImageFieldSerializerMixin):
    class Meta:
        model = FineArt
        fields = ['id', 'title', 'description', 'image', 'created_at']

class PaintingSerializer(ImageFieldSerializerMixin):
    class Meta:
        model = Painting
        fields = ['id', 'title', 'description', 'image', 'premiere_end_date', 'created_at']

class DrawingArtworkSerializer(ImageFieldSerializerMixin):
    class Meta:
        model = DrawingArtwork
        fields = ['id', 'title', 'description', 'image', 'created_at']

class AbstractArtworkSerializer(ImageFieldSerializerMixin):
    class Meta:
        model = AbstractArtwork
        fields = ['id', 'title', 'description', 'image', 'created_at']

class ThriftStoreItemSerializer(ImageFieldSerializerMixin):
    class Meta:
        model = ThriftStoreItem
        fields = ['id', 'title', 'description', 'price', 'image', 'created_at']

class ConceptualMixedMediaSerializer(ImageFieldSerializerMixin):
    class Meta:
        model = ConceptualMixedMedia
        fields = ['id', 'title', 'description', 'image', 'created_at']

class FashionArtSerializer(ImageFieldSerializerMixin):
    class Meta:
        model = FashionArt
        fields = ['id', 'title', 'description', 'image', 'created_at']

class VirtualInteractiveArtSerializer(ImageFieldSerializerMixin):
    interactive_url = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = VirtualInteractiveArt
        fields = ['id', 'title', 'description', 'image', 'interactive_url', 'created_at']

# Artist
class ArtistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile_picture = serializers.SerializerMethodField()
    blockchain_address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Artist
        fields = ['id', 'user', 'bio', 'profile_picture', 'category', 'is_major', 'is_trending', 'medium', 'blockchain_address', 'created_at']

    def get_profile_picture(self, obj):
        return build_absolute_uri(self.context, obj.profile_picture)

# Aesthetic Moment
class AestheticMomentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()

    class Meta:
        model = AestheticMoment
        fields = ['id', 'user', 'title', 'description', 'image', 'video', 'created_at']

    def get_image(self, obj):
        return build_absolute_uri(self.context, obj.image)

    def get_video(self, obj):
        return build_absolute_uri(self.context, obj.video)

# Notification
class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'sender', 'message', 'post', 'is_read', 'created_at']

# Subscription
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'description', 'price', 'duration_days', 'stripe_price_id', 'created_at']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'plan', 'is_active', 'start_date', 'end_date', 'stripe_subscription_id', 'stripe_checkout_session_id']

# Blockchain
class BlockchainWalletSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = BlockchainWallet
        fields = ['id', 'user', 'address', 'created_at']

    def validate_address(self, value):
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError("Invalid Ethereum wallet address")
        return value

class EthereumTransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = EthereumTransaction
        fields = ['id', 'user', 'to_address', 'amount', 'txn_hash', 'status', 'created_at']

    def validate_to_address(self, value):
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError("Invalid Ethereum address")
        return value

# Posts & Interactions
class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    likes = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'caption', 'image', 'created_at', 'likes']

    def get_likes(self, obj):
        return obj.likes.count()

    def get_image(self, obj):
        return build_absolute_uri(self.context, obj.image)

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']

class FeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'comment', 'is_helpful', 'created_at']

# Galleries
class CinematographyGallerySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()

    class Meta:
        model = CinematographyGallery
        fields = ['id', 'title', 'description', 'image', 'video', 'created_at']

    def get_image(self, obj):
        return build_absolute_uri(self.context, obj.image)

    def get_video(self, obj):
        return build_absolute_uri(self.context, obj.video)

class PhotographyContentSerializer(ImageFieldSerializerMixin):
    class Meta:
        model = PhotographyContent
        fields = ['id', 'title', 'description', 'image', 'created_at']

class ArtGallerySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    flowers = serializers.SerializerMethodField()

    class Meta:
        model = ArtGallery
        fields = ['id', 'title', 'description', 'image', 'price', 'flowers', 'created_at']

    def get_image(self, obj):
        return build_absolute_uri(self.context, obj.image)

    def get_flowers(self, obj):
        return obj.flowers.count()

class ArtCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ArtCategory
        fields = ['id', 'name', 'description', 'subcategories', 'created_at']

# Basic Artwork
class ArtworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artwork
        fields = '__all__'
