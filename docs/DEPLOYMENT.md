# BCRIS Deployment Kılavuzu - Coolify + Docker

Bu kılavuz, BCRIS projesini Hostinger VPS sunucusunda Coolify kullanarak Docker ile nasıl yayınlayacağınızı açıklar.

## 📋 Gereksinimler

### Sunucu
- **VPS**: Hostinger VPS veya herhangi bir VPS
- **RAM**: Minimum 2GB (4GB önerilir)
- **Disk**: Minimum 20GB
- **OS**: Ubuntu 20.04+ veya Debian 11+

### Yazılım
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Coolify**: En son versiyon

## 🚀 Hızlı Başlangıç

### 1. Coolify Kurulumu

```bash
# Coolify'ı yükle (eğer yüklü değilse)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

### 2. Proje Hazırlığı

```bash
# Projeyi klonla veya yükle
git clone <your-repo-url> bcris
cd bcris

# .env dosyasını oluştur
cp .env.example .env
nano .env
```

### 3. Environment Variables Ayarla

`.env` dosyasını düzenleyin:

```env
# Django Settings
DJANGO_SECRET_KEY=your-very-long-random-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
POSTGRES_DB=bcris
POSTGRES_USER=bcris_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://bcris_user:your_secure_password_here@db:5432/bcris
```

**Secret Key Oluşturma:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Coolify'da Proje Oluşturma

1. **Coolify Dashboard'a giriş yapın**
2. **New Resource** → **Docker Compose** seçin
3. **Git Repository** ekleyin veya **Manual** seçin
4. **docker-compose.yml** dosyasını yükleyin
5. **Environment Variables** ekleyin (.env içeriğini)

### 5. Volumes Yapılandırması

Coolify'da aşağıdaki volume'ları ekleyin:

```yaml
volumes:
  - db_data:/app/db.sqlite3          # Veritabanı (SQLite)
  - media_data:/app/media            # Yüklenen dosyalar
  - model_data:/app/models           # ML model dosyaları
  - static_data:/app/staticfiles     # Static dosyalar
  - log_data:/app/logs               # Log dosyaları
  - postgres_data:/var/lib/postgresql/data  # PostgreSQL data
```

### 6. Deploy

```bash
# Coolify'dan deploy butonuna tıklayın
# veya CLI'dan:
docker-compose up -d --build
```

### 7. İlk Kurulum

```bash
# Container'a girin
docker exec -it bcris_web bash

# Migration'ları çalıştır
python manage.py migrate

# Superuser oluştur
python manage.py createsuperuser

# Static dosyaları topla
python manage.py collectstatic --noinput

# Çıkış
exit
```

## 📦 Volumes Açıklaması

### Kalıcı Veriler (Her güncellemede korunur)

#### 1. `db_data` - Veritabanı
```yaml
db_data:/app/db.sqlite3
```
- SQLite veritabanı dosyası
- Tüm uygulama verileri
- **ÖNEMLİ**: Yedeklenmeli!

#### 2. `media_data` - Media Dosyaları
```yaml
media_data:/app/media
```
- Hekim kimlik kartları
- Hasta veri dosyaları
- Yüklenen Excel dosyaları
- İndirilebilir dosyalar
- **ÖNEMLİ**: Yedeklenmeli!

#### 3. `model_data` - ML Model Dosyaları
```yaml
model_data:/app/models
```
- ML model dosyaları (.joblib)
- Feature list
- Class order
- **ÖNEMLİ**: Yedeklenmeli!

#### 4. `static_data` - Static Dosyalar
```yaml
static_data:/app/staticfiles
```
- CSS, JavaScript, images
- Admin panel static dosyaları
- Otomatik oluşturulur

#### 5. `log_data` - Log Dosyaları
```yaml
log_data:/app/logs
```
- Django logları
- Gunicorn access/error logları
- Hata ayıklama için

#### 6. `postgres_data` - PostgreSQL Data
```yaml
postgres_data:/var/lib/postgresql/data
```
- PostgreSQL veritabanı dosyaları
- **ÖNEMLİ**: Yedeklenmeli!

## 🔧 Yapılandırma

### PostgreSQL Kullanımı (Önerilir)

`.env` dosyasında:
```env
DATABASE_URL=postgresql://bcris_user:password@db:5432/bcris
```

### SQLite Kullanımı

`.env` dosyasında:
```env
DATABASE_URL=sqlite:///db.sqlite3
```

`docker-compose.yml`'de `db` servisini kaldırın.

### Domain Yapılandırması

Coolify'da:
1. **Domains** sekmesine gidin
2. Domain ekleyin: `bcris.yourdomain.com`
3. **SSL Certificate** otomatik oluşturulur (Let's Encrypt)

### Nginx Reverse Proxy (Coolify otomatik yapar)

```nginx
location / {
    proxy_pass http://bcris_web:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /static/ {
    alias /app/staticfiles/;
}

location /media/ {
    alias /app/media/;
}
```

## 🔄 Güncelleme

### Kod Güncellemesi

```bash
# Coolify'dan:
# 1. Git'ten pull
# 2. Rebuild & Redeploy

