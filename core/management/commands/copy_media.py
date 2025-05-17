from django.core.management.base import BaseCommand
import shutil
import os

class Command(BaseCommand):
    help = 'Copies initial media files into /media/'

    def handle(self, *args, **kwargs):
        src = os.path.join(os.path.dirname(__file__), '../../../../static_init_media/artworks')
        dest = '/media/artworks'
        os.makedirs(dest, exist_ok=True)
        for filename in os.listdir(src):
            shutil.copy(os.path.join(src, filename), os.path.join(dest, filename))
        self.stdout.write(self.style.SUCCESS('Media copied to /media/'))
