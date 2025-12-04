# 🚨 Hızlı Çözüm: "database 'bcris_user' does not exist"

## Sorun
PostgreSQL, veritabanı adı olarak kullanıcı adını kullanmaya çalışıyor.

## ✅ Hızlı Çözüm (Coolify)

### 1. Environment Variables'ı Kontrol Edin

Coolify'da **Environment Variables** sekmesine gidin ve şunları kontrol edin:

```env
POSTGRES_DB=bcris
POSTGRES_USER=bcris_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=bcris-db
DATABASE_URL=postgresql://bcris_user:your_secure_password@bcris-db:5432/bcris
```

**ÖNEMLİ**: 
- `DATABASE_URL`'in sonundaki `/bcris` kısmı veritabanı adıdır (kullanıcı adı değil!)
- `POSTGRES_HOST` Coolify'da oluşturduğunuz database service adı olmalı (genellikle `bcris-db` veya benzeri)

### 2. Değişkenleri Düzeltin

Eğer `DATABASE_URL` şöyle ise:
```
❌ postgresql://bcris_user:password@db:5432/bcris_user
❌ postgresql://bcris_user:password@localhost:5432/bcris_user
```

Şu şekilde değiştirin (Coolify database service adınızı kullanın):
```
✅ postgresql://bcris_user:password@bcris-db:5432/bcris
```

**Not**: `bcris-db` kısmı Coolify'da oluşturduğunuz PostgreSQL service'in adıdır. Kendi service adınızı kullanın.

### 3. Database Service Adını Bulma

Coolify'da:
1. **Resources** → **Databases** sekmesine gidin
2. PostgreSQL database'inizin adını not edin (örn: `bcris-db`, `postgres-xyz`, vb.)
3. Bu adı `DATABASE_URL` ve `POSTGRES_HOST` değişkenlerinde kullanın

### 4. Redeploy

Coolify'da **Redeploy** butonuna tıklayın.

## 🔧 Alternatif Çözüm: Manuel Database Oluşturma

Eğer yukarıdaki çözüm işe yaramazsa:

```bash
# 1. Database container'ına girin
docker exec -it <db_container_name> psql -U bcris_user -d postgres

# 2. Database oluşturun
CREATE DATABASE bcris;

# 3. Çıkış
\q

# 4. Web container'ını yeniden başlatın
docker restart <web_container_name>
```

## 🔍 Diagnostic Script ile Kontrol

Coolify container'ında çalıştırın:

```bash
# Container'a girin
docker exec -it <web_container_name> bash

# Diagnostic script'i çalıştırın
python check_db_config.py

# Çıkış
exit
```

Bu script:
- ✅ Environment variables'ları kontrol eder
- ✅ DATABASE_URL formatını doğrular
- ✅ Database adı eşleşmesini kontrol eder
- ✅ Database bağlantısını test eder
- ✅ Sorunlar için çözüm önerir

## 🔍 Container İsimlerini Bulma

```bash
# Container'ları listele
docker ps

# veya
docker-compose ps
```

## 📝 Doğru Yapılandırma

### .env Dosyası
```env
POSTGRES_DB=bcris                    # ← Veritabanı adı
POSTGRES_USER=bcris_user             # ← Kullanıcı adı
POSTGRES_PASSWORD=secure_password    # ← Şifre
DATABASE_URL=postgresql://bcris_user:secure_password@db:5432/bcris  # ← Son kısım DB adı!
```

### docker-compose.yml
```yaml
db:
  environment:
    - POSTGRES_DB=bcris              # ← Veritabanı adı
    - POSTGRES_USER=bcris_user       # ← Kullanıcı adı
    - POSTGRES_PASSWORD=password     # ← Şifre
```

## ✅ Test

Düzeltmeden sonra test edin:

```bash
# Logları kontrol edin
docker-compose logs -f web

# Database bağlantısını test edin
docker exec -it <web_container> python manage.py check --database default
```

Başarılı olursa şunu görmelisiniz:
```
✅ PostgreSQL is ready!
📦 Running migrations...
✅ BCRIS is ready!
```

## 🆘 Hala Çalışmıyor mu?

Detaylı sorun giderme için: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
