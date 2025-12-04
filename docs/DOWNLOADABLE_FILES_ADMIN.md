# İndirilebilir Dosyalar - Admin Panel Yönetimi ✅

## Yapılan Değişiklik
Ana sayfadaki indirilebilir dosyalar (Örnek Excel ve Değişken Formatı Bilgi Dosyası) artık admin panelden yönetilebiliyor. Admin panelden yüklenen dosyalar otomatik olarak kullanıcılara sunuluyor.

## Özellikler

### 1. Yeni Model: DownloadableFile
**Dosya**: `rcb_predictor/models.py`

```python
class DownloadableFile(models.Model):
    FILE_TYPES = [
        ('sample_excel', 'Örnek Excel Dosyası'),
        ('variable_format', 'Değişken Formatı Bilgi Dosyası'),
    ]
    
    file_type = models.CharField(max_length=50, choices=FILE_TYPES, unique=True)
    file = models.FileField(upload_to='downloadable_files/')
    description_tr = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
```

**Özellikler:**
- ✅ İki tip dosya: Örnek Excel ve Değişken Formatı
- ✅ Çoklu format desteği: .xlsx, .xls, .pdf, .docx, .doc, .txt
- ✅ Türkçe/İngilizce açıklama alanları
- ✅ Yükleyen kullanıcı takibi
- ✅ Aktif/Pasif durumu
- ✅ Otomatik dosya boyutu hesaplama

### 2. Admin Panel
**Dosya**: `rcb_predictor/admin.py`

**Liste Görünümü:**
- Dosya tipi
- Dosya adı
- Boyut (MB)
- Yüklenme tarihi
- Yükleyen kullanıcı
- Aktif durumu
- İndir butonu

**Detay Görünümü:**
- Dosya yükleme alanı
- Türkçe/İngilizce açıklamalar
- Dosya bilgileri paneli (boyut, indirme linki)
- Otomatik yükleyen kullanıcı kaydı

**Özellikler:**
- 📥 Liste görünümünde direkt indirme butonu
- 📊 Dosya boyutu otomatik hesaplanıyor
- 🎨 Renkli bilgi panelleri (mavi tema)
- 🔒 Sadece bir dosya tipi için bir kayıt (unique constraint)

### 3. View Güncellemeleri
**Dosya**: `rcb_predictor/views.py`

#### download_sample_excel()
```python
# 1. Admin panelden yüklenen dosyayı kontrol et
downloadable_file = DownloadableFile.objects.filter(
    file_type='sample_excel',
    is_active=True
).first()

if downloadable_file and downloadable_file.file:
    # Admin dosyasını döndür
    return response

# 2. Yoksa otomatik oluştur (fallback)
# Veritabanından özellikleri çekip Excel oluştur
```

#### download_variable_format()
```python
# 1. Admin panelden yüklenen dosyayı kontrol et
downloadable_file = DownloadableFile.objects.filter(
    file_type='variable_format',
    is_active=True
).first()

if downloadable_file and downloadable_file.file:
    # Dosya uzantısına göre content type belirle
    # PDF, Word, Excel desteği
    return response

# 2. Yoksa otomatik oluştur (fallback)
```

## Kullanım

### Admin Panelden Dosya Yükleme

1. **Admin Panele Giriş**
   - http://localhost:8000/admin/
   - Kullanıcı adı ve şifre ile giriş

2. **İndirilebilir Dosyalar Bölümü**
   - Sol menüden "İndirilebilir Dosyalar" seçin
   - "İndirilebilir Dosya Ekle" butonuna tıklayın

3. **Dosya Yükleme**
   - **Dosya Tipi**: Örnek Excel Dosyası veya Değişken Formatı Bilgi Dosyası
   - **Dosya**: Yüklenecek dosyayı seçin (.xlsx, .pdf, .docx vb.)
   - **Açıklama (TR)**: Türkçe açıklama (opsiyonel)
   - **Açıklama (EN)**: İngilizce açıklama (opsiyonel)
   - **Aktif**: ✅ İşaretli olmalı
   - "Kaydet" butonuna tıklayın

