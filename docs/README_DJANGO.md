# BCRIS - Django Versiyonu

Bu proje, Flask tabanlı BCRIS (Breast Cancer Response Intelligence System) uygulamasının Django'ya çevrilmiş halidir.

## Kurulum

### 1. Gerekli Paketleri Yükleyin

```bash
pip install -r requirements.txt
```

### 2. Veritabanını Oluşturun

```bash
python manage.py migrate
```

### 3. Static Dosyaları Toplayın (Production için)

```bash
python manage.py collectstatic
```

### 4. Uygulamayı Çalıştırın

```bash
python manage.py runserver
```

Uygulama `http://127.0.0.1:8000/` adresinde çalışacaktır.

## Proje Yapısı

```
.
├── bcris_project/          # Django proje ayarları
│   ├── settings.py         # Proje ayarları
│   ├── urls.py             # Ana URL yapılandırması
│   └── wsgi.py             # WSGI yapılandırması
├── rcb_predictor/          # Ana uygulama
│   ├── views.py            # View fonksiyonları
│   ├── urls.py             # Uygulama URL'leri
│   └── ...
├── templates/              # HTML şablonları
│   ├── rcb_model_all.html  # Ana sayfa
│   └── admin_messages.html # Admin paneli
├── static/                 # Static dosyalar (CSS, JS, resimler)
│   ├── logo.png
│   └── languages.json
├── models/                 # ML model dosyaları
│   ├── best_model.joblib
│   ├── feature_list.json
│   └── class_order.json
├── treatment_messages.json # Tedavi mesajları
├── variable_info.json      # Değişken bilgileri
├── manage.py               # Django yönetim scripti
└── requirements.txt        # Python bağımlılıkları
```

## Flask'tan Django'ya Çevirme Değişiklikleri

### 1. Route'lar → URL Patterns
- Flask: `@app.route('/')`
- Django: `path('', views.index, name='index')`

### 2. Request Handling
- Flask: `request.args.get()`, `request.json`
- Django: `request.GET.get()`, `json.loads(request.body)`

### 3. Response
- Flask: `jsonify()`, `render_template()`
- Django: `JsonResponse()`, `render()`

### 4. Static Files
- Flask: `url_for('static', filename='...')`
- Django: `{% static '...' %}`

### 5. CSRF Protection
- Django view'larında POST istekleri için `@csrf_exempt` dekoratörü eklendi
- Production'da CSRF koruması aktif edilmelidir

## Özellikler

- ✅ RCB kategorisi tahmini
- ✅ Excel dosyasından veri yükleme
- ✅ Optimal özellik kombinasyonları
- ✅ Çoklu dil desteği (TR/EN)
- ✅ Tedavi önerileri
- ✅ Admin paneli
- ✅ Değişken bilgileri
- ✅ Örnek dosya indirme

## Notlar

- Model dosyaları (`models/` klasörü) ve JSON dosyaları Flask versiyonundan aynı şekilde kullanılmaktadır
- Template dosyaları minimal değişikliklerle Django template syntax'ına uyarlanmıştır
- Global değişkenler (model, feature_list, vb.) views.py içinde tanımlanmıştır
- Production ortamında `DEBUG = False` yapılmalı ve `ALLOWED_HOSTS` ayarlanmalıdır

## Admin Paneli

Admin paneline erişim için süper kullanıcı oluşturun:

```bash
python manage.py createsuperuser
```

Admin paneli: `http://127.0.0.1:8000/admin/`

## Lisans

Bu proje, Yusuf Kağan DAĞDEVİREN tarafından geliştirilen bir doktora tez çalışmasıdır.
