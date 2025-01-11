from django.db import models
from membership.models import Membership, Plot, Remarks, MembershipAttachment, UserAttachment

from account.models import UserProfile, Owners



class Payment(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    Owners = models.ForeignKey(Owners, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paymentMethod = models.CharField(max_length=50)
    paymentDate = models.DateTimeField()
    paymentReceipt = models.FileField(upload_to='payment/')
    paymentStatus = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    receviedBy = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.membership.id) + "-" + self.amount

