# 🗄️ Veritabanı Tabanlı Sistem - Tam Dokümantasyon

## 🎯 Sistem Mimarisi

### Önceki Sistem (Hard-Coded)
```python
# ❌ Eski Yöntem
CATEGORY_OPTIONS = {
    'i1': [('--- Seçiniz ---', 0), ('İnvaziv Duktal Karsinom', 1), ...]
}
FEATURES_ALL = ['i1', 'i2', 'i3', ...]
```

### Yeni Sistem (Database-Driven)
```python
# ✅ Yeni Yöntem
features = Feature.objects.filter(is_active=True)
options = CategoryOption.objects.filter(feature=feature)
```

## 📊 Veri Akışı

### 1. Sayfa Yükleme
```
Kullanıcı → index() → Veritabanı
                   ↓
            Feature.objects.all()
            CategoryOption.objects.all()
            FeatureGroup.objects.all()
                   ↓
            Template'e gönder
```

### 2. Tahmin İşlemi
```
Kullanıcı → predict() → Veritabanı
                     ↓
              MLModel.objects.get(is_active=True)
              Feature.objects.filter(is_active=True)
                     ↓
              Model yükle (cache)
              Tahmin yap
                     ↓
              TreatmentMessage.objects.filter(...)
                     ↓
              Sonuç döndür
```

### 3. Admin Panel
```
Admin → Django Admin → Veritabanı
                    ↓
             Model güncelle
             Feature ekle/düzenle
             Message ekle/düzenle
                    ↓
             Otomatik yansır
```

## 🔄 Değişiklikler

### views.py Değişiklikleri

#### Önceki (Hard-Coded):
```python
from rcb_predictor.views import CATEGORY_OPTIONS, FEATURES_ALL

def index(request):
    return render(request, 'template.html', {
        'category_options': CATEGORY_OPTIONS,
        'features': FEATURES_ALL
    })
```

#### Şimdi (Database):
```python
from rcb_predictor.models import Feature, CategoryOption

def index(request):
    features = Feature.objects.filter(is_active=True)
    options = get_category_options_dict()
    return render(request, 'template.html', {
        'category_options': options,
        'features': features
    })
```

## 🎨 Admin Panel Özellikleri

### 1. Özellik Yönetimi
- **Ekle/Düzenle/Sil:** Özellikleri admin panelden yönet
- **Sıralama:** Drag & drop ile sıralama (order field)
- **Aktif/Pasif:** Özellikleri aktif/pasif yap
- **Gruplama:** Özellikleri gruplara ayır

### 2. Kategori Seçenekleri
- **Inline Düzenleme:** Özellik sayfasında direkt düzenle
- **Çoklu Dil:** Türkçe ve İngilizce etiketler
- **Değer Yönetimi:** Integer değerler

### 3. Tedavi Mesajları
- **Koşullu Gösterim:** JSON koşullarla
- **Önceliklendirme:** Priority field ile sıralama
- **Çoklu Dil:** TR/EN desteği
- **Mesaj Tipleri:** info, warning, critical

### 4. ML Model Yönetimi
- **Model Upload:** .joblib dosyası yükle
- **Feature List:** JSON formatında
- **Class Order:** JSON formatında
- **Aktif Model:** Tek model aktif olabilir
- **Cache:** Model cache'lenir (performans)

## 🚀 Kullanım Örnekleri

### Yeni Özellik Ekleme

1. **Admin Panele Git:** http://127.0.0.1:8000/admin/
2. **Özellikler → Özellik Ekle**
3. **Bilgileri Doldur:**
   - Kod: i65
   - İsim (TR): Yeni Özellik
   - İsim (EN): New Feature
   - Grup: Patoloji
   - Sıra: 65
   - Aktif: ✓

4. **Kategori Seçenekleri Ekle (Inline):**
   - Etiket: Seçenek 1, Değer: 1
   - Etiket: Seçenek 2, Değer: 2

5. **Kaydet**

✅ Özellik anında frontend'de görünür!

### Yeni Tedavi Mesajı Ekleme

1. **Tedavi → Tedavi Mesajı Ekle**
2. **Bilgileri Doldur:**
   - Mesaj ID: new_message
   - Başlık (TR): Yeni Mesaj
   - Başlık (EN): New Message
   - Mesaj (TR): Mesaj içeriği...
   - Mesaj (EN): Message content...
   - Tip: info
   - Öncelik: 5

3. **Koşullar (JSON):**
```json
{
  "i2": 1,
  "i3": [1, 2]
}
```

4. **Kaydet**

