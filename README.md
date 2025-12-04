# BCRIS - Breast Cancer Response Intelligence System

🧬 **Meme Kanseri Yanıt Değerlendirme Sistemi**

AI destekli, veritabanı tabanlı RCB (Residual Cancer Burden) kategorisi tahmin platformu.

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Python 3.8+
- Django 5.2+
- PostgreSQL veya SQLite

### Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Veritabanını oluştur
python manage.py migrate

# Statik dosyaları topla
python manage.py collectstatic

# Sunucuyu başlat
python manage.py runserver
```

### İlk Kullanım

1. **Admin Kullanıcısı Oluştur**
```bash
python manage.py createsuperuser
```

2. **Ana Sayfa**: http://localhost:8000/
3. **Admin Panel**: http://localhost:8000/admin/

## 📁 Proje Yapısı

```
BCRIS/
├── bcris_project/          # Django proje ayarları
├── rcb_predictor/          # Ana uygulama
│   ├── models.py           # Veritabanı modelleri
│   ├── views.py            # View fonksiyonları
│   ├── admin.py            # Admin panel yapılandırması
│   └── migrations/         # Veritabanı migration'ları
├── templates/              # HTML şablonları
│   ├── rcb_model_all.html  # Ana sayfa
│   ├── thanks.html         # Teşekkür sayfası
│   └── physician/          # Hekim sayfaları
├── static/                 # Statik dosyalar (CSS, JS, images)
├── media/                  # Yüklenen dosyalar
├── models/                 # ML model dosyaları
├── docs/                   # Dokümantasyon
├── tests/                  # Test dosyaları
└── manage.py               # Django yönetim scripti
```

## ✨ Özellikler

### 🎯 Ana Özellikler
- ✅ RCB kategorisi tahmini (RCB-0, RCB-1, RCB-2, RCB-3)
- ✅ Excel'den toplu veri yükleme
- ✅ Değişken bilgi sistemi (i butonu)
- ✅ Tedavi önerileri
- ✅ PDF rapor indirme
- ✅ Çoklu dil desteği (TR/EN)

### 👨‍⚕️ Hekim Sistemi
- ✅ Hekim kayıt ve giriş
- ✅ Hasta verisi yükleme
- ✅ Admin onay sistemi
- ✅ Teşekkür sayfası

### 🎨 Admin Panel
- ✅ Modern Unfold tema
- ✅ Özellik yönetimi
- ✅ Kategori seçenekleri
- ✅ Değişken bilgileri
- ✅ Tedavi mesajları
- ✅ ML model yönetimi
- ✅ Hekim onay sistemi
- ✅ İndirilebilir dosya yönetimi
- ✅ Tahmin kontrolü (include_in_prediction)

### 🌐 Çoklu Dil
- ✅ Türkçe/İngilizce
- ✅ Tüm sayfalarda dil desteği
- ✅ localStorage ile tercih saklama
- ✅ Otomatik dil yükleme

### 📊 Veritabanı Tabanlı
- ✅ Tüm veriler veritabanında
- ✅ Hard-code yok
- ✅ Kolay güncelleme
- ✅ Admin panelden yönetim

## 🔧 Yapılandırma

### Veritabanı
`bcris_project/settings.py` dosyasında veritabanı ayarlarını yapılandırın.

### ML Model
Admin Panel → ML Modeller → Model Yükle

### Özellikler
Admin Panel → Özellikler → Özellik Ekle/Düzenle

### Dil Dosyaları
- Ana sayfa: `static/languages.json`
- Hekim sayfaları: `static/physician_translations.json`

## 📚 Dokümantasyon

Detaylı dokümantasyon için `docs/` klasörüne bakın:

- **Genel**: [docs/README.md](docs/README.md)
- **Django**: [docs/README_DJANGO.md](docs/README_DJANGO.md)
- **Veritabanı**: [docs/DATABASE_DRIVEN_SYSTEM.md](docs/DATABASE_DRIVEN_SYSTEM.md)
- **Özellikler**: [docs/TAMAMLANAN_OZELLIKLER_OZET.md](docs/TAMAMLANAN_OZELLIKLER_OZET.md)

## 🧪 Test

```bash
# Test klasörüne git
cd tests/

# Testleri çalıştır
python test_hekim_sistemi.py
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📝 Lisans

Bu proje akademik bir çalışmadır.

## 👥 İletişim

- **Proje Sahibi**: Yusuf Kağan DAĞDEVİREN
- **Email**: dagdeviren.kagan@gmail.com

## 🙏 Teşekkürler

BCRIS projesine veri katkısında bulunan tüm hekimlere ve kurumlara teşekkür ederiz.

---

**Not**: Bu sistem bir doktora tez çalışmasıdır ve sınırlı sayıda hasta verisi ile geliştirilmiştir. Klinik kullanım öncesinde daha geniş veri setleri ile validasyon gereklidir.
