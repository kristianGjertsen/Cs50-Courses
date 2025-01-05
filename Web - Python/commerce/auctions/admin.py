from django.contrib import admin
from .models import *

# Register your models here.


class AdminListing(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # Check if the object exists (editing mode)
        if obj:  # This means we are editing
            return fields  # Return all fields
        else:  # This means we are creating
            # Exclude the field you want to hide
            fields.remove("user_bid")
            fields.remove("num_bid")
            fields.remove("bidders")
            return fields


admin.site.register(Listings, AdminListing)
admin.site.register(User)
admin.site.register(Watchlist)
admin.site.register(Comments)
