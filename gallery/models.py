from django.db import models
from django.utils.text import slugify


class Artwork(models.Model):
    ARTWORK_TYPES = [
        ("painting", "Painting"),
        ("wall_decoration", "Wall Decoration"),
        ("lamp", "Lamp"),
        ("tray", "Tray"),
        ("decor_piece", "Decor Piece"),
        ("accessory", "Accessory"),
    ]

    STATUS_CHOICES = [
        ("available", "Available"),
        ("acquired", "Acquired"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    artwork_type = models.CharField(max_length=30, choices=ARTWORK_TYPES, db_index=True)
    description = models.TextField(blank=True)
    materials = models.CharField(max_length=255, blank=True)

    width_cm = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)
    depth_cm = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)
    diameter_cm = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available", db_index=True)
    is_collaboration = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Artwork"
        verbose_name_plural = "Artworks"

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
    def is_acquired(self):
        return self.status == "acquired"

    @property
    def main_image(self):
        main = self.images.filter(is_main=True).first()
        if main:
            return main.image
        first = self.images.first()
        return first.image if first else None

    @property
    def display_image(self):
        main = self.images.filter(is_main=True).first()
        if main:
            return main.image.url
        first = self.images.first()
        return first.image.url if first else ""

    @property
    def display_dimensions(self):
        parts = []

        if self.diameter_cm:
            parts.append(f"Diameter: {self.diameter_cm} cm")

        size_parts = []
        if self.width_cm:
            size_parts.append(str(self.width_cm))
        if self.height_cm:
            size_parts.append(str(self.height_cm))
        if self.depth_cm:
            size_parts.append(str(self.depth_cm))

        if size_parts:
            parts.append(" × ".join(size_parts) + " cm")

        return " | ".join(parts)


class ArtworkImage(models.Model):
    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="artworks/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Artwork image"
        verbose_name_plural = "Artwork images"

    def __str__(self):
        return f"{self.artwork.title} image"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_main:
            ArtworkImage.objects.filter(artwork=self.artwork).exclude(pk=self.pk).update(is_main=False)