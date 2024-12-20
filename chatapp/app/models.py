from django.db import models
from django.conf import settings



class Details(models.Model):
    email = models.EmailField(unique=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
