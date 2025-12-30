from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, db_index=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField()
    stock = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(999999)],
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Generate slug if missing
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Ensure unique slug
            Model = self.__class__
            while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
