# 🚀 Coolify Deployment (Dockerfile + SQLite)

BCRIS projesini Coolify'da 3 dakikada deploy edin!

## 📦 Adım 1: Yeni Proje

1. Coolify → **+ New** → **Application**
2. Git repository seçin
3. **Build Pack**: **Dockerfile** ⚠️
4. **Next**

## 🔐 Adım 2: Environment Variables (2 tane)

```env
DJANGO_SECRET_KEY=your-very-long-random-secret-key
DJANGO_ALLOWED_HOSTS=your-coolify-domain.sslip.io,yourdomain.com,www.yourdomain.com
```

**Not**: Coolify'ın otomatik oluşturduğu domain'i (örn: `n0sc8wsk0w4ow08g00wg0kkc.82.25.101.93.sslip.io`) mutlaka ekleyin!

Secret key oluştur:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 📁 Adım 3: Volumes

Coolify'da **Volumes** sekmesi:

```
/app/data → bcris-database
/app/media → bcris-media
/app/models → bcris-models
/app/staticfiles → bcris-static
/app/logs → bcris-logs
```

## 🚀 Adım 4: Deploy

**Deploy** butonuna tıkla!

## 🎉 Adım 5: Superuser Oluştur

```bash
docker exec -it $(docker ps -q -f name=bcris) python manage.py createsuperuser
```

## ✅ Bitti!

- Admin: `https://yourdomain.com/admin/`
- Ana Sayfa: `https://yourdomain.com/`

---

**Avantajlar**:
- ✅ Veritabanı kurulumu yok (SQLite)
- ✅ Sadece 2 environment variable
- ✅ Tek container
- ✅ Hızlı deployment
