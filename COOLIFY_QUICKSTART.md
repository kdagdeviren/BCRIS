# 🚀 Coolify Hızlı Başlangıç (docker-compose)

Bu rehber, BCRIS projesini Coolify'da docker-compose ile 5 dakikada deploy etmenizi sağlar.

## ✅ Ön Hazırlık

1. Projenizi Git'e push edin (GitHub, GitLab, vb.)
2. Coolify dashboard'unuza giriş yapın

## 📦 Adım 1: Yeni Proje Oluştur

1. Coolify'da **+ New** → **Resource** → **Application**
2. **Source** seçin:
   - Git repository'nizi seçin
   - Branch: `main` veya `master`
3. **Build Pack**: **Docker Compose** seçin ⚠️ ÖNEMLİ
4. **Next**

## 🔐 Adım 2: Environment Variables (Sadece 3 tane!)

Coolify'da **Environment Variables** sekmesine gidin ve sadece şu 3 değişkeni ekleyin:

```env
DJANGO_SECRET_KEY=your-very-long-random-secret-key-here
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
POSTGRES_PASSWORD=your_secure_password_123
```

### Secret Key Oluşturma

Terminalinizde çalıştırın:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Çıkan uzun string'i `DJANGO_SECRET_KEY` olarak kullanın.

### Domain Ayarı

- Eğer domain'iniz varsa: `yourdomain.com,www.yourdomain.com`
- Eğer sadece IP kullanıyorsanız: `123.45.67.89`
- Coolify subdomain kullanıyorsanız: `myapp.coolify.io`

**Hepsi bu kadar!** Diğer tüm ayarlar otomatik yapılandırılır.

## 🚀 Adım 3: Deploy

1. **Deploy** butonuna tıklayın
2. Build loglarını izleyin (2-3 dakika sürer)
3. Başarılı olursa şunu görürsünüz:

```
✅ PostgreSQL is ready!
📦 Running migrations...
✅ BCRIS is ready!
[INFO] Starting gunicorn...
```

## 🎉 Adım 4: İlk Giriş

### Superuser Oluştur

Coolify'da **Terminal** sekmesine gidin:

```bash
# Web container'ına girin
docker exec -it $(docker ps -q -f name=web) bash

# Superuser oluşturun
python manage.py createsuperuser

# Çıkış
exit
```

Kullanıcı adı, email ve şifre girin.

### Admin Panele Giriş

- URL: `https://yourdomain.com/admin/`
- Oluşturduğunuz kullanıcı bilgileriyle giriş yapın

### Ana Sayfa

- URL: `https://yourdomain.com/`

## 🎨 Adım 5: İlk Ayarlar (Opsiyonel)

Admin panelde:

1. **Features** → Değişkenleri kontrol edin (otomatik yüklenir)
2. **Downloadable Files** → Örnek Excel ve PDF dosyalarını yükleyin
3. **Physicians** → Test kullanıcısı oluşturun

## 📊 Volumes (Otomatik)

docker-compose.yml otomatik olarak şu volume'ları oluşturur:

- `postgres_data` → Database verileri
- `media_data` → Yüklenen dosyalar
- `model_data` → ML model dosyaları
- `static_data` → CSS, JS, images
- `log_data` → Uygulama logları

Deployment'lar arasında tüm veriler korunur.

## 🔧 Opsiyonel Ayarlar

### SSL/HTTPS Aktif Etme

Domain'iniz SSL sertifikası varsa, Environment Variables'a ekleyin:

```env
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Email Ayarları

Email göndermek için (opsiyonel):

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Port Değiştirme

Varsayılan port 8000. Değiştirmek için:

```env
PORT=3000
```

## 🐛 Sorun Giderme

### Hata: "database 'bcris_user' does not exist"

Bu hata **ARTIK OLMAMALI** çünkü docker-compose.yml otomatik yapılandırılmış.

Eğer hala alıyorsanız:
1. Environment Variables'da `POSTGRES_PASSWORD` olduğundan emin olun
2. **Redeploy** yapın

### Hata: "DisallowedHost"

`DJANGO_ALLOWED_HOSTS` değişkenine domain'inizi ekleyin:

```env
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,coolify-url.com
```

### Static Files Yüklenmiyor

Container'a girin ve manuel çalıştırın:

```bash
docker exec -it $(docker ps -q -f name=web) python manage.py collectstatic --noinput
```

### Database Bağlantı Hatası

Logları kontrol edin:

```bash
# Database logs
docker logs $(docker ps -q -f name=db)

# Web logs
docker logs $(docker ps -q -f name=web)
```

### Diagnostic Script

Container'da çalıştırın:

```bash
docker exec -it $(docker ps -q -f name=web) python check_db_config.py
```

## 🔄 Güncelleme

Kod değişikliklerinden sonra:

1. Git'e push yapın
2. Coolify'da **Redeploy** butonuna tıklayın
3. Volumes sayesinde veriler korunur

## 📋 Özet Checklist

- [ ] Git repository hazır
- [ ] Coolify'da yeni application oluşturuldu
- [ ] Build Pack: **Docker Compose** seçildi
- [ ] 3 environment variable eklendi:
  - [ ] `DJANGO_SECRET_KEY`
  - [ ] `DJANGO_ALLOWED_HOSTS`
  - [ ] `POSTGRES_PASSWORD`
- [ ] Deploy tıklandı
- [ ] Superuser oluşturuldu
- [ ] Admin panele giriş yapıldı

## 🆘 Yardım

Sorun yaşıyorsanız:

- [QUICK_FIX.md](QUICK_FIX.md) - Hızlı çözümler
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Detaylı sorun giderme
- [docs/COOLIFY_DEPLOYMENT.md](docs/COOLIFY_DEPLOYMENT.md) - Detaylı rehber

## 🎯 Sonuç

Artık BCRIS projeniz Coolify'da çalışıyor! 🎉

- ✅ PostgreSQL database otomatik yapılandırıldı
- ✅ Volumes otomatik oluşturuldu
- ✅ Tüm ayarlar otomatik yapıldı
- ✅ Production-ready

---

**Deployment Süresi**: ~5 dakika  
**Gerekli Environment Variables**: Sadece 3 tane  
**Manuel Ayar**: Yok, hepsi otomatik!
