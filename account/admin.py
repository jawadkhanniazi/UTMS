from django.contrib import admin
from account.models import User, UserProfile, Owners


admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Owners)