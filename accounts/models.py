from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.urls import reverse  


# Create your models here.

def custom_validate_email(value):
        if "@gmail.com" in value: 
            return value
        elif "@yahoo.com" in value:
            return value
        else:
            raise ValidationError("This field accepts mail ids of google and yahoo only") 

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(null=True, unique=True, max_length=100, validators=[validate_email, custom_validate_email])


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)







