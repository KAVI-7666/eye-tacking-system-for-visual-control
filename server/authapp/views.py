from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(["POST"])
def signup_user(request):
    username = request.data.get("username")
    password = request.data.get("password")
    name = request.data.get("name")

    if not username or not password or not name:
        return Response(
            {"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username, password=password, first_name=name
    )
    token = Token.objects.create(user=user)
    return Response({"message": "User created", "token": token.key})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        # Delete the token to log the user out
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully."})
    except:
        return Response({"error": "Logout failed."}, status=400)
