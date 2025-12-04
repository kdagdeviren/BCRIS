# BCRIS Deployment Sorun Giderme

## ❌ Hata: "database 'bcris_user' does not exist"

### Sorun
PostgreSQL, veritabanı adı olarak kullanıcı adını (`POSTGRES_USER`) kullanmaya çalışıyor.

### Çözüm 1: Environment Variables Kontrolü (Coolify)

Coolify'da **Environment Variables** sekmesinde kontrol edin:

```env
# DOĞRU ✅
POSTGRES_DB=bcris
POSTGRES_USER=bcris_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=bcris-db                    # ← Coolify database service adı
DATABASE_URL=postgresql://bcris_user:your_password@bcris-db:5432/bcris

# YANLIŞ ❌
DATABASE_URL=postgresql://bcris_user:your_password@db:5432/bcris_user
DATABASE_URL=postgresql://bcris_user:your_password@localhost:5432/bcris_user
```

**Önemli Noktalar**:
1. `DATABASE_URL`'deki son kısım (`/bcris`) veritabanı adıdır, kullanıcı adı değil!
2. `POSTGRES_HOST` Coolify'da oluşturduğunuz database service adı olmalı
3. Coolify'da database service adını **Resources** → **Databases** sekmesinden bulabilirsiniz

### Çözüm 2: Docker Compose Kontrolü

`docker-compose.yml` dosyasında:

```yaml
db:
  environment:
    - POSTGRES_DB=bcris          # ✅ Veritabanı adı
    - POSTGRES_USER=bcris_user   # ✅ Kullanıcı adı
    - POSTGRES_PASSWORD=password # ✅ Şifre
```

### Çözüm 3: Manuel Database Oluşturma

Eğer sorun devam ederse, database'i manuel oluşturun:

```bash
# Database container'ına girin
docker exec -it bcris_db psql -U bcris_user -d postgres

# Database oluşturun
CREATE DATABASE bcris;

# Çıkış
\q
```

### Çözüm 4: Container'ları Yeniden Başlatın

```bash
# Tüm container'ları durdurun
docker-compose down

# Volume'ları temizleyin (DİKKAT: Veri kaybı!)
docker-compose down -v

# Yeniden başlatın
docker-compose up -d
```

## ❌ Hata: "Connection refused" veya "Database not ready"

### Sorun
Web container, database hazır olmadan başlamaya çalışıyor.

### Çözüm 1: start.sh Kontrolü

`start.sh` scripti database'i beklemeli:

```bash
# PostgreSQL hazır mı kontrol et
pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"
```

### Çözüm 2: depends_on Kontrolü

`docker-compose.yml`'de:

```yaml
web:
  depends_on:
    - db
```

### Çözüm 3: Health Check

Database container'ının health check'i:

```yaml
db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U bcris_user"]
    interval: 10s
    timeout: 5s
    retries: 5
```

## ❌ Hata: "Static files not found"

### Sorun
Static dosyalar toplanmamış veya yanlış yerde.

### Çözüm 1: Collectstatic Çalıştırın

```bash
docker exec -it bcris_web python manage.py collectstatic --noinput
```

### Çözüm 2: WhiteNoise Kontrolü

`settings_production.py`'da:

```python
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Çözüm 3: Volume Kontrolü

```yaml
volumes:
  - static_data:/app/staticfiles
```

## ❌ Hata: "Permission denied"

### Sorun
Container içinde dosya izinleri yanlış.

### Çözüm 1: Ownership Düzeltme

```bash
docker exec -it bcris_web chown -R bcris:bcris /app/media /app/logs
```

### Çözüm 2: Dockerfile Kontrolü

```dockerfile
RUN useradd -m -u 1000 bcris && \
    chown -R bcris:bcris /app

