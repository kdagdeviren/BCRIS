# Özellik Tahmin Kontrolü - TAMAMLANDI ✅

## Yapılan Değişiklik
Feature (Özellik) modeline `include_in_prediction` (Tahminde Kullan) alanı eklendi. Artık admin panelden hangi değişkenlerin tahminde kullanılacağını kontrol edebilirsiniz.

## Özellik

### Yeni Alan: include_in_prediction
**Model**: `Feature` (rcb_predictor/models.py)

```python
include_in_prediction = models.BooleanField(
    default=True, 
    verbose_name="Tahminde Kullan",
    help_text="Bu özellik tahmin hesaplamasında kullanılsın mı? (False ise değer her zaman 0 kabul edilir)"
)
```

**Varsayılan Değer**: `True` (Tüm özellikler varsayılan olarak tahminde kullanılır)

## Nasıl Çalışır?

### 1. Admin Panelden Kontrol
**Yol**: Admin Panel → Özellikler → Özellik Düzenle

**Liste Görünümü:**
- ✅ "Tahminde Kullan" checkbox'ı direkt listede düzenlenebilir
- 🎨 "Tahmin Durumu" sütunu renklı gösterim:
  - ✓ Kullanılıyor (Yeşil)
  - ✗ Hariç (0 kabul edilir) (Kırmızı)

**Detay Görünümü:**
- "Tahmin Ayarları" bölümü
- Açıklama: "Bu özellik tahmin hesaplamasında kullanılsın mı? Kapalıysa değer her zaman 0 kabul edilir."

**Filtreleme:**
- Tahminde kullanılan/kullanılmayan özellikleri filtreleyebilirsiniz

### 2. Tahmin Hesaplaması
**Dosya**: `rcb_predictor/views.py` - `predict()` fonksiyonu

```python
# Tahminde kullanılmayacak özellikleri kontrol et
excluded_features = Feature.objects.filter(
    is_active=True,
    include_in_prediction=False
).values_list('code', flat=True)

feature_vector = []
for feat in feature_list:
    # Eğer özellik tahminde kullanılmayacaksa 0 kabul et
    if feat in excluded_features:
        feature_vector.append(0)
        print(f"⚠️ {feat} tahminde kullanılmıyor, değer 0 kabul edildi")
    else:
        value = features_dict.get(feat, 0)
        feature_vector.append(int(value))
```

**Mantık:**
1. Kullanıcı formda değer seçer (örn: i11 = 3)
2. Tahmin yapılırken `include_in_prediction` kontrol edilir
3. Eğer `False` ise, kullanıcının seçtiği değer göz ardı edilir
4. Değer otomatik olarak `0` kabul edilir
5. Model bu değerle tahmin yapar

## Kullanım Senaryoları

### Senaryo 1: i11 ve i20'yi Hariç Tutma
**Durum**: i11 ve i20 değişkenleri hesaplamada kullanılmamalı

**Adımlar:**
1. Admin Panel → Özellikler
2. i11 özelliğini bul
3. "Tahminde Kullan" checkbox'ını kaldır
4. Kaydet
5. i20 için aynı işlemi tekrarla

**Sonuç:**
- Kullanıcı i11 ve i20 için değer seçse bile
- Tahmin yapılırken bu değerler 0 kabul edilir
- Model bu değişkenleri görmezden gelir

### Senaryo 2: Geçici Olarak Bir Değişkeni Devre Dışı Bırakma
**Durum**: Bir değişkenin etkisini test etmek istiyorsunuz

**Adımlar:**
1. Admin Panel → Özellikler
2. Test etmek istediğiniz özelliği bul
3. "Tahminde Kullan" checkbox'ını kaldır
4. Kaydet
5. Ana sayfada tahmin yapın
6. Sonuçları gözlemleyin
7. Tekrar aktif etmek için checkbox'ı işaretleyin

### Senaryo 3: Yeni Model Eğitimi İçin Özellik Seçimi
**Durum**: Sadece belirli özellikleri kullanarak model eğitmek istiyorsunuz

**Adımlar:**
1. Admin Panel → Özellikler
2. Kullanmak istemediğiniz özelliklerin "Tahminde Kullan" checkbox'ını kaldırın
3. Kaydet
4. Tahminler artık sadece seçili özelliklerle yapılır

## Admin Panel Görünümü

