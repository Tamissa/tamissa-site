# Views for the shop app
from datetime import timedelta

from django.apps import apps
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import PurchaseRequestForm
from .models import PurchaseRequest


def get_artwork_model():
    return apps.get_model("gallery", "Artwork")


def get_cart(request):
    return request.session.get("cart", {})


def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def get_main_image_url(artwork):
    main_img = artwork.images.filter(is_main=True).first()

    if main_img is None:
        main_img = artwork.images.first()

    return main_img.image.url if main_img else None


def release_expired_cart_holds(request):
    """
    Remove expired cart items from the session and return their artwork
    status back to 'published' if they were only reserved by that cart hold.
    """
    Artwork = get_artwork_model()
    cart = get_cart(request)
    now = timezone.now()

    expired_slugs = []

    for slug, item in cart.items():
        reserved_until_str = item.get("reserved_until")

        if not reserved_until_str:
            expired_slugs.append(slug)
            continue

        try:
            reserved_until = timezone.datetime.fromisoformat(reserved_until_str)
        except ValueError:
            expired_slugs.append(slug)
            continue

        if timezone.is_naive(reserved_until):
            reserved_until = timezone.make_aware(
                reserved_until,
                timezone.get_current_timezone(),
            )

        if reserved_until <= now:
            expired_slugs.append(slug)

    for slug in expired_slugs:
        artwork = Artwork.objects.filter(slug=slug).first()

        if artwork and artwork.status == "reserved":
            artwork.status = "published"
            artwork.save(update_fields=["status"])

        cart.pop(slug, None)

    save_cart(request, cart)


def add_to_cart(request, artwork_slug):
    release_expired_cart_holds(request)

    Artwork = get_artwork_model()
    artwork = Artwork.objects.filter(slug=artwork_slug).first()

    if not artwork:
        return redirect("gallery:gallery_list")

    if artwork.status != "published":
        return redirect("gallery:artwork_detail", slug=artwork.slug)

    cart = get_cart(request)

    if artwork.slug not in cart:
        reserved_until = timezone.now() + timedelta(minutes=30)

        cart[artwork.slug] = {
            "title": artwork.title,
            "reserved_until": reserved_until.isoformat(),
        }
        save_cart(request, cart)

        artwork.status = "reserved"
        artwork.save(update_fields=["status"])

    return redirect("shop:cart_detail")


def cart_detail(request):
    release_expired_cart_holds(request)

    Artwork = get_artwork_model()
    cart = get_cart(request)
    cart_items = []
    now = timezone.now()

    for slug, item in cart.items():
        artwork = Artwork.objects.filter(slug=slug).first()

        if not artwork:
            continue

        reserved_until_str = item.get("reserved_until")

        if not reserved_until_str:
            continue

        try:
            reserved_until = timezone.datetime.fromisoformat(reserved_until_str)
        except ValueError:
            continue

        if timezone.is_naive(reserved_until):
            reserved_until = timezone.make_aware(
                reserved_until,
                timezone.get_current_timezone(),
            )

        minutes_left = max(
            0,
            int((reserved_until - now).total_seconds() // 60),
        )

        cart_items.append(
            {
                "artwork": artwork,
                "artwork_image_url": get_main_image_url(artwork),
                "reserved_until": reserved_until,
                "minutes_left": minutes_left,
            }
        )

    return render(
        request,
        "shop/cart_detail.html",
        {
            "cart_items": cart_items,
        },
    )


def remove_from_cart(request, artwork_slug):
    release_expired_cart_holds(request)

    Artwork = get_artwork_model()
    cart = get_cart(request)

    if artwork_slug in cart:
        cart.pop(artwork_slug, None)
        save_cart(request, cart)

        artwork = Artwork.objects.filter(slug=artwork_slug).first()
        if artwork and artwork.status == "reserved":
            artwork.status = "published"
            artwork.save(update_fields=["status"])

    return redirect("shop:cart_detail")


def request_purchase(request, artwork_slug, artwork_title):
    release_expired_cart_holds(request)

    Artwork = get_artwork_model()
    artwork = Artwork.objects.filter(slug=artwork_slug).first()

    artwork_image_url = get_main_image_url(artwork) if artwork else None

    if request.method == "POST":
        form = PurchaseRequestForm(request.POST)

        if form.is_valid():
            PurchaseRequest.objects.create(
                artwork_slug=artwork_slug,
                artwork_title=artwork_title,
                customer_name=form.cleaned_data["customer_name"],
                customer_email=form.cleaned_data["customer_email"],
                message=form.cleaned_data["message"],
            )

            send_mail(
                subject=f"New purchase request for {artwork_title}",
                message=(
                    f"A new purchase request was submitted.\n\n"
                    f"Artwork: {artwork_title}\n"
                    f"Slug: {artwork_slug}\n\n"
                    f"Customer name: {form.cleaned_data['customer_name']}\n"
                    f"Customer email: {form.cleaned_data['customer_email']}\n\n"
                    f"Message:\n{form.cleaned_data['message']}"
                ),
                from_email=None,
                recipient_list=["your_email@gmail.com"],
                fail_silently=False,
            )

            return redirect("shop:request_purchase_success")

    else:
        form = PurchaseRequestForm()

    return render(
        request,
        "shop/request_purchase.html",
        {
            "form": form,
            "artwork_title": artwork_title,
            "artwork": artwork,
            "artwork_image_url": artwork_image_url,
        },
    )


def request_purchase_success(request):
    release_expired_cart_holds(request)
    return render(request, "shop/request_purchase_success.html")