4. **Dosya Güncelleme**
   - Mevcut kaydı açın
   - Yeni dosya yükleyin
   - "Kaydet" butonuna tıklayın
   - Eski dosya otomatik olarak değiştirilir

### Ana Sayfadan İndirme

**Kullanıcı Deneyimi:**
1. Kullanıcı ana sayfada "📥 Örnek Excel Dosyası İndir" butonuna tıklar
2. Sistem önce admin panelden yüklenen dosyayı kontrol eder
3. Varsa admin dosyasını indirir
4. Yoksa otomatik oluşturulan dosyayı indirir

## Dosya Tipleri

### 1. Örnek Excel Dosyası (sample_excel)
**Amaç**: Kullanıcılara Excel formatında örnek veri göstermek

**Desteklenen Formatlar:**
- .xlsx (Excel 2007+)
- .xls (Excel 97-2003)

**Fallback**: Veritabanından ilk 10 özellik ile otomatik Excel oluşturulur

### 2. Değişken Formatı Bilgi Dosyası (variable_format)
**Amaç**: Tüm değişkenlerin açıklamalarını içeren dokümantasyon

**Desteklenen Formatlar:**
- .xlsx, .xls (Excel)
- .pdf (PDF)
- .docx, .doc (Word)
- .txt (Metin)

**Fallback**: Veritabanından tüm özellikler ile otomatik Excel oluşturulur

## Veritabanı

### Migration
```bash
python manage.py makemigrations rcb_predictor
python manage.py migrate
```

**Oluşturulan Tablo**: `rcb_predictor_downloadablefile`

**Alanlar:**
- id (Primary Key)
- file_type (VARCHAR, UNIQUE)
- file (VARCHAR - dosya yolu)
- description_tr (TEXT)
- description_en (TEXT)
- uploaded_at (DATETIME)
- uploaded_by_id (Foreign Key → auth_user)
- is_active (BOOLEAN)

## Dosya Depolama

**Klasör**: `media/downloadable_files/`

**Örnek Dosya Yolları:**
- `media/downloadable_files/ornek_excel_2025.xlsx`
- `media/downloadable_files/degisken_formati_v2.pdf`

## Avantajlar

✅ **Esneklik**: Admin dosya formatını değiştirebilir (Excel → PDF)
✅ **Güncelleme**: Dosyalar kolayca güncellenebilir
✅ **Versiyon**: Yeni versiyonlar yüklenebilir
✅ **Fallback**: Admin dosya yoksa otomatik oluşturulur
✅ **Çoklu Format**: PDF, Word, Excel desteği
✅ **Takip**: Kim, ne zaman yükledi bilgisi
✅ **Açıklama**: Türkçe/İngilizce açıklamalar

## Test Senaryoları

### Senaryo 1: Admin Dosya Yok
1. Admin panelde dosya yüklenmemiş
2. Kullanıcı "İndir" butonuna tıklar
3. Sistem otomatik Excel oluşturur ✅
4. Kullanıcı dosyayı indirir

### Senaryo 2: Admin Dosya Var
1. Admin panelde örnek Excel yüklendi
2. Kullanıcı "İndir" butonuna tıklar
3. Sistem admin dosyasını döndürür ✅
4. Kullanıcı admin dosyasını indirir

### Senaryo 3: Dosya Güncelleme
1. Admin panelde eski dosya var
2. Admin yeni dosya yükler
3. Kullanıcı "İndir" butonuna tıklar
4. Sistem yeni dosyayı döndürür ✅

### Senaryo 4: Farklı Format
1. Admin PDF dosyası yükler (değişken formatı için)
2. Kullanıcı "İndir" butonuna tıklar
3. Sistem PDF'i döndürür (doğru content-type ile) ✅
4. Kullanıcı PDF'i görüntüler/indirir

## Dosyalar
- `rcb_predictor/models.py` - DownloadableFile modeli
- `rcb_predictor/admin.py` - Admin panel yapılandırması
- `rcb_predictor/views.py` - İndirme view'ları güncellendi
- `rcb_predictor/migrations/0003_downloadablefile.py` - Migration dosyası
