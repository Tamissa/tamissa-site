from django.contrib import admin
from .models import Artwork, ArtworkImage


class ArtworkImageInline(admin.TabularInline):
    model = ArtworkImage
    extra = 1
    fields = ("image", "alt_text", "is_main", "sort_order")
    ordering = ("sort_order",)


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ("title", "artwork_type", "status", "is_collaboration", "created_at")
    list_filter = ("artwork_type", "status", "is_collaboration")
    search_fields = ("title", "description", "materials")
    prepopulated_fields = {"slug": ("title",)}

    fields = (
        "title",
        "slug",
        "artwork_type",
        "description",
        "materials",
        "width_cm",
        "height_cm",
        "depth_cm",
        "diameter_cm",
        "is_collaboration",
        "status",
    )

    inlines = [ArtworkImageInline]