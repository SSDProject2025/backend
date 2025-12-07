from django.db import models
from fiordispino.core.validators import validate_genre

class Genre(models.Model):
    name = models.CharField(validators=[validate_genre])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

