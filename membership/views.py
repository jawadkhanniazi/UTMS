from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import datetime
from django.db import transaction
from rest_framework.pagination import PageNumberPagination

from membership.models import Membership, Plot, Remarks, MembershipAttachment
from account.models import UserProfile,Owners

from membership.serializers import MembershipSerializer, PlotSerializer, RemarksSerializer


class PlotPagination(PageNumberPagination):
    page_size = 5  # You can customize this if needed
    page_size_query_param = 'page_size'
    max_page_size = 100  # Optional, for limiting the max size per page


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_membership(request):
    with transaction.atomic():
        print(request.data)
        
        ## data for membership
        currentUserProfile = UserProfile.objects.get(user=request.user)
        bookingDate = datetime.datetime.now()
        allotmentDate = request.data.get('allotmentDate', None)
        endDate = request.data.get('endDate', None)
        membershipType = request.data.get('membershipType', None)
        bookingAgency = request.data.get('bookingAgency', None)
        bookingPhase = request.data.get('bookingPhase', None)
        
        ## save data in models, save those fileds which are not none
        membership = Membership.objects.create(
            bookingDate=bookingDate,
            allotmentDate=allotmentDate,
            endDate=endDate,
            membershipType=membershipType,
            bookingAgency=bookingAgency,
            bookingPhase=bookingPhase,
            user=currentUserProfile
        )

        ## data for plot
        plotNumber = request.data.get('plotNumber', None)
        plotStreet = request.data.get('plotStreet', None)
        plotBlock = request.data.get('plotBlock', None)
        plotSize = request.data.get('plotSize', None)
        plotCategory = request.data.get('plotCategory', None)
        extraFeatures = request.data.get('extraFeatures', None)
        extraLand = request.data.get('extraLand', None)
        plotSurronding = request.data.get('plotSurronding', [])
        
        ## save data in models, save those fileds which are not none
        plot = Plot.objects.create(
            membership=membership,
            plotNumber=plotNumber,
            plotStreet=plotStreet,
            plotBlock=plotBlock,
            plotSize=plotSize,
            plotCategory=plotCategory,
            extraFeatures=extraFeatures,
            extraLand=extraLand,
            plotSurronding=plotSurronding,
        )

        ##data for owner details and next of kin
        ownerName = request.data.get('ownerName', None)
        ownerCNIC = request.data.get('ownerCNIC', None)
        ownerAddress = request.data.get('ownerAddress', None)
        ownerPhone = request.data.get('ownerPhone', None)
        ownerWhatsapp = request.data.get('ownerWhatsapp', None)
        ownerEmail = request.data.get('ownerEmail', None)
        ownerPostalAddress = request.data.get('ownerPostalAddress', None)
        ownerNextOfKinName = request.data.get('ownerNextOfKinName', None)
        ownerNextOfKinCNIC = request.data.get('ownerNextOfKinCNIC', None)
        ownerNextOfKinPhone = request.data.get('ownerNextOfKinPhone', None)
        ownerNextOfKinRelation = request.data.get('ownerNextOfKinRelation', None)
        ownerNextOfKinWhatsapp = request.data.get('ownerNextOfKinWhatsapp', None)
        ownerNextOfKinEmail = request.data.get('ownerNextOfKinEmail', None)
        ownerNextOfKinAddress = request.data.get('ownerNextOfKinAddress', None)
        ownerNextOfKinPostalAddress = request.data.get('ownerNextOfKinPostalAddress', None)
        
        ## save data in models, save those fileds which are not none
        owner = Owners.objects.create(
            ownerName=ownerName,
            ownerCnic=ownerCNIC,
            ownerAddress=ownerAddress,
            ownerPhone=ownerPhone,
            ownerWhatsapp=ownerWhatsapp,
            ownerEmail=ownerEmail,
            ownerPostalAddress=ownerPostalAddress,
            ownerNextOfKin=ownerNextOfKinName,
            ownerNextOfKinCnic=ownerNextOfKinCNIC,
            ownerNextOfKinPhone=ownerNextOfKinPhone,
            ownerNextOfKinRelation=ownerNextOfKinRelation,
            ownerNextOfKinWhatsapp=ownerNextOfKinWhatsapp,
            ownerNextOfKinEmail=ownerNextOfKinEmail,
            ownerNextOfKinAddress=ownerNextOfKinAddress,
            ownerNextOfKinPostalAddress=ownerNextOfKinPostalAddress,
            
        )

        membership.Owner = owner
        membership.save()

        serializer = PlotSerializer(plot)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_membership(request):
    plots = Plot.objects.all().order_by('-id')
    
    paginator = PlotPagination()
    result_page = paginator.paginate_queryset(plots, request)
    
    serializer = PlotSerializer(result_page, many=True)
    
    # Constructing the response with pagination data
    response_data = {
        'results': serializer.data,
        'pagination_data': {
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
        },
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_membership(request, id):
    membership = Membership.objects.get(id=id)
    if membership is None:
        return Response({'message': 'Membership not found'}, status=status.HTTP_404_NOT_FOUND)
    
    print(request.data)
    ## to inactivate the membership
    if request.data.get('isActive', None) is False:
        print('inactivating')
        membership.isActive = False
        membership.save()
        return Response({'message': 'Membership inactivated successfully'}, status=status.HTTP_200_OK)
    
    return Response({'message': 'Membership updated successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_attechment(request, id):
    membership = Membership.objects.get(id=id)
    attachment = request.data.get('attachment', None)
    remarks = request.data.get('remarks', None)
    
    currentUserProfile = UserProfile.objects.get(user=request.user)
    
    attachment = MembershipAttachment.objects.create(
        membership=membership,
        attachment=attachment,
        remarks=remarks,
        user=currentUserProfile
    )
    
    return Response({'message': 'Attachment added successfully'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_single_membership(request, id):
    membership = Membership.objects.get(id=id)
    if membership:
        plot = Plot.objects.get(membership=membership)
        if plot:
            serializer = PlotSerializer(plot)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Membership not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Membership not found'}, status=status.HTTP_404_NOT_FOUND)
   

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_remarks(request, id):
    membership = Membership.objects.get(id=id)
    if membership is None:
        return Response({'message': 'Membership not found'}, status=status.HTTP_404_NOT_FOUND)
    
    remarks = request.data.get('remarks', None)
    currentUserProfile = UserProfile.objects.get(user=request.user)
    
    remarks = Remarks.objects.create(
        membership=membership,
        remarks=remarks,
        user=currentUserProfile
    )
    
    return Response({'message': 'Remarks added successfully'}, status=status.HTTP_201_CREATED)

from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_membership(request):
    search = request.query_params.get('search', None)
    if search:
        plots = Plot.objects.filter(
            Q(plotNumber__icontains=search) |
            Q(plotStreet__icontains=search) |
            Q(plotBlock__icontains=search) |
            Q(plotSize__icontains=search) |
            Q(plotCategory__icontains=search) |
            Q(extraFeatures__icontains=search) |
            Q(plotSurronding__icontains=search) |
            Q(extraLand__icontains=search)
        
            )
        serializer = PlotSerializer(plots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Please provide search parameter'}, status=status.HTTP_400_BAD_REQUEST)