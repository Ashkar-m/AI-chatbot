from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Details
import stripe
from django.conf import settings
import json

def home(request):
    return render(request,'Layout/base.html')


def details(request):
    if request.method == "POST":
        email = request.POST.get('email')

        if email:
            if Details.objects.filter(email=email).exists():
                
                return redirect('email_exists')
                

            Details.objects.create(email=email)

            return redirect('payment')
        
        else:
            return HttpResponse("Please enter a valid email address.", status=400)
   
    return render(request, 'app/details.html')

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def payment(request):
    if request.method == "POST":
        base_url = "http://127.0.0.1:8000/"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'T-shirt',
                        },
                        'unit_amount': 2000, 
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=base_url + 'success/',
            cancel_url=base_url + 'cancel/',
        )

        # return JsonResponse({
        #     'id': checkout_session.id
        # })
        return JsonResponse({'id':checkout_session.id})
    return render(request, 'app/payment.html')


# def payment(request):
#     if request.method == "POST":
#         base_url = "http://127.0.0.1:8000/"

#         try:
#             # Create a Stripe Checkout session
#             checkout_session = stripe.checkout.Session.create(
#                 payment_method_types=['card'],
#                 line_items=[{
#                     'price_data': {
#                         'currency': 'usd',
#                         'product_data': {
#                             'name': 'T-shirt',
#                         },
#                         'unit_amount': 2000,  # $20.00 in cents
#                     },
#                     'quantity': 1,
#                 }],
#                 mode='payment',
#                 success_url=base_url + 'success/',
#                 cancel_url=base_url + 'cancel/',
#             )

#             return JsonResponse({
#                 'id': checkout_session.id,
#                 'client_secret': checkout_session.client_secret  # Return the client_secret here
#             })
#             print(checkout_session)
        
#         except stripe.error.StripeError as e:
#             # Log the error to see the details
#             print(f"Stripe error: {e.user_message}")
#             return JsonResponse({'error': e.user_message}, status=400)

#     return render(request, 'app/payment.html')


def create_payment_intent(request):
    if request.method == 'POST':
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=5000,  # Amount in cents
                currency='usd',
                payment_method_types=["card"],
            )
            return JsonResponse({'client_secret': payment_intent['client_secret']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    
def success(request):
    return render(request, 'app/success.html')


def cancel(request):
    return render(request, 'app/cancel.html')


def email_exists(request):
    return render(request, 'app/email_exists.html')

class CreateChatRoom(APIView):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class = RoomSerializer

    def post(self,request,pk):
        current_user = request.user
        other_user = UserModel.objects.get(pk=pk)

        existing_chat_rooms = Room.objects.filter(members = current_user).filter(members = other_user)
        if existing_chat_rooms.exists():
            serializer = RoomSerializer(existing_chat_rooms.first())
            return Response(serializer.data,status=status.HTTP_200_OK)

        chat_room = Room()
        chat_room.save()
        chat_room.members.add(current_user,other_user)

        serializer = RoomSerializer(chat_room)
        return Response(serializer.data,status=status.HTTP_201_CREATED)