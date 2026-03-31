from django.shortcuts import render, get_object_or_404
from .models import Artwork


def home(request):
    """
    Main gallery page — shows all artworks, no cart or purchase logic.
    """
    artworks = Artwork.objects.all().order_by('-created_at')
    return render(request, 'gallery/gallery_list.html', {
        'artworks': artworks,
    })


def artwork_detail(request, slug):
    """
    Individual artwork detail page — purely informational, no add-to-cart.
    """
    artwork = get_object_or_404(Artwork, slug=slug)

    # Related pieces: same type, exclude current
    related = Artwork.objects.filter(
        artwork_type=artwork.artwork_type
    ).exclude(pk=artwork.pk).order_by('-created_at')[:4]

    return render(request, 'gallery/artwork_detail.html', {
        'artwork': artwork,
        'related': related,
    })


def contact(request):
    """
    Contact page.
    """
    return render(request, 'gallery/contact.html')