### Liste Görünümü
```
Kod | Ad (TR)        | Ad (EN)      | Grup      | Sıra | Aktif | Tahminde Kullan | Tahmin Durumu
----|----------------|--------------|-----------|------|-------|-----------------|------------------
i1  | Histolojik Tip | Histological | Patoloji  | 1    | ✓     | ✓               | ✓ Kullanılıyor
i11 | TIL Değeri     | TIL Value    | Patoloji  | 11   | ✓     | ✗               | ✗ Hariç (0 kabul edilir)
i20 | Yaş Grubu      | Age Group    | Demografi | 20   | ✓     | ✗               | ✗ Hariç (0 kabul edilir)
```

### Detay Görünümü
```
┌─ Temel Bilgiler ─────────────────┐
│ Kod: i11                          │
│ Grup: Patoloji                    │
│ Sıra: 11                          │
│ Aktif: ✓                          │
└───────────────────────────────────┘

┌─ İsimler ────────────────────────┐
│ Ad (TR): TIL Değeri               │
│ Ad (EN): TIL Value                │
└───────────────────────────────────┘

┌─ Tahmin Ayarları ────────────────┐
│ ☐ Tahminde Kullan                 │
│                                   │
│ Bu özellik tahmin hesaplamasında  │
│ kullanılsın mı? Kapalıysa değer   │
│ her zaman 0 kabul edilir.         │
└───────────────────────────────────┘
```

## Veritabanı

### Migration
```bash
python manage.py makemigrations rcb_predictor
python manage.py migrate
```

**Oluşturulan Migration**: `0004_feature_include_in_prediction.py`

**Eklenen Alan:**
- Tablo: `rcb_predictor_feature`
- Alan: `include_in_prediction` (BOOLEAN)
- Varsayılan: `TRUE`

### Mevcut Verileri Güncelleme
i11 ve i20'yi hariç tutmak için:

```python
from rcb_predictor.models import Feature

# i11 ve i20'yi tahminde hariç tut
Feature.objects.filter(code__in=['i11', 'i20']).update(include_in_prediction=False)
```

## Avantajlar

✅ **Esneklik**: Hangi özelliklerin kullanılacağını kolayca kontrol edin
✅ **Test**: Özelliklerin etkisini test edin
✅ **Hızlı**: Kod değişikliği gerektirmez, sadece admin panelden
✅ **Görsel**: Renkli durum gösterimi ile kolay takip
✅ **Filtreleme**: Kullanılan/kullanılmayan özellikleri filtreleyin
✅ **Toplu Düzenleme**: Liste görünümünden toplu düzenleme yapın
✅ **Güvenli**: Kullanıcı değer seçse bile, sistem 0 kabul eder

## Örnek Kullanım

### Python Console'dan
```python
from rcb_predictor.models import Feature

# i11'i hariç tut
i11 = Feature.objects.get(code='i11')
i11.include_in_prediction = False
i11.save()

# i20'yi hariç tut
i20 = Feature.objects.get(code='i20')
i20.include_in_prediction = False
i20.save()

# Hariç tutulan özellikleri listele
excluded = Feature.objects.filter(include_in_prediction=False)
for f in excluded:
    print(f"{f.code} - {f.name_tr}")
```

### Admin Panel'den
1. http://localhost:8000/admin/
2. Özellikler → i11
3. "Tahminde Kullan" checkbox'ını kaldır
4. Kaydet
5. Özellikler → i20
6. "Tahminde Kullan" checkbox'ını kaldır
7. Kaydet

## Test

### Test 1: Hariç Tutulan Özellik
1. Admin panelden i11'i hariç tut
2. Ana sayfada i11 için değer 3 seç
3. Tahmin yap
4. Console'da: "⚠️ i11 tahminde kullanılmıyor, değer 0 kabul edildi"
5. Tahmin i11=0 ile yapılır ✅

### Test 2: Dahil Edilen Özellik
1. Admin panelden i11'i dahil et
2. Ana sayfada i11 için değer 3 seç
3. Tahmin yap
4. Tahmin i11=3 ile yapılır ✅

## Dosyalar
- `rcb_predictor/models.py` - Feature modeline `include_in_prediction` alanı eklendi
- `rcb_predictor/admin.py` - Admin panel görünümü güncellendi
- `rcb_predictor/views.py` - `predict()` fonksiyonu güncellendi
- `rcb_predictor/migrations/0004_feature_include_in_prediction.py` - Migration dosyası
