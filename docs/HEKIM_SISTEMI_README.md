# 🏥 BCRIS Hekim Sistemi - Kurulum ve Kullanım

## 📌 Genel Bakış

BCRIS projesine eklenen yeni hekim sistemi, hekimlerin hasta verilerini sisteme yüklemesini ve makine öğrenmesi modelinin gelişimine katkıda bulunmasını sağlar.

## ✨ Özellikler

### 1. Hekim Kayıt ve Giriş Sistemi
- ✅ Kayıt formu (Sign Up)
- ✅ Giriş formu (Login)
- ✅ Kimlik kartı yükleme (KVKK uyumlu)
- ✅ Admin onay sistemi

### 2. Hekim Paneli
- ✅ Dashboard (istatistikler)
- ✅ Veri yükleme formu
- ✅ Yüklemeler listesi
- ✅ Durum takibi

### 3. Admin Paneli
- ✅ Hekim onaylama
- ✅ Veri inceleme
- ✅ Durum güncelleme
- ✅ İstatistikler

### 4. Teşekkür Sayfası
- ✅ Katkıda bulunan hekimler
- ✅ İstatistikler
- ✅ Kurum bilgileri

## 🚀 Kurulum

### 1. Veritabanı Migrasyonları
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Admin Kullanıcısı Oluşturma
```bash
python manage.py createsuperuser
```

### 3. Sunucuyu Başlatma
```bash
python manage.py runserver
```

## 📖 Kullanım

### Hekim Kaydı
1. Tarayıcıda `http://localhost:8000/signup/` adresine gidin
2. Formu doldurun:
   - Kullanıcı adı
   - Ad Soyad
   - Email
   - Telefon (opsiyonel)
   - Kurum/Hastane
   - Bölüm (opsiyonel)
   - Ünvan (opsiyonel)
   - Şifre
   - Kimlik kartı (TC kapatılmış)
3. "Kayıt Ol" butonuna tıklayın
4. Admin onayını bekleyin

### Admin Onayı
1. Admin paneline girin: `http://localhost:8000/admin/`
2. "Hekimler" bölümüne gidin
3. Bekleyen hekimi seçin
4. Kimlik kartını kontrol edin
5. "Seçili hekimleri onayla" action'ını kullanın

### Hekim Girişi
1. `http://localhost:8000/login/` adresine gidin
2. Kullanıcı adı ve şifrenizi girin
3. Dashboard'a yönlendirileceksiniz

### Veri Yükleme
1. Dashboard'dan "Yeni Veri Yükle" butonuna tıklayın
2. Excel dosyasını seçin (.xlsx, .xls, .csv)
3. Açıklama ekleyin (opsiyonel)
4. "Yükle" butonuna tıklayın
5. Admin incelemesini bekleyin

### Admin Veri İnceleme
1. Admin panelinde "Hasta Verileri" bölümüne gidin
2. Yüklenen veriyi seçin
3. Durumu güncelleyin:
   - İnceleniyor
   - İşlendi
   - ML'e Entegre Edildi
4. Notlar ekleyin

## 🔗 URL'ler

| Sayfa | URL | Erişim |
|-------|-----|--------|
| Ana Sayfa | `/` | Herkese açık |
| Hekim Kaydı | `/signup/` | Herkese açık |
| Hekim Girişi | `/login/` | Herkese açık |
| Hekim Dashboard | `/physician/dashboard/` | Giriş gerekli |
| Veri Yükleme | `/physician/upload/` | Giriş gerekli |
| Yüklemeler | `/physician/uploads/` | Giriş gerekli |
| Teşekkür | `/thanks/` | Herkese açık |
| Admin Paneli | `/admin/` | Admin |

## 📊 Veritabanı Modelleri

### Physician (Hekim)
```python
- user: OneToOne(User)
- full_name: CharField
- email: EmailField
- phone: CharField
- institution: CharField
- department: CharField
- title: CharField
- id_card_image: ImageField
- approval_status: CharField (pending/approved/rejected)
- approval_date: DateTimeField
- approved_by: ForeignKey(User)
- rejection_reason: TextField
```

