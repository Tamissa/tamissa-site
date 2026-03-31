import csv
import os
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.management.base import BaseCommand
from gallery.models import Artwork


class Command(BaseCommand):
    help = "Import artworks from CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **options):
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
                size = (row.get("Size") or "").strip()
                price_raw = (row.get("Price") or "").strip()
                description = (row.get("Description") or "").strip()
                image_file = (row.get("Image File") or "").strip()

                if not title:
                    self.stdout.write(self.style.WARNING(f"Row {row_num}: missing Name, skipped"))
                    skipped_count += 1
                    continue

                price = Decimal("0.00")
                if price_raw:
                    try:
                        cleaned = price_raw.replace("€", "").replace(",", ".").strip()
                        price = Decimal(cleaned)
                    except InvalidOperation:
                        self.stdout.write(
                            self.style.WARNING(f"Row {row_num}: invalid price '{price_raw}', using 0.00")
                        )

                artwork, created = Artwork.objects.get_or_create(
                    title=title,
                    defaults={
                        "size": size,
                        "price": price,
                        "description": description,
                    },
                )

                if not created:
                    self.stdout.write(self.style.WARNING(f"Row {row_num}: '{title}' already exists, skipped"))
                    skipped_count += 1
                    continue

                if image_file:
                    image_path = os.path.join(settings.MEDIA_ROOT, "artworks", image_file)
                    if os.path.exists(image_path):
                        artwork.image.name = f"artworks/{image_file}"
                        artwork.save()
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"Row {row_num}: image not found -> media/artworks/{image_file}")
                        )

                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Row {row_num}: imported '{title}'"))

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created: {created_count}, Skipped: {skipped_count}"
        ))