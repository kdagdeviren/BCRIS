# BCRIS - Yeni Özellikler Geliştirme Planı

## Talep Özeti
Kullanıcı, sisteme aşağıdaki özelliklerin eklenmesini istiyor:

### 1. Kullanıcı Kayıt ve Giriş Sistemi
- **Login** ve **Sign Up** sayfaları
- Sign Up sırasında:
  - Kullanıcı bilgileri (ad, soyad, email, telefon, kurum, bölüm, ünvan)
  - Kurum kimlik kartı ön yüzü yükleme (TC kimlik no kapatılmış olmalı - KVKK)
  - Kayıt sonrası "Onay Bekliyor" durumu

### 2. Admin Onay Sistemi
- Admin veya site yöneticisi hekim kimliklerini onaylar
- Onaylanan hekimler kendi hastalarının verilerini girebilir
- **Amaç**: ML için hasta sayısını artırmak
- Hasta sayısı arttıkça doğruluk ve kesinlik oranları artacak

### 3. Teşekkür Sayfası
- Ana sayfada "Teşekkür" linki
- Veri yollayan hekimlerin:
  - Adı
  - Ünvanı
  - Kurumu
  - Kurum logosu
- Projeye destek için teşekkür amaçlı

### 4. Ana Sayfa Erişim
- Tahmin aracı herkese açık (giriş gerektirmez)
- Excel yükleme butonu herkese açık
- Sign in/up gerektirmez

## Mevcut Durum
✅ Veritabanı modelleri zaten hazır:
- `Physician` modeli (hekim bilgileri, onay durumu, kimlik kartı)
- `PatientDataUpload` modeli (hasta verileri yükleme)
- `MLTrainingLog` modeli (ML eğitim logları)
- Admin paneli hazır (Unfold ile)

## Yapılacaklar

### Adım 1: Authentication Sistemi
- [ ] Django authentication kullan
- [ ] Login sayfası oluştur
- [ ] Sign Up sayfası oluştur (Physician kaydı)
- [ ] Kimlik kartı yükleme formu

### Adım 2: Hekim Paneli
- [ ] Hekim dashboard sayfası
- [ ] Hasta verisi yükleme formu
- [ ] Yüklenen verileri görüntüleme
- [ ] Onay durumu takibi

### Adım 3: Admin Onay Sistemi
- [x] Admin panelinde zaten var (Physician modeli)
- [ ] Email bildirimleri (opsiyonel)

### Adım 4: Teşekkür Sayfası
- [ ] Teşekkür sayfası template
- [ ] Onaylı hekimleri listele
- [ ] Kurum logoları için model/field ekle

### Adım 5: Ana Sayfa Güncellemeleri
- [ ] Header'a Login/Sign Up butonları ekle
- [ ] Teşekkür sayfası linki ekle
- [ ] Tahmin aracı ve Excel yükleme açık kalsın

## Teknik Detaylar

### URL Yapısı
```
/                          -> Ana sayfa (tahmin aracı - herkese açık)
/login/                    -> Giriş sayfası
/signup/                   -> Kayıt sayfası
/physician/dashboard/      -> Hekim paneli (giriş gerekli)
/physician/upload/         -> Veri yükleme (giriş gerekli)
/thanks/                   -> Teşekkür sayfası (herkese açık)
/admin/                    -> Admin paneli (mevcut)
```

### Güvenlik
- KVKK uyumlu (TC kimlik no kapatılmalı)
- Dosya yükleme validasyonu
- Sadece onaylı hekimler veri yükleyebilir
- Admin onayı gerekli

### Veritabanı
- Mevcut modeller yeterli
- Opsiyonel: `PhysicianLogo` modeli eklenebilir

## Öncelik Sırası
1. Authentication (Login/Sign Up)
2. Hekim Dashboard
3. Ana sayfa güncellemeleri
4. Teşekkür sayfası

## Notlar
- Tahmin aracı herkese açık kalacak (mevcut durum korunacak)
- Hekim sistemi tamamen ayrı bir modül olacak
- ML eğitimi için veri toplama odaklı
