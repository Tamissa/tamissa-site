from django.db import models
from django.utils.text import slugify


class Artwork(models.Model):
    ARTWORK_TYPES = [
        ('painting', 'Painting'),
        ('wall_decoration', 'Wall Decoration'),
        ('lamp', 'Lamp'),
        ('tray', 'Tray'),
        ('decor_piece', 'Decor Piece'),
        ('accessory', 'Accessory'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('acquired', 'Acquired'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    artwork_type = models.CharField(max_length=30, choices=ARTWORK_TYPES, db_index=True)
    description = models.TextField(blank=True)

    width_cm = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)
    depth_cm = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)

    main_image = models.ImageField(upload_to='artworks/', blank=True, null=True)
    main_image_url = models.URLField(max_length=500, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', db_index=True)
    is_collaboration = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while Artwork.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def display_image(self):
        if self.main_image_url:
            return self.main_image_url
        if self.main_image:
            return self.main_image.url
        return ""

    @property
    def is_acquired(self):
        return self.status == "acquired"


class ArtworkImage(models.Model):
    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to='artworks/')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.artwork.title} Image"