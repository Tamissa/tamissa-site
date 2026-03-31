# Import the render shortcut to return HTML pages
from django.shortcuts import render

# Import Artwork so the homepage can show featured pieces
from gallery.models import Artwork


def home(request):
    """
    Homepage for the Tamissa brand.
    Shows a curated set of featured artworks.
    """

    # Get up to 4 artworks marked as featured
    # Only show artworks that are visible to the public
    featured_artworks = list(
        Artwork.objects.filter(is_featured=True)
        .exclude(status="draft")
        .order_by("-created_at")[:4]
    )

    # Attach a main image URL to each artwork
    for art in featured_artworks:
        main_img = art.images.filter(is_main=True).first()

        if main_img is None:
            main_img = art.images.first()

        art.main_image_url = main_img.image.url if main_img else None

    return render(request, "core/home.html", {
        "featured_artworks": featured_artworks,
    })