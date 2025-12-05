# 🎯 BCRIS Deployment - Final Konfigürasyon

## ✅ Yapılandırma: Dockerfile + SQLite

Proje artık **en basit** şekilde deploy edilebilir:

### 🎨 Mimari
- **Container**: Tek Docker container
- **Database**: SQLite (volume'da)
- **Web Server**: Gunicorn
- **Static Files**: WhiteNoise
- **Build**: Dockerfile

### 📦 Gerekli Dosyalar

✅ **Dockerfile** - Production-ready Python 3.11 image  
✅ **start.sh** - Container başlangıç scripti  
✅ **.dockerignore** - Build optimizasyonu  
✅ **.env.example** - Environment variables şablonu  
✅ **bcris_project/settings_production.py** - SQLite yapılandırması  
✅ **requirements.txt** - Python bağımlılıkları  

### 🗑️ Gereksiz Dosyalar (Silinebilir)

❌ **docker-compose.yml** - Artık gerekli değil  
❌ **docker-compose.yaml** - Artık gerekli değil  
❌ **COOLIFY_QUICKSTART.md** - Eski PostgreSQL rehberi  
❌ **DEPLOYMENT_SUMMARY.md** - Eski özet  
❌ **DOCKER_DEPLOYMENT.md** - Eski rehber  
❌ **QUICK_FIX.md** - PostgreSQL sorunları için  
❌ **check_db_config.py** - PostgreSQL kontrolü için  
❌ **docs/COOLIFY_DEPLOYMENT.md** - Eski detaylı rehber  
❌ **docs/TROUBLESHOOTING.md** - PostgreSQL sorunları  

## 🚀 Coolify Deployment Adımları

### 1. Proje Oluştur
- Build Pack: **Dockerfile**
- Git repository'nizi bağlayın

### 2. Environment Variables (2 tane)
```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=yourdomain.com
```

### 3. Volumes (5 tane)
```
/app/data → bcris-database
/app/media → bcris-media
/app/models → bcris-models
/app/staticfiles → bcris-static
/app/logs → bcris-logs
```

### 4. Deploy
Deploy butonuna tıkla!

### 5. Superuser
```bash
docker exec -it $(docker ps -q -f name=bcris) python manage.py createsuperuser
```

## 📊 Volume Detayları

| Path | Volume Name | İçerik | Kritik |
|------|-------------|--------|--------|
| `/app/data` | bcris-database | SQLite database | ⚠️ ÇOK ÖNEMLİ |
| `/app/media` | bcris-media | Yüklenen dosyalar | ⚠️ ÖNEMLİ |
| `/app/models` | bcris-models | ML model dosyaları | ⚠️ ÖNEMLİ |
| `/app/staticfiles` | bcris-static | CSS, JS, images | ℹ️ Yeniden oluşturulabilir |
| `/app/logs` | bcris-logs | Uygulama logları | ℹ️ Opsiyonel |

## 🔧 Teknik Detaylar

### Database
- **Engine**: SQLite3
- **Location**: `/app/data/db.sqlite3`
- **Backup**: Tek dosya, kolay yedekleme

### Web Server
- **Server**: Gunicorn
- **Workers**: 4
- **Threads**: 2 per worker
- **Timeout**: 120 saniye
- **Port**: 8000

### Static Files
- **Handler**: WhiteNoise
- **Compression**: Aktif
- **Location**: `/app/staticfiles`

### Security
- **DEBUG**: False
- **SECRET_KEY**: Environment variable
- **ALLOWED_HOSTS**: Environment variable
- **SSL**: Opsiyonel (environment variable)

## ✨ Avantajlar

✅ **Basit**: Tek container, tek database dosyası  
✅ **Hızlı**: Veritabanı kurulumu yok  
✅ **Az kaynak**: PostgreSQL container'ı yok  
✅ **Kolay yedekleme**: Tek SQLite dosyası  
✅ **Minimal config**: Sadece 2 environment variable  

## ⚠️ SQLite Limitler

SQLite küçük-orta ölçekli projeler için uygundur:

✅ **Uygun**:
- Günde <100K istek
- Eşzamanlı <100 kullanıcı
- Database <10GB
- Tek sunucu deployment

❌ **Uygun Değil**:
- Çok yüksek trafik
- Çok sayıda eşzamanlı yazma
- Çoklu sunucu (load balancing)
- Database >10GB

## 🔄 Migration: SQLite → PostgreSQL

Eğer ileride PostgreSQL'e geçmek isterseniz:

1. PostgreSQL container ekle
2. `settings_production.py`'de database ayarlarını değiştir
3. Data export/import yap
4. Redeploy

## 📝 Deployment Checklist

- [ ] Git'e push yapıldı
- [ ] Coolify'da application oluşturuldu
- [ ] Build Pack: Dockerfile seçildi
- [ ] 2 environment variable eklendi
- [ ] 5 volume eklendi
- [ ] Deploy tıklandı
- [ ] Build başarılı
- [ ] Container çalışıyor
- [ ] Superuser oluşturuldu
- [ ] Admin panele giriş yapıldı
- [ ] Ana sayfa çalışıyor

## 🆘 Sorun Giderme

### Container başlamıyor
```bash
docker logs $(docker ps -aq -f name=bcris)
```

### Database hatası
```bash
docker exec -it $(docker ps -q -f name=bcris) ls -la /app/data/
```

### Static files yüklenmiyor
```bash
docker exec -it $(docker ps -q -f name=bcris) python manage.py collectstatic --noinput
```

### Migrations hatası
```bash
docker exec -it $(docker ps -q -f name=bcris) python manage.py migrate --noinput
```

## 🎯 Sonuç

Proje artık **production-ready** ve **minimal yapılandırma** ile deploy edilebilir:

- ✅ Dockerfile ile tek container
- ✅ SQLite ile kolay database
- ✅ 5 volume ile veri güvenliği
- ✅ 2 environment variable ile basit config
- ✅ Gunicorn ile production server
- ✅ WhiteNoise ile static files

**Deployment süresi**: ~3 dakika  
**Gerekli bilgi**: Sadece secret key ve domain  
**Veritabanı kurulumu**: Yok!

---

📚 **Hızlı Başlangıç**: [COOLIFY_SIMPLE.md](COOLIFY_SIMPLE.md)