USER bcris
```

## ❌ Hata: "Migration failed"

### Sorun
Database migration'ları çalışmadı.

### Çözüm 1: Manuel Migration

```bash
docker exec -it bcris_web python manage.py migrate --noinput
```

### Çözüm 2: Migration Durumu

```bash
# Migration durumunu kontrol et
docker exec -it bcris_web python manage.py showmigrations

# Fake migration (gerekirse)
docker exec -it bcris_web python manage.py migrate --fake
```

## ❌ Hata: "Module not found"

### Sorun
Python paketi yüklenmemiş.

### Çözüm 1: Requirements Kontrolü

```bash
# Container'a girin
docker exec -it bcris_web bash

# Paketi kontrol et
pip list | grep django

# Paketi yükle
pip install <package-name>
```

### Çözüm 2: Rebuild

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## ❌ Hata: "Port already in use"

### Sorun
8000 portu başka bir uygulama tarafından kullanılıyor.

### Çözüm 1: Port Değiştirme

`docker-compose.yml`'de:

```yaml
ports:
  - "8001:8000"  # Host:Container
```

### Çözüm 2: Portu Kullanan Uygulamayı Bulma

```bash
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

## ❌ Hata: "Out of memory"

### Sorun
Container yeterli RAM'e sahip değil.

### Çözüm 1: Worker Sayısını Azaltın

`start.sh` veya `Dockerfile`'da:

```bash
gunicorn --workers 2 --threads 2 ...  # 4 yerine 2
```

### Çözüm 2: Memory Limit

`docker-compose.yml`'de:

```yaml
web:
  deploy:
    resources:
      limits:
        memory: 2G
```

## 🔍 Genel Debugging

### Logları Kontrol Edin

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

# Container'a girin
docker exec -it bcris_web bash
```

### Database Bağlantısı Test

```bash
# PostgreSQL'e bağlan
docker exec -it bcris_db psql -U bcris_user -d bcris

# Database'leri listele
\l

# Tabloları listele
\dt

# Çıkış
\q
```

### Django Shell

```bash
# Django shell'e girin
docker exec -it bcris_web python manage.py shell

# Database bağlantısını test et
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("✅ Database connected!")
```

## 🆘 Hala Çözülmedi mi?

### 1. Temiz Başlangıç

```bash
# UYARI: Tüm veriler silinir!
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

### 2. Logları Kaydedin

```bash
docker-compose logs > logs.txt
```

### 3. Environment Variables'ı Kontrol Edin

```bash
# Container içinde
docker exec -it bcris_web env | grep POSTGRES
docker exec -it bcris_web env | grep DJANGO
```

### 4. Destek Alın

- GitHub Issues açın
- Logları paylaşın
- Environment variables'ı (şifreler hariç) paylaşın
- Docker ve sistem bilgilerini ekleyin

## 📋 Checklist

Deployment sorunları için kontrol listesi:

- [ ] `.env` dosyası oluşturuldu
- [ ] `DJANGO_SECRET_KEY` değiştirildi
- [ ] `POSTGRES_PASSWORD` güçlü
- [ ] `DATABASE_URL` doğru format
- [ ] `ALLOWED_HOSTS` doğru
- [ ] Docker ve Docker Compose yüklü
- [ ] Portlar müsait (8000, 5432)
- [ ] Yeterli disk alanı (min 10GB)
- [ ] Yeterli RAM (min 2GB)
- [ ] start.sh executable (+x)
- [ ] Volume'lar oluşturuldu
- [ ] Migration'lar çalıştırıldı
- [ ] Static files toplandı
- [ ] Superuser oluşturuldu

## 🔗 Faydalı Komutlar

```bash
# Container'ları yeniden başlat
docker-compose restart

# Sadece web'i yeniden başlat
docker-compose restart web

# Logları temizle
docker-compose logs --tail=0 -f

# Volume'ları listele
docker volume ls

# Network'leri listele
docker network ls

# Image'ları listele
docker images

# Kullanılmayan kaynakları temizle
docker system prune -a
```
