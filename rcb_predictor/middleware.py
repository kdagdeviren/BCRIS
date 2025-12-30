"""
BCRIS - Site Giriş Şifresi Middleware
Basit bir şifre ile site erişimini kontrol eder.
"""

from django.shortcuts import render, redirect
from django.urls import reverse


class SitePasswordMiddleware:
    """
    Site girişinde basit şifre kontrolü yapar.
    Şifre doğru girildiğinde session'a kaydedilir.
    """
    
    # Basit şifre - değiştirmek için buraya bakın
    SITE_PASSWORD = '123'
    
    # Şifre gerektirmeyen URL'ler (admin, static, media)
    EXEMPT_URLS = [
        '/admin/',
        '/static/',
        '/media/',
        '/site-login/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Şifre gerektirmeyen URL'leri kontrol et
        path = request.path
        for exempt_url in self.EXEMPT_URLS:
            if path.startswith(exempt_url):
                return self.get_response(request)
        
        # Session'da şifre doğrulanmış mı kontrol et
        if request.session.get('site_authenticated', False):
            return self.get_response(request)
        
        # Şifre giriş sayfasına yönlendir
        if path != '/site-login/':
            return redirect('/site-login/')
        
        return self.get_response(request)
