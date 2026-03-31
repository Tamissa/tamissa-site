import csv
import os
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import artworks from CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **options):

        # 👇 IMPORTANT: import inside handle
        from gallery.models import Artwork, ArtworkImage

        csv_path = options["csv_path"]

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found: {csv_path}"))
            return

        created_count = 0
        skipped_count = 0

        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                title = (row.get("Name") or "").strip()
                description = (row.get("Description") or "").strip()
                size = (row.get("Size") or "").strip()
                price_raw = (row.get("Price") or "").strip()
                image_file = (row.get("Image File") or "").strip()

                if not title:
                    skipped_count += 1
                    continue

                # ---- PRICE ----
                price = Decimal("0.00")
                if price_raw:
                    try:
                        cleaned = price_raw.replace("€", "").replace(",", ".").strip()
                        price = Decimal(cleaned)
                    except InvalidOperation:
                        pass

                # ---- SIZE ----
                width = 0
                height = 0
                if "x" in size.lower():
                    try:
                        parts = size.lower().replace("cm", "").split("x")
                        width = int(parts[0].strip())
                        height = int(parts[1].strip())
                    except:
                        pass

                artwork, created = Artwork.objects.get_or_create(
                    title=title,
                    defaults={
                        "description": description,
                        "width_cm": width,
                        "height_cm": height,
                        "price_eur": price,
                        "status": "published",
                    },
                )

                if not created:
                    skipped_count += 1
                    continue

                # ---- IMAGE ----
                if image_file:
                    image_path = os.path.join(settings.MEDIA_ROOT, "artworks", image_file)

                    if os.path.exists(image_path):
                        ArtworkImage.objects.create(
                            artwork=artwork,
                            image=f"artworks/{image_file}",
                            is_main=True
                        )

                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done → Created: {created_count}, Skipped: {skipped_count}"
        ))