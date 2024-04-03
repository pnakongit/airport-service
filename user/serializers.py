from django.contrib.auth import get_user_model
from django.core import exceptions
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "first_name", "last_name")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"}
            }
        }
        required_fields = ("email", "password")

    def validate_password(self, value: str) -> str:
        user = self.instance
        errors = []

        try:
            validate_password(password=value, user=user)

        except exceptions.ValidationError as e:
            errors = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return value

    def create(self, validated_data) -> User:
        return get_user_model().objects.create_user(
            **validated_data
        )

    def update(self, instance, validated_data) -> User:
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
