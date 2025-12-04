"""
BCRIS - Authentication Views
Hekim giriş, kayıt ve dashboard view'ları
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .forms import PhysicianSignUpForm, PatientDataUploadForm
from .models import Physician, PatientDataUpload, MLTrainingLog


def physician_signup(request):
    """Hekim kayıt sayfası"""
    if request.method == 'POST':
        form = PhysicianSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                'Kaydınız başarıyla oluşturuldu! Admin onayı sonrasında sisteme giriş yapabileceksiniz.'
            )
            return redirect('rcb_predictor:physician_login')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = PhysicianSignUpForm()
    
    return render(request, 'physician/signup.html', {'form': form})


def physician_login_view(request):
    """Hekim giriş sayfası"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Hekim profilini kontrol et
            try:
                physician = user.physician_profile
                
                if physician.approval_status == 'pending':
                    messages.warning(
                        request,
                        'Hesabınız henüz onaylanmadı. Lütfen admin onayını bekleyin.'
                    )
                    return redirect('rcb_predictor:physician_login')
                
                elif physician.approval_status == 'rejected':
                    messages.error(
                        request,
                        f'Hesabınız reddedildi. Sebep: {physician.rejection_reason}'
                    )
                    return redirect('rcb_predictor:physician_login')
                
                elif physician.approval_status == 'approved':
                    login(request, user)
                    messages.success(request, f'Hoş geldiniz, {physician.full_name}!')
                    return redirect('rcb_predictor:physician_dashboard')
            
            except Physician.DoesNotExist:
                messages.error(request, 'Hekim profili bulunamadı.')
                return redirect('rcb_predictor:physician_login')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
    
    return render(request, 'physician/login.html')


@login_required
def physician_logout_view(request):
    """Hekim çıkış"""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('rcb_predictor:index')


@login_required
def physician_dashboard(request):
    """Hekim dashboard"""
    try:
        physician = request.user.physician_profile
        
        # İstatistikler
        total_uploads = PatientDataUpload.objects.filter(physician=physician).count()
        pending_uploads = PatientDataUpload.objects.filter(
            physician=physician,
            processing_status='pending'
        ).count()
        processed_uploads = PatientDataUpload.objects.filter(
            physician=physician,
            processing_status__in=['processed', 'integrated']
        ).count()
        total_patients = PatientDataUpload.objects.filter(
            physician=physician
        ).aggregate(total=Count('patient_count'))['total'] or 0
        
        # Son yüklemeler
        recent_uploads = PatientDataUpload.objects.filter(
            physician=physician
        ).order_by('-uploaded_at')[:10]
        
        context = {
            'physician': physician,
            'total_uploads': total_uploads,
            'pending_uploads': pending_uploads,
            'processed_uploads': processed_uploads,
            'total_patients': total_patients,
            'recent_uploads': recent_uploads,
        }
        
        return render(request, 'physician/dashboard.html', context)
    
    except Physician.DoesNotExist:
        messages.error(request, 'Hekim profili bulunamadı.')
        return redirect('rcb_predictor:index')


@login_required
def physician_upload_data(request):
    """Hasta verisi yükleme"""
    try:
        physician = request.user.physician_profile
        
        if physician.approval_status != 'approved':
            messages.error(request, 'Veri yüklemek için hesabınızın onaylanmış olması gerekir.')
            return redirect('rcb_predictor:physician_dashboard')
        
        if request.method == 'POST':
            form = PatientDataUploadForm(request.POST, request.FILES)
            if form.is_valid():
                upload = form.save(commit=False, physician=physician)
                
                # Excel dosyasından hasta sayısını çıkar (basit kontrol)
                try:
                    import pandas as pd
                    df = pd.read_excel(upload.excel_file)
                    upload.patient_count = len(df)
                except Exception as e:
                    upload.patient_count = 0
                    messages.warning(request, f'Hasta sayısı otomatik hesaplanamadı: {str(e)}')
                
                upload.save()
                
                messages.success(
                    request,
                    f'Veri başarıyla yüklendi! ({upload.patient_count} hasta). Admin incelemesi sonrasında sisteme eklenecektir.'
                )
                return redirect('rcb_predictor:physician_dashboard')
            else:
                messages.error(request, 'Lütfen formdaki hataları düzeltin.')
        else:
            form = PatientDataUploadForm()
        
        # Önceki yüklemeler
        previous_uploads = PatientDataUpload.objects.filter(
            physician=physician
        ).order_by('-uploaded_at')[:5]
        
        context = {
            'physician': physician,
            'form': form,
            'previous_uploads': previous_uploads,
        }
        
        return render(request, 'physician/upload_data.html', context)
    
    except Physician.DoesNotExist:
        messages.error(request, 'Hekim profili bulunamadı.')
        return redirect('rcb_predictor:index')


@login_required
def physician_uploads_list(request):
    """Hekim yüklemelerini listele"""
    try:
        physician = request.user.physician_profile
        
        uploads = PatientDataUpload.objects.filter(
            physician=physician
        ).order_by('-uploaded_at')
        
        context = {
            'physician': physician,
            'uploads': uploads,
        }
        
        return render(request, 'physician/uploads_list.html', context)
    
    except Physician.DoesNotExist:
        messages.error(request, 'Hekim profili bulunamadı.')
        return redirect('rcb_predictor:index')


def thanks_page(request):
    """Teşekkür sayfası - Veri yollayan hekimleri listele"""
    # Onaylı ve veri yüklemiş hekimleri al
    physicians = Physician.objects.filter(
        approval_status='approved',
        uploads__processing_status__in=['processed', 'integrated']
    ).annotate(
        total_uploads=Count('uploads', filter=Q(uploads__processing_status__in=['processed', 'integrated'])),
        total_patients=Count('uploads__patient_count')
    ).filter(total_uploads__gt=0).distinct().order_by('-total_uploads')
    
    # ML istatistikleri
    latest_training = MLTrainingLog.objects.order_by('-training_date').first()
    
    context = {
        'physicians': physicians,
        'latest_training': latest_training,
    }
    
    return render(request, 'thanks.html', context)