✅ Mesaj koşullar sağlandığında gösterilir!

### Yeni Model Yükleme

1. **Model → ML Model Ekle**
2. **Model Dosyası:** best_model.joblib yükle
3. **Feature List (JSON):**
```json
["i1", "i2", "i3", "i4", ...]
```

4. **Class Order (JSON):**
```json
[0, 1, 2, 3]
```

5. **Aktif Model:** ✓
6. **Kaydet**

✅ Model anında aktif olur!

## 🔧 Teknik Detaylar

### Model Cache Sistemi

```python
_cached_model = None
_cached_model_id = None

def get_active_model():
    global _cached_model, _cached_model_id
    
    active_model = MLModel.objects.filter(is_active=True).first()
    
    # Cache kontrolü
    if _cached_model_id == active_model.id:
        return _cached_model  # Cache'den döndür
    
    # Model'i yükle ve cache'e kaydet
    model = joblib.load(active_model.model_file.path)
    _cached_model = model
    _cached_model_id = active_model.id
    
    return model
```

### Tedavi Mesajı Filtreleme

```python
def get_treatment_messages_from_db(features, lang):
    messages = TreatmentMessage.objects.filter(is_active=True)
    
    for msg in messages:
        conditions = msg.get_conditions()  # JSON → dict
        
        # Koşulları kontrol et
        if all_conditions_match(features, conditions):
            matching_messages.append(msg)
    
    return matching_messages
```

### Kategori Seçenekleri

```python
def get_category_options_dict():
    options_dict = {}
    
    for feature in Feature.objects.filter(is_active=True):
        options_dict[feature.code] = [
            (opt.label_tr, opt.value) 
            for opt in feature.options.all()
        ]
    
    return options_dict
```

## 📈 Performans Optimizasyonları

### 1. Prefetch Related
```python
Feature.objects.prefetch_related('options', 'info')
```

### 2. Select Related
```python
Feature.objects.select_related('group')
```

### 3. Model Cache
- Model bir kez yüklenir
- Cache'den servis edilir
- Model değiştiğinde cache temizlenir

### 4. Query Optimization
- Sadece aktif kayıtlar çekilir
- Gereksiz JOIN'ler önlenir
- Index'ler kullanılır

## 🔐 Güvenlik

### 1. Admin Panel
- ✅ Django authentication
- ✅ Permission system
- ✅ CSRF protection

### 2. File Upload
- ✅ File extension validation
- ✅ File size limit
- ✅ Secure file storage

### 3. JSON Validation
- ✅ JSON syntax kontrolü
- ✅ Type validation
- ✅ Error handling

## 📝 Migration Stratejisi

### İlk Kurulum
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py import_initial_data
```

### Veri Güncelleme
```bash
# Yeni özellik ekleme
python manage.py shell
>>> from rcb_predictor.models import Feature
>>> Feature.objects.create(code='i65', name_tr='Yeni', ...)
```

### Yedekleme
```bash
# Tüm veriyi yedekle
python manage.py dumpdata rcb_predictor > backup.json

# Geri yükle
python manage.py loaddata backup.json
```

## 🎯 Avantajlar

### ✅ Esneklik
- Kod değişikliği olmadan güncelleme
- Admin panelden yönetim
- Anında değişiklik

### ✅ Ölçeklenebilirlik
- Sınırsız özellik
- Sınırsız mesaj
- Çoklu model desteği

### ✅ Bakım Kolaylığı
- Merkezi yönetim
- Versiyon kontrolü
- Audit trail

### ✅ Çoklu Dil
- TR/EN desteği
- Kolay genişletme
- Merkezi çeviri

## 🚨 Önemli Notlar

1. **Model Cache:** Model değiştiğinde sunucuyu yeniden başlatın
2. **Migration:** Yeni model eklendiğinde migration çalıştırın
3. **Backup:** Düzenli yedek alın
4. **Testing:** Değişiklikleri test edin

## 📞 Sorun Giderme

### Model Yüklenmiyor
```bash
# Cache'i temizle
python manage.py shell
>>> from rcb_predictor.views import _cached_model
>>> _cached_model = None
```

### Özellik Görünmüyor
- Admin panelde "Aktif" olduğundan emin olun
- Sıra numarasını kontrol edin
- Sayfayı yenileyin

### Mesaj Gösterilmiyor
- Koşulları kontrol edin
- "Aktif" olduğundan emin olun
- JSON syntax'ını kontrol edin

---

**🎉 Artık tüm sistem veritabanı tabanlı! Hard-code yok!**
