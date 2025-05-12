from rest_framework import serializers, viewsets
from django.contrib.auth.models import User
from .models import (
    Artwork, FineArt, Artist, ThriftStoreItem, Painting, DrawingArtwork, AbstractArtwork,
    AestheticMoment, Notification, SubscriptionPlan, UserSubscription, BlockchainWallet,
    EthereumTransaction, Post, Like, Feedback, CinematographyGallery, PhotographyContent,
    ArtGallery, ArtCategory, Profile, ConceptualMixedMedia, FashionArt, VirtualInteractiveArt,
    ExhibitionPlan, UserSubscription
)

from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import requests
from rest_framework.generics import ListAPIView
# profiles/views.py
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from .serializers import (
    ArtworkSerializer, FineArtSerializer, ArtistSerializer, ThriftStoreItemSerializer, PaintingSerializer,
    DrawingArtworkSerializer, NotificationSerializer, SubscriptionPlanSerializer, EthereumTransactionSerializer, PostSerializer,
    AestheticMomentSerializer, CinematographyGallerySerializer, PhotographyContentSerializer, ArtGallerySerializer, ArtCategorySerializer, ConceptualMixedMediaSerializer,
    FashionArtSerializer, VirtualInteractiveArtSerializer
)
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import permission_classes
from django.db.models import Q
from .models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
import stripe
from web3 import Web3

from django.http import HttpResponse
from django.views.generic import View
import os

# Define the FrontendAppView here
class FrontendAppView(View):
    def get(self, request):
        index_path = os.path.join('static/frontend', 'index.html')
        return HttpResponse(open(index_path, 'rb').read(), content_type='text/html')



# NFT Storage API configuration
NFT_STORAGE_API_URL = 'https://api.nft.storage/upload'
NFT_STORAGE_API_KEY = settings.NFT_STORAGE_API_KEY  # Set this in your settings


# Set your Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


def index(request):
    return render(request, 'frontend/index.html')

# Ethereum Web3 setup (for example)
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'))




