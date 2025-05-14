from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = "Set the default site domain and name"

    def handle(self, *args, **options):
        site, created = Site.objects.get_or_create(id=1)
        site.domain = "controlledmotives-backend.onrender.com"
        site.name = "Controlled Motives"
        site.save()
        if created:
            self.stdout.write(self.style.SUCCESS("Site created and set successfully!"))
        else:
            self.stdout.write(self.style.SUCCESS("Site updated successfully!"))