# veya CLI'dan:
docker-compose down
docker-compose up -d --build
```

### Migration Çalıştırma

```bash
docker exec -it bcris_web python manage.py migrate
```

### Static Dosyaları Güncelleme

```bash
docker exec -it bcris_web python manage.py collectstatic --noinput
```

## 💾 Yedekleme

### Veritabanı Yedekleme (PostgreSQL)

```bash
# Yedek al
docker exec bcris_db pg_dump -U bcris_user bcris > backup_$(date +%Y%m%d).sql

# Geri yükle
docker exec -i bcris_db psql -U bcris_user bcris < backup_20241204.sql
```

### Veritabanı Yedekleme (SQLite)

```bash
# Yedek al
docker cp bcris_web:/app/db.sqlite3 ./backup_$(date +%Y%m%d).sqlite3

# Geri yükle
docker cp ./backup_20241204.sqlite3 bcris_web:/app/db.sqlite3
```

### Media Dosyaları Yedekleme

```bash
# Yedek al
docker run --rm -v media_data:/data -v $(pwd):/backup alpine tar czf /backup/media_backup_$(date +%Y%m%d).tar.gz -C /data .

# Geri yükle
docker run --rm -v media_data:/data -v $(pwd):/backup alpine tar xzf /backup/media_backup_20241204.tar.gz -C /data
```

### Model Dosyaları Yedekleme

```bash
# Yedek al
docker run --rm -v model_data:/data -v $(pwd):/backup alpine tar czf /backup/model_backup_$(date +%Y%m%d).tar.gz -C /data .

# Geri yükle
docker run --rm -v model_data:/data -v $(pwd):/backup alpine tar xzf /backup/model_backup_20241204.tar.gz -C /data
```

## 🔍 Monitoring

### Logları İzleme

```bash
# Tüm loglar
docker-compose logs -f

# Sadece web
docker-compose logs -f web

# Sadece database
docker-compose logs -f db

# Son 100 satır
docker-compose logs --tail=100 web
```

### Container Durumu

```bash
# Container'ları listele
docker-compose ps

# Resource kullanımı
docker stats bcris_web bcris_db
```

### Health Check

```bash
# Web health check
curl http://localhost:8000/

# Database health check
docker exec bcris_db pg_isready -U bcris_user
```

## 🐛 Sorun Giderme

### Container Başlamıyor

```bash
# Logları kontrol et
docker-compose logs web

# Container'ı yeniden başlat
docker-compose restart web
```

### Database Bağlantı Hatası

```bash
# Database container'ını kontrol et
docker-compose ps db

# Database loglarını kontrol et
docker-compose logs db

# Database'e bağlan
docker exec -it bcris_db psql -U bcris_user -d bcris
```

### Static Dosyalar Yüklenmiyor

```bash
# Static dosyaları yeniden topla
docker exec -it bcris_web python manage.py collectstatic --noinput

# Nginx'i yeniden başlat (Coolify otomatik yapar)
```

### Permission Hatası

```bash
# Volume permission'larını düzelt
docker exec -it bcris_web chown -R bcris:bcris /app/media /app/logs
```

## 📊 Performance

### Gunicorn Workers

`Dockerfile`'da:
```dockerfile
CMD ["gunicorn", "--workers", "4", "--threads", "2", ...]
```

**Workers Hesaplama**: `(2 x CPU cores) + 1`

### Database Connection Pool

`settings_production.py`'da:
```python
DATABASES = {
    'default': {
        ...
        'CONN_MAX_AGE': 600,  # 10 dakika
    }
}
```

### Cache (Redis - Opsiyonel)

```yaml
# docker-compose.yml'e ekle
redis:
  image: redis:7-alpine
  volumes:
    - redis_data:/data
```

## 🔒 Güvenlik

### Firewall

```bash
# Sadece 80, 443 ve SSH portlarını aç
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### SSL Certificate

Coolify otomatik olarak Let's Encrypt sertifikası oluşturur.

### Environment Variables

- `.env` dosyasını asla Git'e eklemeyin
- Güçlü şifreler kullanın
- Secret key'i düzenli değiştirin

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
web:
  deploy:
    replicas: 3
```

### Load Balancer

Coolify otomatik olarak load balancing yapar.

## 🎯 Checklist

### Deployment Öncesi
- [ ] `.env` dosyası oluşturuldu
- [ ] Secret key değiştirildi
- [ ] Allowed hosts ayarlandı
- [ ] Database şifresi güçlü
- [ ] Domain DNS ayarları yapıldı

### Deployment Sonrası
- [ ] Migration'lar çalıştırıldı
- [ ] Superuser oluşturuldu
- [ ] Static dosyalar toplandı
- [ ] SSL sertifikası aktif
- [ ] Yedekleme planı yapıldı
- [ ] Monitoring kuruldu

## 📞 Destek

Sorun yaşarsanız:
1. Logları kontrol edin
2. Dokümantasyonu okuyun
3. GitHub Issues açın

## 🔗 Faydalı Linkler

- [Coolify Dokümantasyonu](https://coolify.io/docs)
- [Docker Dokümantasyonu](https://docs.docker.com/)
- [Django Deployment](https://docs.djangoproject.com/en/5.2/howto/deployment/)
- [Gunicorn Dokümantasyonu](https://docs.gunicorn.org/)
