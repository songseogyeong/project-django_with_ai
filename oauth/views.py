from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from member.models import Member
from member.serializers import MemberSerializer


class OAuthLoginView(View):
    # oauth 2.0과 django-allauth를 활용한 SNS(google, kakao, naver) 연동 로그인/회원가입 view입니다.
    # 각 sns api마다 redirect url에 작성한 '.../oauth/login'이 호출되었을 때 이 view가 호출됩니다.
    def get(self, request):
        # django-allauth에서 제공하는 SocialAccount 클래스에서 get()을 통해 request.user와 일치하는 객체를 조회합니다.
        user = SocialAccount.objects.get(user=request.user)

        # provider는 google, kakao, naver 중 1개이며 user객체의 provider 필드에 담겨있습니다.
        provider = user.provider

        # user객체의 extra_data 필드값을 data 변수에 담아줍니다.
        data = user.extra_data

        # kakao의 경우 데이터의 구조가 다르므로 따로 처리하여 이메일과 닉네임을 추출합니다.
        if provider == 'kakao':
            member_email = data['kakao_account']['email']
            member_name = data['properties']['nickname']
        # 나머지 google, naver의 경우 바로 이메일과 닉네임을 추출합니다.
        else:
            member_email = data['email']
            member_name = data['name']

        # 아래 주석처리한 부분은 이미 가입한 계정과 동일한 이메일이지만 다른 provider(SNS)로 로그인을 시도하였을 때
        # auth_user 테이블에서 중복이 발생하여 자동으로 django에서 sign up 페이지로 redirect하는 현상을 방지하기 위해
        # User.objects (auth_user 테이블에 접근)의 filter로 해당 이메일의 정보를 지우는 코드였으나,
        # auth_user 테이블을 건드리지 않는 방향으로 기획이 변경되어 주석처리하게 되었습니다.

        # user = User.objects.filter(email=member_email)
        # if user.exists():
        #     user.first().delete()

        # 앞서 추출한 provider(SNS종류)와 사용자의 이메일 주소, 그리고 이름을 data 딕셔너리에 담아줍니다.
        data = {
            'member_type': provider,
            'member_email': member_email,
            'member_nickname': member_name
        }

        # tbl_member 테이블에 해당 데이터에 맞는 정보가 없다면 최초 연동이므로 회원가입 페이지로 redirect합니다.
        if not Member.enabled_objects.filter(**data).exists():
            return redirect(f'/member/join?type={provider}&email={member_email}&name={member_name}')

        # 그렇지 않다면 일치하는 Member 객체를 조회합니다.
        member = Member.enabled_objects.filter(**data)

        # 해당 객체를 직렬화하여 세션에 'member' 키값으로 담아줍니다.
        request.session['member'] = MemberSerializer(member.first()).data

        # redirect할 경로를 "/"로 초기화합니다.
        path = "/"

        # 세션에서 로그인 화면으로 오기 직전 경로를 가져옵니다.
        previous_uri = request.session.get('previous_uri')

        # 직전 경로가 None이 아니라면 path 변수에 해당 경로를 담아준 후 세션에서 지워줍니다.
        if previous_uri is not None:
            path = previous_uri
            del request.session['previous_uri']

        # 앞서 처리해둔 path로 일괄처리를 통해 redirect합니다.
        return redirect(path)

