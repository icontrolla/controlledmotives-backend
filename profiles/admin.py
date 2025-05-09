from django.contrib import admin
from .models import (
    Artwork, DrawingArt,Artist, Flower, ArtType,
     AestheticMoment, Like, Notification, Rating
)



admin.site.register(Artwork)


admin.site.register(ArtType)
admin.site.register(Artist)
admin.site.register(DrawingArt)
admin.site.register(Flower)
admin.site.register(AestheticMoment)
admin.site.register(Like)
admin.site.register(Notification)
admin.site.register(Rating)



