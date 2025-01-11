from rest_framework import serializers
from membership.models import Membership, Plot, Remarks, MembershipAttachment, UserAttachment
from account.serializers import OwnerSerializer

class MembershipAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipAttachment
        fields = '__all__'

class UserAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAttachment
        fields = '__all__'

class MembershipSerializer(serializers.ModelSerializer):
    membershipId = serializers.IntegerField(source='id', read_only=True)
    Owner = OwnerSerializer()
    class Meta:
        model = Membership
        exclude = ['id',]


class PlotSerializer(serializers.ModelSerializer):
    plotId = serializers.IntegerField(source='id', read_only=True)
    membership = MembershipSerializer()
    creatorDatails = serializers.SerializerMethodField()
    membershipAttachments = serializers.SerializerMethodField()
    remarks = serializers.SerializerMethodField()

    class Meta:
        model = Plot
        exclude = ['id']

    def get_creatorDatails(self, obj):
        data = {}
        data['name'] = obj.membership.user.user.name
        data['email'] = obj.membership.user.user.email
        if obj.membership.user.profilePic:
            data['profilePic'] = obj.membership.user.profilePic.url
        else:
            data['profilePic'] = None
        
        return data

    def get_membershipAttachments(self, obj):
        data = []
        attachments = MembershipAttachment.objects.filter(membership=obj.membership)
        for attachment in attachments:
            data.append({
                'attachmentId': attachment.id,
                'attachment': attachment.attachment.url,
                'remarks': attachment.remarks,
                'createdAt': attachment.createdAt,
                'addedByUserDetails': {
                    'name': attachment.user.user.name,
                    'email': attachment.user.user.email,
                    'profilePic': attachment.user.profilePic.url if attachment.user.profilePic else None
                }
            })
        return data
    
    def get_remarks(self, obj):
        data = []
        remarks = Remarks.objects.filter(membership=obj.membership)
        for remark in remarks:
            data.append({
                'remarkId': remark.id,
                'remark': remark.remarks,
                'createdAt': remark.createdAt,
                'addedByuserDetails': {
                    'name': remark.user.user.name,
                    'email': remark.user.user.email,
                    'profilePic': remark.user.profilePic.url if remark.user.profilePic else None
                }
            })
        return data

class RemarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remarks
        fields = '__all__'