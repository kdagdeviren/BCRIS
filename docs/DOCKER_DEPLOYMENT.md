# 🐳 BCRIS Docker Deployment - Hızlı Başlangıç

## 📦 Oluşturulan Dosyalar

### 1. **Dockerfile**
Production-ready Docker image tanımı:
- Python 3.11 slim base
- Gunicorn web server
- Non-root user (güvenlik)
- Health check
- Multi-stage build için optimize

### 2. **docker-compose.yml**
Tam stack yapılandırması:
- Web service (Django + Gunicorn)
- PostgreSQL database
- Volumes (kalıcı veri)
- Networks
- Health checks

### 3. **.env.example**
Environment variables şablonu:
- Django ayarları
- Database credentials
- Email ayarları
- Security settings

### 4. **.dockerignore**
Docker build'den hariç tutulan dosyalar:
- Python cache
- Virtual environments
- IDE dosyaları
- Dokümantasyon

### 5. **settings_production.py**
Production Django ayarları:
- Database (PostgreSQL/SQLite)
- Static files (WhiteNoise)
- Security headers
- Logging
- Cache (Redis opsiyonel)

### 6. **start.sh**
Container başlangıç scripti:
- Database bekleme
- Migration çalıştırma
- Static files toplama
- Gunicorn başlatma

### 7. **docs/DEPLOYMENT.md**
Detaylı deployment kılavuzu

## 🚀 Hızlı Başlangıç

### 1. Environment Hazırlığı

```bash
# .env dosyası oluştur
cp .env.example .env

# .env dosyasını düzenle
nano .env
```

**Önemli**: `DJANGO_SECRET_KEY` ve `POSTGRES_PASSWORD` değiştirin!

### 2. Build & Run

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Logları izle
docker-compose logs -f
```

### 3. İlk Kurulum

```bash
# Migration
docker exec -it bcris_web python manage.py migrate

# Superuser
docker exec -it bcris_web python manage.py createsuperuser

# Static files
docker exec -it bcris_web python manage.py collectstatic --noinput
```

### 4. Erişim

- **Ana Sayfa**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/

## 📁 Volumes (Kalıcı Veri)

### Otomatik Korunan Veriler

```yaml
volumes:
  db_data: /app/db.sqlite3              # Veritabanı
  media_data: /app/media                # Yüklenen dosyalar
  model_data: /app/models               # ML modeller
  static_data: /app/staticfiles         # Static dosyalar
  log_data: /app/logs                   # Loglar
  postgres_data: /var/lib/postgresql/data  # PostgreSQL
```

**Önemli**: Bu volume'lar her deployment'ta korunur!

## 🔧 Coolify Deployment

### 1. Coolify'da Yeni Proje

1. **New Resource** → **Docker Compose**
2. Git repository bağla veya manuel yükle
3. `docker-compose.yml` seç

### 2. Environment Variables

Coolify'da `.env` içeriğini ekle:
```
DJANGO_SECRET_KEY=...
DJANGO_ALLOWED_HOSTS=yourdomain.com
POSTGRES_PASSWORD=...
```

### 3. Domain Ayarları

1. **Domains** → Domain ekle
2. SSL otomatik oluşturulur (Let's Encrypt)

### 4. Deploy

**Deploy** butonuna tıkla!

## 🔄 Güncelleme

```bash
# Kod güncelle
git pull

# Rebuild & restart
docker-compose down
docker-compose up -d --build

# Migration (gerekirse)
docker exec -it bcris_web python manage.py migrate
```

## 💾 Yedekleme

### Veritabanı (PostgreSQL)

```bash
# Yedek al
docker exec bcris_db pg_dump -U bcris_user bcris > backup.sql

# Geri yükle
docker exec -i bcris_db psql -U bcris_user bcris < backup.sql
```

### Media Dosyaları

```bash
# Yedek al
docker run --rm -v media_data:/data -v $(pwd):/backup alpine tar czf /backup/media.tar.gz -C /data .

# Geri yükle
docker run --rm -v media_data:/data -v $(pwd):/backup alpine tar xzf /backup/media.tar.gz -C /data
```

## 🐛 Sorun Giderme

### Logları Kontrol

```bash
# Tüm loglar
docker-compose logs -f

# Sadece web
docker-compose logs -f web

# Sadece database
docker-compose logs -f db
```

### Container'a Giriş

```bash
# Web container
docker exec -it bcris_web bash

# Database container
docker exec -it bcris_db psql -U bcris_user -d bcris
```

### Yeniden Başlatma

```bash
# Tüm servisler
docker-compose restart

# Sadece web
docker-compose restart web
```

## 📊 Monitoring

### Container Durumu

```bash
docker-compose ps
```

### Resource Kullanımı

```bash
docker stats bcris_web bcris_db
```

### Health Check

```bash
curl http://localhost:8000/
```

## 🔒 Güvenlik Checklist

- [ ] `DJANGO_SECRET_KEY` değiştirildi
- [ ] `DJANGO_DEBUG=False` ayarlandı
- [ ] Güçlü database şifresi kullanıldı
- [ ] `ALLOWED_HOSTS` doğru ayarlandı
- [ ] SSL sertifikası aktif
- [ ] Firewall yapılandırıldı

## 📚 Detaylı Dokümantasyon

Daha fazla bilgi için: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## 🎯 Production Checklist

### Deployment Öncesi
- [ ] `.env` dosyası oluşturuldu
- [ ] Secret key değiştirildi
- [ ] Database şifresi güçlü
- [ ] Domain DNS ayarları yapıldı

### Deployment Sonrası
- [ ] Migration'lar çalıştırıldı
- [ ] Superuser oluşturuldu
- [ ] Static files toplandı
- [ ] SSL aktif
- [ ] Yedekleme planı yapıldı

## 🆘 Destek

Sorun yaşarsanız:
1. `docker-compose logs -f` ile logları kontrol edin
2. [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) dokümantasyonunu okuyun
3. GitHub Issues açın

---

**Not**: Bu yapılandırma production-ready'dir ve Coolify ile tam uyumludur!
