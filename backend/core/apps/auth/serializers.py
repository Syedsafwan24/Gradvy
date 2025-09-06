from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 
                 'is_active', 'is_staff', 'date_joined', 'last_login', 
                 'mfa_enrolled', 'profile', 'groups']
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return {
                'phone_number': obj.profile.phone_number,
            }
        return {}
    
    def get_groups(self, obj):
        return list(obj.groups.values_list('name', flat=True))


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            request = self.context.get('request')
            user = authenticate(request=request, email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('Account is disabled')
            if user.is_locked:
                raise serializers.ValidationError('Account is temporarily locked')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')

class MFAVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    
    def validate_code(self, value):
        if len(value) != 6:
            raise serializers.ValidationError('TOTP code must be 6 digits')
        return value

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect')
        return value
