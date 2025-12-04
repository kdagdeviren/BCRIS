"""
BCRIS Hekim Sistemi Test Scripti
Bu script hekim sisteminin temel fonksiyonlarını test eder
"""

import os
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bcris_project.settings')
django.setup()

from django.contrib.auth.models import User
from rcb_predictor.models import Physician, PatientDataUpload, MLTrainingLog, MLModel
from django.utils import timezone


def test_physician_creation():
    """Hekim oluşturma testi"""
    print("\n" + "="*50)
    print("TEST 1: Hekim Oluşturma")
    print("="*50)
    
    try:
        # Test kullanıcısı oluştur
        user, created = User.objects.get_or_create(
            username='test_hekim',
            defaults={
                'email': 'test@hastane.com',
                'first_name': 'Test',
                'last_name': 'Hekim'
            }
        )
        
        if created:
            user.set_password('test123')
            user.save()
            print("✅ Test kullanıcısı oluşturuldu")
        else:
            print("ℹ️  Test kullanıcısı zaten mevcut")
        
        # Hekim profili oluştur
        physician, created = Physician.objects.get_or_create(
            user=user,
            defaults={
                'full_name': 'Dr. Test Hekim',
                'email': 'test@hastane.com',
                'phone': '+90 555 123 4567',
                'institution': 'Test Hastanesi',
                'department': 'Onkoloji',
                'title': 'Uzm. Dr.',
                'approval_status': 'pending'
            }
        )
        
        if created:
            print("✅ Hekim profili oluşturuldu")
        else:
            print("ℹ️  Hekim profili zaten mevcut")
        
        print(f"   - Ad: {physician.full_name}")
        print(f"   - Kurum: {physician.institution}")
        print(f"   - Durum: {physician.get_approval_status_display()}")
        
        return physician
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def test_physician_approval(physician):
    """Hekim onaylama testi"""
    print("\n" + "="*50)
    print("TEST 2: Hekim Onaylama")
    print("="*50)
    
    try:
        if physician.approval_status == 'pending':
            physician.approval_status = 'approved'
            physician.approval_date = timezone.now()
            physician.save()
            print("✅ Hekim onaylandı")
        else:
            print("ℹ️  Hekim zaten onaylı")
        
        print(f"   - Durum: {physician.get_approval_status_display()}")
        print(f"   - Onay Tarihi: {physician.approval_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


def test_data_upload(physician):
    """Veri yükleme testi"""
    print("\n" + "="*50)
    print("TEST 3: Veri Yükleme")
    print("="*50)
    
    try:
        # Test veri yüklemesi oluştur
        upload, created = PatientDataUpload.objects.get_or_create(
            physician=physician,
            original_filename='test_data.xlsx',
            defaults={
                'patient_count': 50,
                'description': 'Test veri seti',
                'processing_status': 'pending',
                'file_size': 1024 * 100  # 100KB
            }
        )
        
        if created:
            print("✅ Veri yüklemesi oluşturuldu")
        else:
            print("ℹ️  Veri yüklemesi zaten mevcut")
        
        print(f"   - Dosya: {upload.original_filename}")
        print(f"   - Hasta Sayısı: {upload.patient_count}")
        print(f"   - Durum: {upload.get_processing_status_display()}")
        
        return upload
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def test_data_processing(upload):
    """Veri işleme testi"""
    print("\n" + "="*50)
    print("TEST 4: Veri İşleme")
    print("="*50)
    
    try:
        # Durumları sırayla güncelle
        statuses = ['reviewing', 'processed', 'integrated']
        
        for status in statuses:
            upload.processing_status = status
            if status == 'processed':
                upload.processed_date = timezone.now()
            upload.save()
            print(f"✅ Durum güncellendi: {upload.get_processing_status_display()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


def test_statistics():
    """İstatistik testi"""
    print("\n" + "="*50)
    print("TEST 5: İstatistikler")
    print("="*50)
    
    try:
        # Hekim istatistikleri
        total_physicians = Physician.objects.count()
        approved_physicians = Physician.objects.filter(approval_status='approved').count()
        pending_physicians = Physician.objects.filter(approval_status='pending').count()
        
        print(f"📊 Hekim İstatistikleri:")
        print(f"   - Toplam: {total_physicians}")
        print(f"   - Onaylı: {approved_physicians}")
        print(f"   - Bekleyen: {pending_physicians}")
        
        # Veri istatistikleri
        total_uploads = PatientDataUpload.objects.count()
        pending_uploads = PatientDataUpload.objects.filter(processing_status='pending').count()
        processed_uploads = PatientDataUpload.objects.filter(processing_status__in=['processed', 'integrated']).count()
        
        print(f"\n📊 Veri İstatistikleri:")
        print(f"   - Toplam Yükleme: {total_uploads}")
        print(f"   - Bekleyen: {pending_uploads}")
        print(f"   - İşlenmiş: {processed_uploads}")
        
        # Hasta istatistikleri
        total_patients = sum(PatientDataUpload.objects.values_list('patient_count', flat=True))
        
        print(f"\n📊 Hasta İstatistikleri:")
        print(f"   - Toplam Hasta: {total_patients}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


def test_ml_training_log():
    """ML eğitim logu testi"""
    print("\n" + "="*50)
    print("TEST 6: ML Eğitim Logu")
    print("="*50)
    
    try:
        # Aktif model var mı kontrol et
        active_model = MLModel.objects.filter(is_active=True).first()
        
        if not active_model:
            print("⚠️  Aktif ML modeli bulunamadı")
            return False
        
        # Test eğitim logu oluştur
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            print("⚠️  Admin kullanıcısı bulunamadı")
            return False
        
        log, created = MLTrainingLog.objects.get_or_create(
            model=active_model,
            training_date=timezone.now(),
            defaults={
                'trained_by': admin_user,
                'total_patients': 1000,
                'training_patients': 800,
                'test_patients': 200,
                'accuracy': 85.5,
                'precision': 0.87,
                'recall': 0.84,
                'f1_score': 0.85,
                'notes': 'Test eğitimi'
            }
        )
        
        if created:
            print("✅ ML eğitim logu oluşturuldu")
        else:
            print("ℹ️  ML eğitim logu zaten mevcut")
        
        print(f"   - Model: {log.model.name}")
        print(f"   - Toplam Hasta: {log.total_patients}")
        print(f"   - Doğruluk: {log.accuracy}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


def run_all_tests():
    """Tüm testleri çalıştır"""
    print("\n" + "="*50)
    print("BCRIS HEKİM SİSTEMİ TEST SÜİTİ")
    print("="*50)
    
    # Test 1: Hekim oluşturma
    physician = test_physician_creation()
    if not physician:
        print("\n❌ Test başarısız: Hekim oluşturulamadı")
        return
    
    # Test 2: Hekim onaylama
    if not test_physician_approval(physician):
        print("\n❌ Test başarısız: Hekim onaylanamadı")
        return
    
    # Test 3: Veri yükleme
    upload = test_data_upload(physician)
    if not upload:
        print("\n❌ Test başarısız: Veri yüklenemedi")
        return
    
    # Test 4: Veri işleme
    if not test_data_processing(upload):
        print("\n❌ Test başarısız: Veri işlenemedi")
        return
    
    # Test 5: İstatistikler
    if not test_statistics():
        print("\n❌ Test başarısız: İstatistikler alınamadı")
        return
    
    # Test 6: ML eğitim logu
    test_ml_training_log()
    
    print("\n" + "="*50)
    print("✅ TÜM TESTLER TAMAMLANDI")
    print("="*50)
    print("\nSonraki adımlar:")
    print("1. Tarayıcıda http://localhost:8000/signup/ adresine gidin")
    print("2. Yeni bir hekim kaydı oluşturun")
    print("3. Admin panelinden onaylayın: http://localhost:8000/admin/")
    print("4. Hekim olarak giriş yapın: http://localhost:8000/login/")
    print("5. Veri yükleyin: http://localhost:8000/physician/upload/")
    print("6. Teşekkür sayfasını görüntüleyin: http://localhost:8000/thanks/")


if __name__ == '__main__':
    run_all_tests()
