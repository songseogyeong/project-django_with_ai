from django.shortcuts import render
from django.views import View


class ServiceTermsWebView(View):
    # 서비스 이용약관 페이지로 이동하는 view입니다.
    def get(self, request):
        return render(request, 'terms/web/service-terms-web.html')


class RefundTermsWebView(View):
    # 취소 및 환불 약관 페이지로 이동하는 view입니다.
    def get(self, request):
        return render(request, 'terms/web/refund-terms-web.html')


class PrivacyTermsWebView(View):
    # 개인정보처리방침 페이지로 이동하는 view입니다.
    def get(self, request):
        return render(request, 'terms/web/privacyprovision-web.html')


class MarketingTermsWebView(View):
    # 마케팅 정보 수신동의 페이지로 이동하는 view입니다.
    def get(self, request):
        return render(request, 'terms/web/marketing-terms-web.html')


class InformationTermsWebView(View):
    # 회원가입 수집·이용 동의서 페이지로 이동하는 view입니다.
    def get(self, request):
        return render(request, 'terms/web/information-web.html')


class EmailTermsWebView(View):
    # 이메일 주소 무단수집 거부 페이지로 이동하는 view입니다.
    def get(self, request):
        return render(request, 'terms/web/email-terms-web.html')


class EBankingTermsWebView(View):
    # 전자금융거래 이용약관 페이지로 이동하는 view입니다.
    def get(self, request):
        return render(request, 'terms/web/e-banking-terms-web.html')
