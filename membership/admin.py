from django.contrib import admin

# Register your models here.
from membership.models import Membership, Plot, Remarks, MembershipAttachment, UserAttachment

admin.site.register(Membership)
admin.site.register(Plot)
admin.site.register(Remarks)
admin.site.register(MembershipAttachment)
admin.site.register(UserAttachment)