@api_view(['GET'])
def create_ethereum_wallet(request):
    acct = Account.create()
    return Response({
        'address': acct.address,
        'private_key': acct.key.hex(),  # Be cautious with this — don’t show private keys in production
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_wallet(request):
    wallet_address = request.data.get('wallet_address')
    if not wallet_address:
        return Response({'detail': 'Wallet address is required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    user.wallet_address = wallet_address
    user.save()
    return Response({'detail': 'Wallet address saved successfully.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_eth_view(request):
    recipient = request.data.get('recipient_address')
    amount = request.data.get('amount')  # in ETH

    if not recipient or not amount:
        return Response({'detail': 'Recipient address and amount are required.'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        # Convert ETH to Wei
        value = w3.toWei(float(amount), 'ether')

        # Get nonce
        nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)

        # Create transaction
        tx = {
            'nonce': nonce,
            'to': recipient,
            'value': value,
            'gas': 21000,
            'gasPrice': w3.toWei('50', 'gwei'),
        }

        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=SENDER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return Response({'detail': 'Transaction sent', 'tx_hash': tx_hash.hex()}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request, plan_id):
    try:
        # Here, you would fetch the plan details from your database using the plan_id
        plan = Plan.objects.get(id=plan_id)  # Assuming you have a Plan model for your subscription plans

        # Create a checkout session for Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': plan.name,
                        },
                        'unit_amount': plan.price * 100,  # Convert to cents
                    },
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=request.build_absolute_uri('/subscription/success/'),
            cancel_url=request.build_absolute_uri('/subscription/cancel/'),
        )

        return Response({
            'checkout_url': session.url
        }, status=status.HTTP_200_OK)

    except Plan.DoesNotExist:
        return Response({'detail': 'Subscription plan not found.'}, status=status.HTTP_404_NOT_FOUND)

    except stripe.error.StripeError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_stripe_product(request):
    # Get the data from the request (e.g., product name, description, price)
    name = request.data.get('name')
    description = request.data.get('description')
    price = request.data.get('price')  # Price in cents, e.g., 1000 for $10

    if not name or not description or not price:
        return Response({"detail": "Missing required fields: name, description, price."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Create a Stripe product
        product = stripe.Product.create(
            name=name,
            description=description,
        )

        # Create a Stripe price for the product
        price = stripe.Price.create(
            unit_amount=price,  # Price in cents
            currency='usd',  # Set the currency (you can change this)
            product=product.id,
        )

        # Return the product and price details
        return Response({
            'product_id': product.id,
            'price_id': price.id,
            'name': product.name,
            'description': product.description,
            'unit_amount': price.unit_amount,
            'currency': price.currency,
        }, status=status.HTTP_201_CREATED)

    except stripe.error.StripeError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VirtualInteractiveArtViewSet(viewsets.ModelViewSet):
    queryset = VirtualInteractiveArt.objects.all()
    serializer_class = VirtualInteractiveArtSerializer
    permission_classes = [IsAuthenticated]

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
def subscribe_success(request):
    # You can customize this as needed, maybe show a success message or return relevant data.
    return Response({'detail': 'Subscription successful!'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def cancel_subscription(request):
    try:
        # Retrieve the user's subscription ID from your model or request data
        subscription_id = request.data.get('subscription_id')

        if not subscription_id:
            return Response({'detail': 'Subscription ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Call Stripe API to cancel the subscription
        stripe.Subscription.delete(subscription_id)

        # You could update the database here, e.g., mark the user's subscription as canceled
        return Response({'detail': 'Subscription canceled successfully.'}, status=status.HTTP_200_OK)
    except stripe.error.StripeError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ThriftStoreItemViewSet(viewsets.ModelViewSet):
    queryset = ThriftStoreItem.objects.all()
    serializer_class = ThriftStoreItemSerializer
    permission_classes = [IsAuthenticated]


@csrf_exempt
@api_view(['POST'])
def stripe_webhook(request):
    # Retrieve the webhook secret and event from Stripe
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    # Verify the webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({'detail': 'Invalid payload.'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'detail': 'Invalid signature.'}, status=400)

    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        # Payment succeeded
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        customer_id = payment_intent['customer']
        # Process the payment (you can update your database here, e.g., marking the subscription as active)

        # Example: Retrieve user and update subscription status
        # You would fetch your user based on Stripe customer ID, e.g.:
        # user = User.objects.get(stripe_customer_id=customer_id)
        # user.subscription_status = 'active'
        # user.save()

    elif event['type'] == 'invoice.payment_failed':
        # Payment failed
        payment_intent = event['data']['object']
        # Handle the failed payment, notify the user, etc.

    # Other event types you can handle (you can add more cases)
    else:
        print(f"Unhandled event type: {event['type']}")

    # Acknowledge receipt of the event
    return JsonResponse({'detail': 'Event received'}, status=200)

class PaintingViewSet(viewsets.ModelViewSet):
    queryset = Painting.objects.all()
    serializer_class = PaintingSerializer
    permission_classes = [IsAuthenticated]


class DrawingViewSet(viewsets.ModelViewSet):
    queryset = DrawingArtwork.objects.all()
    serializer_class = DrawingArtworkSerializer
    permission_classes = [IsAuthenticated]

class ArtGalleryViewSet(viewsets.ModelViewSet):
    queryset = ArtGallery.objects.all()
    serializer_class = ArtGallerySerializer
    permission_classes = [IsAuthenticated]

class ArtCategoryViewSet(viewsets.ModelViewSet):
    queryset = ArtCategory.objects.all()
    serializer_class = ArtCategorySerializer
    permission_classes = [IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

class ConceptualMixedMediaViewSet(viewsets.ModelViewSet):
    queryset = ConceptualMixedMedia.objects.all()
    serializer_class = ConceptualMixedMediaSerializer
    permission_classes = [IsAuthenticated]

class FashionArtViewSet(viewsets.ModelViewSet):
    queryset = FashionArt.objects.all()
    serializer_class = FashionArtSerializer
    permission_classes = [IsAuthenticated]

class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

class CinematographyGalleryViewSet(viewsets.ModelViewSet):
    queryset = CinematographyGallery.objects.all()
    serializer_class = CinematographyGallerySerializer
    permission_classes = [IsAuthenticated]

class FineArtViewSet(viewsets.ModelViewSet):
    queryset = FineArt.objects.all()
    serializer_class = FineArtSerializer
    permission_classes = [IsAuthenticated]

class EthereumTransactionViewSet(viewsets.ModelViewSet):
    queryset = EthereumTransaction.objects.all()
    serializer_class = EthereumTransactionSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
def artist_signup(request):
    if request.method == 'POST':
        # Get data from request
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        bio = request.data.get('bio', '')
        category = request.data.get('category', 'upcoming')
        profile_picture = request.FILES.get('profile_picture')

        # Create the User
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            artist = Artist.objects.create(user=user, bio=bio, category=category, profile_picture=profile_picture)
            artist.save()

            # Serialize and send response
            artist_data = ArtistSerializer(artist)
            return Response({'artist': artist_data.data, 'message': 'Account created successfully!'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PhotographyContentViewSet(viewsets.ModelViewSet):
    queryset = PhotographyContent.objects.all()
    serializer_class = PhotographyContentSerializer
    permission_classes = [IsAuthenticated]

class AestheticMomentViewSet(viewsets.ModelViewSet):
    queryset = AestheticMoment.objects.all()
    serializer_class = AestheticMomentSerializer
    permission_classes = [IsAuthenticated]

class ArtworkViewSet(viewsets.ModelViewSet):
    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer
    permission_classes = [IsAuthenticated]

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "message": "Login successful"})
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class ArtistLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            return Response({"message": "Login successful"})
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class ArtworkListAPIView(ListAPIView):
    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer


@api_view(['GET'])
def artist_profile(request, artist_id):
    try:
        # Get the artist object using artist_id
        artist = Artist.objects.get(id=artist_id)
        # Serialize the artist data
        artist_data = ArtistSerializer(artist)
        return Response(artist_data.data, status=status.HTTP_200_OK)
    except Artist.DoesNotExist:
        return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def create_post(request):
    if 'title' not in request.data or 'content' not in request.data:
        return Response({"error": "Title and content are required"}, status=status.HTTP_400_BAD_REQUEST)

    title = request.data['title']
    content = request.data['content']
    author = request.user  # Assuming the user is logged in

    # Prepare post data
    post = Post.objects.create(title=title, content=content, author=author)
    post.save()

    # Upload to NFT Storage
    try:
        # Data to be uploaded
        nft_data = {
            "title": title,
            "content": content,
            "author": str(author.id),  # Example: User ID as part of the metadata
        }

        # Make a POST request to NFT Storage API
        response = requests.post(
            NFT_STORAGE_API_URL,
            headers={'Authorization': f'Bearer {NFT_STORAGE_API_KEY}'},
            files={
                'file': ('post_metadata.json', str(nft_data), 'application/json'),
            },
        )

        # Check if the response was successful
        if response.status_code == 200:
            nft_data = response.json()
            post.nft_storage_url = nft_data.get('url')  # Save the NFT URL in your post model
            post.save()
            nft_url = nft_data.get('url')
        else:
            return Response({"error": "Failed to upload to NFT storage"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Serialize and return the post data with the NFT URL
    post_data = PostSerializer(post)
    return Response({"post": post_data.data, "nft_url": nft_url}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return Response({"message": "Post deleted"}, status=status.HTTP_204_NO_CONTENT)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def flower_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user in post.flowers.all():
        post.flowers.remove(request.user)
        return Response({"message": "Flower removed from post"}, status=status.HTTP_200_OK)
    else:
        post.flowers.add(request.user)
        return Response({"message": "Flower added to post"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_artwork(request, artwork_id):
    try:
        artwork = Artwork.objects.get(id=artwork_id)

        if artwork.is_sold:
            return Response({'detail': 'Artwork is already sold.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get MetaMask transaction hash and contract address
        metamask_tx = request.data.get('metamask_tx')
        contract_address = request.data.get('contract_address')

        if not metamask_tx or not contract_address:
            return Response({'detail': 'Metamask transaction or contract address missing.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate tx here (optional)

        # Mark as pending/sold
        artwork.buyer = request.user
        artwork.contract_address = contract_address  # Ensure Artwork model has this field
        artwork.save()

        # Create or fetch conversation
        conversation, created = Conversation.objects.get_or_create(
            artwork=artwork,
            buyer=request.user,
            seller=artwork.creator
        )

        return Response({
            'detail': 'Purchase initiated. Conversation started for negotiation.',
            'conversation_id': conversation.id,
            'contract_address': contract_address
        }, status=status.HTTP_200_OK)

    except Artwork.DoesNotExist:
        return Response({'detail': 'Artwork not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def process_payment(request, artwork_id, price):
    # Get the current ETH price in USD from CoinGecko
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
        eth_price = response.json().get('ethereum', {}).get('usd')

        if not eth_price:
            return Response({'detail': 'Could not fetch ETH price.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Calculate the equivalent amount of ETH for the given USD price
        eth_amount = price / eth_price

        # Example: Returning the calculation with the artwork price and ETH amount
        return Response({
            'detail': 'Price Calculation',
            'usd_price': price,
            'eth_price': eth_price,
            'eth_amount': eth_amount
        }, status=status.HTTP_200_OK)

    except requests.exceptions.RequestException as e:
        return Response({'detail': f'Error fetching price data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Pagination class
class CustomPagination(PageNumberPagination):
    page_size = 10  # You can change this to control how many results per page
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
def search(request):
    query = request.GET.get('q', '')
    if not query:
        return Response({'detail': 'Search query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a Q object for the search term
    search_query = Q(title__icontains=query) | Q(creator__username__icontains=query)  # Searching artworks by title and users by username

    # Filter the results using the Q object and apply pagination
    artworks = Artwork.objects.filter(search_query)
    users = User.objects.filter(username__icontains=query)

    # Paginate the results
    paginator = CustomPagination()
    artwork_page = paginator.paginate_queryset(artworks, request)
    user_page = paginator.paginate_queryset(users, request)

    # Format the response
    result = {
        'artworks': [
            {'id': artwork.id, 'title': artwork.title, 'creator': artwork.creator.username}
            for artwork in artwork_page
        ],
        'users': [
            {'id': user.id, 'username': user.username}
            for user in user_page
        ]
    }

    # Return the paginated results
    return paginator.get_paginated_response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def artist_dashboard(request):
    try:
        # Assuming the request user is the artist
        artist = request.user

        # Retrieve artworks created by the artist
        artworks = Artwork.objects.filter(creator=artist)

        # Example: Count the number of artworks sold
        sold_artworks_count = artworks.filter(is_sold=True).count()

        # Example: Count the number of artworks created
        total_artworks_count = artworks.count()

        # Example: Get the total earnings (assuming `price` field exists in Artwork)
        total_earnings = sum(artwork.price for artwork in artworks.filter(is_sold=True))

        # Return a JSON response with relevant data for the artist's dashboard
        data = {
            'total_artworks': total_artworks_count,
            'sold_artworks': sold_artworks_count,
            'total_earnings': total_earnings,
            'artworks': [
                {'id': artwork.id, 'title': artwork.title, 'price': artwork.price, 'is_sold': artwork.is_sold}
                for artwork in artworks
            ]
        }

        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    try:
        # Get feedback content and optional rating from the request
        content = request.data.get('content')
        rating = request.data.get('rating', None)

        if not content:
            return Response({'detail': 'Content is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new Feedback entry
        feedback = Feedback.objects.create(
            user=request.user,
            content=content,
            rating=rating if rating is not None else 0  # Default rating if not provided
        )

        return Response({'detail': 'Feedback submitted successfully.'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe(request, plan_id):
    try:
        # Get the exhibition plan based on the ID
        plan = ExhibitionPlan.objects.get(id=plan_id)

        # Calculate the end date of the subscription
        end_date = timezone.now() + timedelta(days=plan.duration_days)

        # Create the subscription record for the user
        subscription = UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            end_date=end_date,
            is_active=True
        )

        # Return the subscription details as a response
        return Response({
            'detail': 'Successfully subscribed to the exhibition plan.',
            'plan': {
                'name': plan.name,
                'description': plan.description,
                'price': plan.price,
                'duration': plan.duration_days,
                'start_date': timezone.now(),
                'end_date': end_date
            }
        }, status=status.HTTP_201_CREATED)

    except ExhibitionPlan.DoesNotExist:
        return Response({'detail': 'Exhibition plan not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_page(request):
    # Get the current user
    user = request.user

    # Fetch the user's Ethereum address (you may store this in your User model or related model)
    ethereum_address = user.profile.ethereum_address  # Assuming you store this in the profile

    if not ethereum_address:
        return Response({'detail': 'Ethereum address not found for the user.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the wallet balance (in Wei, convert to Ether)
        balance_wei = w3.eth.get_balance(ethereum_address)
        balance_ether = w3.fromWei(balance_wei, 'ether')

        return Response({
            'ethereum_address': ethereum_address,
            'balance': balance_ether
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def home(request):
    return Response({
        "message": "Welcome to Controlled Motives Home",
        "status": "success"
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def about_page(request):
    return Response({
        "platform": "Controlled Motives",
        "description": "Controlled Motives is a platform with revlutionary technology for artist to sell there artworks",
        "features": [
            "1/1 Artworks",
            "Flowers instead of likes",
            "Artist negotiation system",
            "Web3 Payments (Ethereum)",
            "Exhibition Subscriptions"
        ]
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return Response({'detail': 'All notifications marked as read.'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return Response({'detail': 'All notifications deleted.'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        return Response({'detail': 'Notification deleted.'}, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({'detail': 'Notification not found.'}, status=status.HTTP_404_NOT_FOUND)