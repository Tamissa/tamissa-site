from django.contrib import admin
from django.utils.html import format_html
from .models import Artwork, ArtworkImage


class ArtworkImageInline(admin.TabularInline):
    model = ArtworkImage
    extra = 3
    fields = ("image", "image_url", "is_main", "preview")
    readonly_fields = ("preview",)
    verbose_name = "Additional image"
    verbose_name_plural = "Additional images"

    def preview(self, obj):
        src = obj.display_image
        if src:
            return format_html(
                '<img src="{}" style="height:60px;width:60px;object-fit:cover;border-radius:4px;" />',
                src
            )
        return "—"

    preview.short_description = "Preview"


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = (
        "thumbnail",
        "title",
        "artwork_type",
        "status",
        "is_featured",
        "is_collaboration",
        "created_at",
    )
    list_filter = ("artwork_type", "status", "is_featured", "is_collaboration")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "preview_image")

    inlines = [ArtworkImageInline]

    fieldsets = (
        ("Artwork", {
            "fields": ("title", "slug", "artwork_type", "description", "is_collaboration", "is_featured")
        }),
        ("Dimensions", {
            "fields": (("width_cm", "height_cm", "depth_cm"),),
            "classes": ("collapse",),
        }),
        ("Main Image", {
            "fields": ("main_image", "main_image_url", "preview_image"),
        }),
        ("Status", {
            "fields": ("status",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def thumbnail(self, obj):
        src = obj.display_image
        if src:
            return format_html(
                '<img src="{}" style="height:48px;width:48px;object-fit:cover;border-radius:4px;" />',
                src
            )
        return "—"

    thumbnail.short_description = ""

    def preview_image(self, obj):
        src = obj.display_image
        if src:
            return format_html(
                '<img src="{}" style="max-height:240px;max-width:100%;border-radius:6px;" />',
                src
            )
        return "—"

    preview_image.short_description = "Preview"