from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from ..models import User, UserProfile

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    is_mfa_enabled = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 
                 'is_active', 'is_staff', 'date_joined', 'last_login', 
                 'updated_at', 'mfa_enrolled', 'is_mfa_enabled', 'profile', 'groups']
        read_only_fields = ['id', 'date_joined', 'last_login', 'updated_at', 'is_staff', 'is_active']
    
    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return {
                'phone_number': obj.profile.phone_number,
                'bio': getattr(obj.profile, 'bio', ''),
                'avatar': getattr(obj.profile, 'avatar', None),
            }
        return {'phone_number': '', 'bio': '', 'avatar': None}
    
    def get_groups(self, obj):
        return list(obj.groups.values_list('name', flat=True))
    
    def get_is_mfa_enabled(self, obj):
        return obj.mfa_enrolled


class UserProfileSerializer(serializers.ModelSerializer):
    """Enhanced serializer for user profile updates with comprehensive validation"""
    phone = serializers.CharField(
        source='profile.phone_number', 
        max_length=20, 
        required=False, 
        allow_blank=True
    )
    bio = serializers.CharField(
        source='profile.bio',
        max_length=500,
        required=False,
        allow_blank=True
    )
    avatar = serializers.ImageField(
        source='profile.avatar',
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'bio', 'avatar']
        
    def validate_email(self, value):
        user = self.instance
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_phone(self, value):
        if value and len(value) > 0:
            # Basic phone number validation
            import re
            phone_pattern = re.compile(r'^[\+]?[1-9][\d]{0,15}$')
            if not phone_pattern.match(value.replace(' ', '').replace('-', '')):
                raise serializers.ValidationError("Enter a valid phone number.")
        return value
    
    def validate_first_name(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("First name is required.")
        if len(value) > 150:
            raise serializers.ValidationError("First name must be less than 150 characters.")
        return value.strip()
    
    def validate_last_name(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("Last name is required.")
        if len(value) > 150:
            raise serializers.ValidationError("Last name must be less than 150 characters.")
        return value.strip()
    
    def update(self, instance, validated_data):
        # Handle profile data separately
        profile_data = validated_data.pop('profile', {})
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create profile
        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False, required=False)
    
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
            # Note: removed is_locked check as it may not exist in the User model
            
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


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation using token"""
    token = serializers.CharField(max_length=255)
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        
        # Validate token
        from ..models import PasswordResetToken
        try:
            token_obj = PasswordResetToken.objects.get(token=attrs['token'])
            if not token_obj.is_valid():
                raise serializers.ValidationError({"token": "Token is expired or already used."})
            attrs['token_obj'] = token_obj
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid token."})
        
        return attrs
