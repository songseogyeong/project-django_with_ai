from django.db import transaction
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from member.models import Member
from pay.models import Pay
from pay.serializers import PaySerializer


class PayCreateAPI(APIView):
    # Bootpay api를 활용하여 결제가 완료된 후 fetch를 통해 요청하는 REST API입니다.
    @transaction.atomic
    def get(self, request):
        # 결제한 사용자의 id를 쿼리스트링으로 받아옵니다.
        member_id = request.GET['memberId']

        # 추후 결제 취소 요청을 위한 receipt_id(영수증 id)를 쿼리스트링으로 받아옵니다.
        receipt_id = request.GET['receiptId']

        # 해당 id에 맞는 사용자를 조회합니다.
        member = Member.enabled_objects.filter(id=member_id)

        # 사용자가 존재한다면 아래 if문으로 진입합니다.
        if member.exists():
            # first()를 통해 조회한 사용자의 객체를 가져온 후 영수증 id와 함께 결제 정보를 insert합니다.
            pay = Pay.objects.create(member=member.first(), receipt_id=receipt_id)
            # 결제 객체를 직렬화합니다.
            pay = PaySerializer(pay).data
            # 직렬화된 결제 객체를 딕셔너리에 담아 Response로 응답합니다.
            pay = {
                'pay': pay
            }

            return Response(pay)

        # 사용자가 존재하지 않는다면 결제 테이블에 insert되지 않으므로 결제 객체 대신 None을 반환합니다.
        # 이때 반환값에 대해서는 javascript에서 판단하여 활동 개설 여부를 결정하게 됩니다.
        return None
