#!/usr/bin/env python
"""
Database Configuration Checker
Bu script environment variables'ları kontrol eder ve database bağlantısını test eder.
"""
import os
import sys

def check_env_vars():
    """Environment variables'ları kontrol et"""
    print("=" * 60)
    print("🔍 Environment Variables Kontrolü")
    print("=" * 60)
    
    required_vars = [
        'DJANGO_SECRET_KEY',
        'DJANGO_ALLOWED_HOSTS',
        'DATABASE_URL',
        'POSTGRES_DB',
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'POSTGRES_HOST',
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Şifreleri gizle
            if 'PASSWORD' in var or 'SECRET' in var:
                display_value = '*' * 8
            elif 'DATABASE_URL' in var:
                # DATABASE_URL'den database adını çıkar
                if '/' in value:
                    parts = value.split('/')
                    db_name = parts[-1]
                    display_value = f".../{db_name}"
                else:
                    display_value = "INVALID FORMAT"
            else:
                display_value = value
            
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    print()
    
    if missing_vars:
        print(f"⚠️  Eksik değişkenler: {', '.join(missing_vars)}")
        return False
    
    # DATABASE_URL kontrolü
    database_url = os.environ.get('DATABASE_URL', '')
    if database_url:
        print("🔍 DATABASE_URL Analizi:")
        if '/' in database_url:
            db_name_from_url = database_url.split('/')[-1]
            postgres_db = os.environ.get('POSTGRES_DB', '')
            
            print(f"   Database adı (URL'den): {db_name_from_url}")
            print(f"   POSTGRES_DB değişkeni: {postgres_db}")
            
            if db_name_from_url != postgres_db:
                print(f"   ⚠️  UYARI: Database adları eşleşmiyor!")
                print(f"   DATABASE_URL'deki: {db_name_from_url}")
                print(f"   POSTGRES_DB'deki: {postgres_db}")
                return False
            else:
                print(f"   ✅ Database adları eşleşiyor: {db_name_from_url}")
        else:
            print("   ❌ DATABASE_URL formatı hatalı!")
            return False
    
    print()
    return True

def test_database_connection():
    """Database bağlantısını test et"""
    print("=" * 60)
    print("🔌 Database Bağlantı Testi")
    print("=" * 60)
    
    try:
        # Django settings'i yükle
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bcris_project.settings_production')
        
        import django
        django.setup()
        
        from django.db import connection
        
        # Bağlantıyı test et
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL bağlantısı başarılı!")
            print(f"   Versiyon: {version}")
            
            # Database adını kontrol et
            cursor.execute("SELECT current_database();")
            current_db = cursor.fetchone()[0]
            print(f"   Bağlı database: {current_db}")
            
            expected_db = os.environ.get('POSTGRES_DB', 'bcris')
            if current_db == expected_db:
                print(f"   ✅ Doğru database'e bağlı: {current_db}")
            else:
                print(f"   ⚠️  UYARI: Farklı database'e bağlı!")
                print(f"   Beklenen: {expected_db}")
                print(f"   Gerçek: {current_db}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database bağlantı hatası:")
        print(f"   {type(e).__name__}: {str(e)}")
        
        # Hata mesajını analiz et
        error_msg = str(e).lower()
        if 'does not exist' in error_msg:
            print("\n💡 Çözüm Önerisi:")
            print("   1. DATABASE_URL'deki database adını kontrol edin")
            print("   2. POSTGRES_DB değişkenini kontrol edin")
            print("   3. Database'i manuel oluşturun:")
            print(f"      docker exec -it <db_container> psql -U {os.environ.get('POSTGRES_USER', 'bcris_user')} -d postgres")
            print(f"      CREATE DATABASE {os.environ.get('POSTGRES_DB', 'bcris')};")
        
        return False

def main():
    """Ana fonksiyon"""
    print("\n" + "=" * 60)
    print("🏥 BCRIS Database Configuration Checker")
    print("=" * 60 + "\n")
    
    # Environment variables kontrolü
    env_ok = check_env_vars()
    
    if not env_ok:
        print("\n❌ Environment variables'da sorun var!")
        print("Lütfen değişkenleri düzeltin ve tekrar deneyin.\n")
        sys.exit(1)
    
    # Database bağlantı testi
    db_ok = test_database_connection()
    
    print("\n" + "=" * 60)
    if env_ok and db_ok:
        print("✅ TÜM KONTROLLER BAŞARILI!")
        print("=" * 60 + "\n")
        sys.exit(0)
    else:
        print("❌ SORUNLAR TESPİT EDİLDİ!")
        print("=" * 60)
        print("\n📚 Detaylı yardım için:")
        print("   - QUICK_FIX.md")
        print("   - docs/TROUBLESHOOTING.md")
        print("   - docs/COOLIFY_DEPLOYMENT.md\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
