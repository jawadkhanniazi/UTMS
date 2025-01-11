from django.db import models
from account.models import UserProfile,Owners
from django.contrib.postgres.fields import ArrayField

class Membership(models.Model):
    membership_status_choices = (
        ('Active', 'Active'),
        # ('Inactive', 'Inactive'),
        ('Cancelled', 'Cancelled'),
        ('Adjustment', 'Adjustment'),
    )
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    Owner = models.ForeignKey(Owners, on_delete=models.SET_NULL, null=True, blank=True)
    bookingDate = models.DateField(auto_now=True)
    membershipStatus = models.CharField(max_length=50)
    allotmentDate = models.DateField(null=True, blank=True)
    membershipType = models.CharField(max_length=50)
    bookingPhase = models.CharField(max_length=50, null=True, blank=True)
    endDate = models.DateField(null=True, blank=True)
    bookingAgency = models.CharField(max_length=50, null=True, blank=True)
    isVerified = models.BooleanField(default=False)
    isConstructed = models.BooleanField(default=False)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)






class Plot(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    plotNumber = models.CharField(max_length=50)
    plotStreet = models.CharField(max_length=50)
    plotBlock = models.CharField(max_length=50)
    plotSize = models.CharField(max_length=50)
    plotCategory = models.CharField(max_length=50)
    extraFeatures = models.TextField(null=True, blank=True)
    plotSurronding = ArrayField(models.CharField(max_length=50), null=True, blank=True)
    extraLand = models.CharField(max_length=50, null=True, blank=True)
    is_possession = models.BooleanField(default=False)

    # def __str__(self):
    #     return str(self.membership.id) + "-" + self.plotNumber


class Remarks(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    remarks = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)

    # def __str__(self):
    #     return str(self.plot.id) + "-" + self.remarks
    

class MembershipAttachment(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='attachments/')
    createdAt = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)

    # def __str__(self):
    #     return str(self.plot.id) + "-" + self.attachment.name

class UserAttachment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='attachments/')
    createdAt = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)

    # def __str__(self):
    #     return self.user.user.name + "-" + self.attachment.name

    