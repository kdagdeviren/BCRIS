# 🚀 Coolify Deployment Guide

Bu rehber, BCRIS projesini Coolify kullanarak Hostinger VPS'e deploy etmek için adım adım talimatlar içerir.

## 📋 Ön Gereksinimler

- Hostinger VPS sunucusu
- Coolify kurulu ve çalışır durumda
- Git repository (GitHub, GitLab, vb.)
- Domain adı (opsiyonel)

## 🔧 Adım 1: Coolify'da Yeni Proje Oluşturma

1. Coolify dashboard'una giriş yapın
2. **New Resource** → **Application** seçin
3. **Source** olarak Git repository'nizi seçin
4. **Build Pack** olarak **Dockerfile** seçin

## 🗄️ Adım 2: PostgreSQL Database Ekleme

1. Aynı projede **New Resource** → **Database** → **PostgreSQL** seçin
2. Database ayarları:
   - **Name**: `bcris-db` (veya istediğiniz isim)
   - **Version**: `15` (önerilen)
   - **Database Name**: `bcris` ⚠️ **ÖNEMLİ**
   - **Username**: `bcris_user`
   - **Password**: Güçlü bir şifre oluşturun

3. Database'i oluşturduktan sonra **Connection String**'i kopyalayın:
   ```
   postgresql://bcris_user:PASSWORD@bcris-db:5432/bcris
   ```

## 🔐 Adım 3: Environment Variables Ayarlama

Application ayarlarında **Environment Variables** sekmesine gidin ve şunları ekleyin:

### Zorunlu Değişkenler

```env
# Django Settings
DJANGO_SECRET_KEY=your-very-long-random-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database - Coolify'dan aldığınız connection string
DATABASE_URL=postgresql://bcris_user:YOUR_PASSWORD@bcris-db:5432/bcris

# PostgreSQL Settings (Coolify otomatik ayarlayabilir)
POSTGRES_DB=bcris
POSTGRES_USER=bcris_user
POSTGRES_PASSWORD=YOUR_PASSWORD
POSTGRES_HOST=bcris-db
POSTGRES_PORT=5432

# Django Settings Module
DJANGO_SETTINGS_MODULE=bcris_project.settings_production
```

### ⚠️ KRITIK NOKTALAR

1. **DATABASE_URL** formatı: `postgresql://USER:PASSWORD@HOST:PORT/DATABASE_NAME`
   - Son kısım (`/bcris`) **veritabanı adıdır**, kullanıcı adı değil!
   
2. **POSTGRES_DB** ve **DATABASE_URL**'deki database adı aynı olmalı (`bcris`)

3. **DJANGO_ALLOWED_HOSTS**: Domain adınızı buraya ekleyin (virgülle ayırarak)

4. **DJANGO_SECRET_KEY**: Güçlü, rastgele bir key oluşturun:
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

### Opsiyonel Değişkenler

```env
# Email Settings (opsiyonel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security (production için önerilen)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Port (Coolify otomatik ayarlar)
PORT=8000
```

## 📦 Adım 4: Volumes Ayarlama

Coolify'da **Volumes** sekmesine gidin ve şunları ekleyin:

```
/app/media → bcris-media
/app/models → bcris-models
/app/staticfiles → bcris-static
/app/logs → bcris-logs
```

Bu volume'lar deployment'lar arasında veri kaybını önler.

## 🚀 Adım 5: Deploy

1. **Deploy** butonuna tıklayın
2. Build loglarını takip edin
3. Başarılı deployment sonrası **Logs** sekmesinden şunları görmelisiniz:

```
✅ PostgreSQL is ready!
📦 Running migrations...
✅ BCRIS is ready!
[INFO] Starting gunicorn...
```

## 🔍 Adım 6: İlk Kurulum

Deploy başarılı olduktan sonra:

### 1. Superuser Oluşturma

Coolify'da **Terminal** sekmesine gidin veya SSH ile bağlanın:

```bash
# Container'a girin
docker exec -it <container_name> bash

# Superuser oluşturun
python manage.py createsuperuser

# Çıkış
exit
```

### 2. Admin Panele Giriş

- URL: `https://yourdomain.com/admin/`
- Oluşturduğunuz superuser bilgileriyle giriş yapın

### 3. İlk Ayarlar

Admin panelde:
1. **Features** → Değişkenleri kontrol edin
2. **Downloadable Files** → Örnek dosyaları yükleyin
3. **Physicians** → Test kullanıcısı oluşturun

## 🐛 Sorun Giderme

### Hata: "database 'bcris_user' does not exist"

**Sebep**: DATABASE_URL yanlış yapılandırılmış.

**Çözüm**:
1. Environment Variables'da `DATABASE_URL`'i kontrol edin
2. Son kısım `/bcris` olmalı, `/bcris_user` değil
3. Doğru format:
   ```
   ✅ postgresql://bcris_user:password@bcris-db:5432/bcris
   ❌ postgresql://bcris_user:password@bcris-db:5432/bcris_user
   ```
4. Düzelttikten sonra **Redeploy**

### Hata: "DisallowedHost"

**Sebep**: Domain adı ALLOWED_HOSTS'a eklenmemiş.

**Çözüm**:
```env
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,coolify-generated-url.com
```

### Hata: Static files yüklenmiyor

**Sebep**: Volume ayarları eksik veya collectstatic çalışmamış.

**Çözüm**:
1. Volumes'u kontrol edin: `/app/staticfiles`
2. Container'a girin ve manuel çalıştırın:
   ```bash
   python manage.py collectstatic --noinput
   ```

### Database bağlantı hatası

**Çözüm**:
1. Database container'ının çalıştığını kontrol edin
2. Environment variables'ı kontrol edin
3. Database logs'u inceleyin
4. Manuel database oluşturun:
   ```bash
   docker exec -it <db_container> psql -U bcris_user -d postgres
   CREATE DATABASE bcris;
   \q
   ```

## 🔄 Güncelleme ve Yeniden Deploy

Kod değişikliklerinden sonra:

1. Git'e push yapın
2. Coolify'da **Redeploy** butonuna tıklayın
3. Volumes sayesinde veriler korunur

## 📊 Monitoring

### Logs İzleme

Coolify'da **Logs** sekmesinden:
- Application logs
- Database logs
- Build logs

### Database Yedekleme

```bash
# Backup oluşturma
docker exec <db_container> pg_dump -U bcris_user bcris > backup.sql

# Restore
docker exec -i <db_container> psql -U bcris_user bcris < backup.sql
```

## 🔒 Güvenlik Önerileri

1. **DJANGO_SECRET_KEY**: Güçlü ve benzersiz olmalı
2. **DJANGO_DEBUG**: Production'da mutlaka `False`
3. **POSTGRES_PASSWORD**: Güçlü şifre kullanın
4. **SSL**: Domain için SSL sertifikası aktif edin (Coolify otomatik yapar)
5. **Firewall**: Sadece gerekli portları açın
6. **Backups**: Düzenli database yedekleri alın

## 📚 Ek Kaynaklar

- [Coolify Documentation](https://coolify.io/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)

## 🆘 Yardım

Sorun yaşıyorsanız:
1. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detaylı sorun giderme
2. [QUICK_FIX.md](../QUICK_FIX.md) - Hızlı çözümler
3. Coolify Discord/Forum - Topluluk desteği

---

**Son Güncelleme**: 4 Aralık 2025