### PatientDataUpload (Hasta Verisi)
```python
- physician: ForeignKey(Physician)
- excel_file: FileField
- original_filename: CharField
- file_size: IntegerField
- patient_count: IntegerField
- description: TextField
- processing_status: CharField (pending/reviewing/processed/rejected/integrated)
- admin_notes: TextField
- processed_by: ForeignKey(User)
- processed_date: DateTimeField
- processed_data_json: TextField
```

### MLTrainingLog (ML Eğitim Logu)
```python
- model: ForeignKey(MLModel)
- training_date: DateTimeField
- trained_by: ForeignKey(User)
- total_patients: IntegerField
- training_patients: IntegerField
- test_patients: IntegerField
- accuracy: FloatField
- precision: FloatField
- recall: FloatField
- f1_score: FloatField
- metrics_json: TextField
- notes: TextField
- data_sources: ManyToMany(PatientDataUpload)
```

## 🔐 Güvenlik

### KVKK Uyumu
- TC kimlik numarası kapatılmalı
- Hasta kimlik bilgileri içermemeli
- Sadece anonim veri kabul edilir

### Erişim Kontrolü
- Tüm hekimler admin onayı gerektirir
- Sadece onaylı hekimler veri yükleyebilir
- Admin paneli sadece admin kullanıcılar için

### Dosya Güvenliği
- Sadece Excel/CSV dosyaları kabul edilir
- Dosya boyutu kontrolü
- Güvenli dosya yükleme

## 🎨 Tasarım

### Renkler
- Primary: `#667eea` (Mor)
- Secondary: `#2c5f7c` (Mavi)
- Success: `#48bb78` (Yeşil)
- Warning: `#ed8936` (Turuncu)
- Error: `#e53e3e` (Kırmızı)

### Responsive
- Mobil uyumlu
- Tablet uyumlu
- Desktop optimize

## 📝 Notlar

### Tahmin Aracı
- Ana sayfadaki tahmin aracı herkese açık kalır
- Excel yükleme özelliği herkese açık kalır
- Giriş gerektirmez

### Hekim Sistemi
- Tamamen ayrı bir modül
- ML eğitimi için veri toplama odaklı
- Admin kontrolü altında

### Admin Paneli
- Unfold ile modern görünüm
- Türkçe dil desteği
- Kolay kullanım

## 🐛 Sorun Giderme

### Kimlik Kartı Yüklenmiyor
- Dosya boyutunu kontrol edin (max 5MB)
- Dosya formatını kontrol edin (jpg, png, jpeg)
- Tarayıcı konsolunu kontrol edin

### Giriş Yapamıyorum
- Kullanıcı adı ve şifrenizi kontrol edin
- Hesabınızın onaylandığından emin olun
- Admin ile iletişime geçin

### Veri Yüklenmiyor
- Dosya formatını kontrol edin (.xlsx, .xls, .csv)
- Dosya boyutunu kontrol edin
- Excel formatının doğru olduğundan emin olun

## 📞 Destek

Herhangi bir sorun veya soru için:
- Admin panelinden mesaj gönderin
- Email: [admin email]
- Telefon: [admin telefon]

## 🔄 Güncellemeler

### v1.0.0 (2024-12-04)
- ✅ Hekim kayıt sistemi
- ✅ Hekim giriş sistemi
- ✅ Hekim paneli
- ✅ Veri yükleme sistemi
- ✅ Admin onay sistemi
- ✅ Teşekkür sayfası

### Gelecek Özellikler
- 📧 Email bildirimleri
- 🏢 Kurum logoları
- 📊 Gelişmiş istatistikler
- 📱 Mobil uygulama
- 🌍 Çoklu dil desteği

## 📄 Lisans

Bu proje BCRIS projesi kapsamındadır.

## 👥 Katkıda Bulunanlar

- Proje Sahibi: [İsim]
- Geliştirici: Kiro AI
- Tarih: 4 Aralık 2024
