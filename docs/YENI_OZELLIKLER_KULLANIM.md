# BCRIS - Yeni Özellikler Kullanım Kılavuzu

## ✅ Tamamlanan Özellikler

### 1. Kullanıcı Kayıt ve Giriş Sistemi

#### Hekim Kaydı (Sign Up)
- **URL**: `/signup/`
- **Özellikler**:
  - Ad Soyad, Email, Telefon
  - Kurum/Hastane, Bölüm, Ünvan
  - Kimlik kartı yükleme (TC kapatılmış olmalı - KVKK uyumlu)
  - Otomatik "Onay Bekliyor" durumu

#### Hekim Girişi (Login)
- **URL**: `/login/`
- **Özellikler**:
  - Kullanıcı adı ve şifre ile giriş
  - Onay durumu kontrolü
  - Onaylanmamış kullanıcılar giriş yapamaz

### 2. Hekim Paneli

#### Dashboard
- **URL**: `/physician/dashboard/`
- **Özellikler**:
  - Toplam yükleme sayısı
  - İşlem bekleyen veri sayısı
  - İşlenmiş veri sayısı
  - Toplam hasta sayısı
  - Son yüklemeler listesi

#### Veri Yükleme
- **URL**: `/physician/upload/`
- **Özellikler**:
  - Excel dosyası yükleme (.xlsx, .xls, .csv)
  - Açıklama ekleme
  - Otomatik hasta sayısı hesaplama
  - Önceki yüklemeleri görüntüleme

#### Yüklemeler Listesi
- **URL**: `/physician/uploads/`
- **Özellikler**:
  - Tüm yüklemeleri görüntüleme
  - Durum takibi
  - Tarih ve hasta sayısı bilgisi

### 3. Admin Onay Sistemi

#### Admin Paneli
- **URL**: `/admin/`
- **Özellikler**:
  - Hekim başvurularını görüntüleme
  - Kimlik kartı kontrolü
  - Toplu onaylama/reddetme
  - Hasta verilerini inceleme
  - Veri durumu güncelleme (İnceleniyor, İşlendi, ML'e Entegre Edildi)

### 4. Teşekkür Sayfası
- **URL**: `/thanks/`
- **Özellikler**:
  - Onaylı ve veri yüklemiş hekimleri listeleme
  - Hekim adı, ünvanı, kurumu
  - Yükleme ve hasta sayısı istatistikleri
  - ML model performans bilgileri

### 5. Ana Sayfa
- **Özellikler**:
  - Tahmin aracı herkese açık (değişiklik yok)
  - Excel yükleme herkese açık (değişiklik yok)
  - Header'a Login/Sign Up butonları eklenebilir (manuel)
  - Teşekkür sayfası linki eklenebilir (manuel)

## 📋 Kullanım Senaryoları

### Senaryo 1: Yeni Hekim Kaydı
1. Hekim `/signup/` adresine gider
2. Formu doldurur ve kimlik kartını yükler
3. Kayıt tamamlanır, "Onay Bekliyor" durumuna geçer
4. Admin panelinden onay bekler

### Senaryo 2: Admin Onayı
1. Admin `/admin/` paneline girer
2. "Hekimler" bölümüne gider
3. Bekleyen hekimleri görür
4. Kimlik kartını kontrol eder
5. "Seçili hekimleri onayla" action'ını kullanır
6. Hekim artık giriş yapabilir

### Senaryo 3: Veri Yükleme
1. Onaylı hekim `/login/` ile giriş yapar
2. Dashboard'a yönlendirilir
3. "Yeni Veri Yükle" butonuna tıklar
4. Excel dosyasını seçer ve açıklama ekler
5. Yükleme tamamlanır, admin incelemesi bekler

### Senaryo 4: Admin Veri İnceleme
1. Admin `/admin/` paneline girer
2. "Hasta Verileri" bölümüne gider
3. Yüklenen veriyi inceler
4. Durumu günceller: İnceleniyor → İşlendi → ML'e Entegre Edildi
5. Notlar ekler

## 🔧 Teknik Detaylar

### Veritabanı Modelleri
- `Physician`: Hekim bilgileri ve onay durumu
- `PatientDataUpload`: Yüklenen hasta verileri
- `MLTrainingLog`: ML eğitim logları

### URL Yapısı
```
/                          -> Ana sayfa (herkese açık)
/login/                    -> Hekim girişi
/signup/                   -> Hekim kaydı
/logout/                   -> Çıkış
/physician/dashboard/      -> Hekim paneli (giriş gerekli)
/physician/upload/         -> Veri yükleme (giriş gerekli)
/physician/uploads/        -> Yüklemeler listesi (giriş gerekli)
/thanks/                   -> Teşekkür sayfası (herkese açık)
/admin/                    -> Admin paneli
```

### Güvenlik
- Django authentication sistemi
- Login required decorator
- KVKK uyumlu (TC kimlik no kapatılmalı)
- Dosya yükleme validasyonu
- Admin onayı gerekli

## 🚀 Sonraki Adımlar

### Ana Sayfa Güncellemeleri (Manuel)
Ana sayfa template'ine aşağıdaki butonları ekleyebilirsiniz:

```html
<!-- Header'a eklenecek -->
<div class="auth-buttons">
    <a href="{% url 'rcb_predictor:physician_login' %}" class="btn-login">Giriş Yap</a>
    <a href="{% url 'rcb_predictor:physician_signup' %}" class="btn-signup">Kayıt Ol</a>
    <a href="{% url 'rcb_predictor:thanks' %}" class="btn-thanks">Teşekkürler</a>
</div>
```

### Email Bildirimleri (Opsiyonel)
- Kayıt sonrası admin'e bildirim
- Onay sonrası hekime bildirim
- Veri işleme sonrası bildirim

### Kurum Logoları (Opsiyonel)
- Physician modeline logo field eklenebilir
- Teşekkür sayfasında gösterilebilir

## 📊 İstatistikler

### Admin Dashboard
- Toplam hekim sayısı
- Onay bekleyen hekim sayısı
- Toplam veri yükleme sayısı
- İşlem bekleyen veri sayısı
- ML model performansı

### Hekim Dashboard
- Kişisel yükleme sayısı
- İşlem durumu
- Toplam hasta katkısı

## 🔐 Güvenlik Notları

1. **KVKK Uyumu**: TC kimlik numarası kapatılmalı
2. **Veri Güvenliği**: Hasta kimlik bilgileri içermemeli
3. **Admin Onayı**: Tüm hekimler manuel onay gerektirir
4. **Dosya Validasyonu**: Sadece Excel/CSV dosyaları kabul edilir
5. **Erişim Kontrolü**: Sadece onaylı hekimler veri yükleyebilir

## 📝 Notlar

- Tahmin aracı herkese açık kalır (mevcut durum korunur)
- Hekim sistemi tamamen ayrı bir modül
- ML eğitimi için veri toplama odaklı
- Admin paneli Unfold ile modern görünüm
- Responsive tasarım (mobil uyumlu)
