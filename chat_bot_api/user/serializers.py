import re
from rest_framework import serializers
from .models import CustomUser


def validate_name_email(first_name: str, last_name: str, email: str) -> None:
    '''
    Private function for validating `username` and `email`. If one it's empty, raise `ValidationError` exception.

    Args:
        username: username that will be validated;
        email: email that will be validated.
    '''

    if not first_name:
        raise serializers.ValidationError('First name is required')
    
    if not last_name:
        raise serializers.ValidationError('Last name is required')
    
    if not email:
        raise serializers.ValidationError('Email is required')
    

def validate_password(password: str) -> None:
    '''
    Private function for validating `password`. If it's empty or less than 8 characters, raise `ValidationError` exception.

    Args:
        password: password that will be validated.
    '''

    if not password:
        raise serializers.ValidationError('Password is required.')
    
    if len(password) < 8:
        raise serializers.ValidationError('Password must be at least 8 characters long.')

    if not re.search(r'[A-Z]', password):
        raise serializers.ValidationError('Password must contain at least one uppercase letter.')
    
    if not re.search(r'[a-z]', password):
        raise serializers.ValidationError('Password must contain at least one lowercase letter.')
    
    if not re.search(r'\d', password):
        raise serializers.ValidationError('Password must contain at least one digit.')
    
    if not re.search(r'[\W_]', password):
        raise serializers.ValidationError('Password must contain at least one special character.')
    


class UserCreateSerializer(serializers.ModelSerializer):
    '''Class for user create validation and serialization. Extends `ModelSerializer`.'''

    class Meta:
        model = CustomUser
        
        fields = ['first_name', 'last_name', 'email', 'password']
        
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data: dict):
        '''
        Method for validating all request necessary field to create a CustomUser.

        Args:
            data: object with user necessary data for validation.

        Return:
            data if all validations were correct.
        '''
        
        validate_name_email(data.get('first_name'), data.get('last_name'), data.get('email'))
        
        validate_password(data.get('password'))
        
        return data
    
    def create(self, validated_data: dict) -> CustomUser:
        '''
        Create a user with hashed password.

        Args:
            validated_data: validating data for inserting on database

        Return:
            CustomUser from validated_data.
        '''
        
        user = CustomUser.objects.create_user(
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            email = validated_data['email'],
            password = validated_data['password'],
        )
        
        return user
    

class UserListSerializer(serializers.ModelSerializer):
    '''Class for user list all users created on database. Extends `ModelSerializer`.'''

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email']


class UserReadSerializer(serializers.ModelSerializer):
    '''Class for user a data user on database. Extends `ModelSerializer`.'''

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email']


class UserUpdateSerializer(serializers.ModelSerializer):
    '''Class for user update user by it's index on database. Extends `ModelSerializer`.'''

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
        }

    def validate(self, data: dict):
        '''
        Method for validating all request necessary field to opdate a CustomUser.

        Args:
            data: object with user necessary data for validation.

        Return:
            data if all validations were correct.
        '''
        
        validate_name_email(data.get('first_name'), data.get('last_name'), data.get('email'))
        
        return data