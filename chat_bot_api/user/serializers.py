import re
from rest_framework import serializers
from .models import CustomUser


def validate_username(username: str) -> None:
    '''
    Private function for validating `username`. If it's empty, raise `ValidationError` exception.

    Args:
        username: username that will be validated.
    '''

    if not username:
        raise serializers.ValidationError('Username is required')
    

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
    
    if not re.search(r'[0-9]', password):
        raise serializers.ValidationError('Password must contain at least one digit.')
    
    if not re.search(r'[\W_]', password):
        raise serializers.ValidationError('Password must contain at least one special character.')
    

def validate_is_staff(is_staff: bool) -> None:
    '''
    Private function for validating `is_staff`. If has None value, raise `ValidationError` exception.

    Args:
        is_staff: boolean hole for validation.
    '''
    
    if is_staff is None:
        raise serializers.ValidationError('is_staff must be specified.')
    


class UserCreateSerializer(serializers.ModelSerializer):
    '''Class for user create validation and serialization. Extends `ModelSerializer`.'''

    class Meta:
        model = CustomUser

        fields = ['username', 'password', 'is_staff']

    def validate(self, data: dict):
        '''
        Method for validating all request necessary field to create a CustomUser.

        Args:
            data: object with user necessary data for validation.

        Return:
            data if all validations were correct.
        '''
        
        validate_username(data.get('username'))
        
        validate_password(data.get('password'))
        
        validate_is_staff(data.get('is_staff'))
        
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
            username = validated_data['username'],
            password = validated_data['password'],
            is_staff = validated_data['is_staff'],
        )
        
        return user
    

class UserListSerializer(serializers.ModelSerializer):
    '''Class for user list all users created on database. Extends `ModelSerializer`.'''

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_staff', 'is_active']


class UserReadSerializer(serializers.ModelSerializer):
    '''Class for user a data user on database. Extends `ModelSerializer`.'''

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_staff', 'is_active']


class UserUpdateSerializer(serializers.ModelSerializer):
    '''Class for user update user by it's index on database. Extends `ModelSerializer`.'''

    class Meta:
        model = CustomUser
        fields = ['username', 'is_staff']

    def validate(self, data: dict):
        '''
        Method for validating all request necessary field to opdate a CustomUser.

        Args:
            data: object with user necessary data for validation.

        Return:
            data if all validations were correct.
        '''
        
        validate_username(data.get('username'))
        
        validate_is_staff(data.get('is_staff'))
        
        return data