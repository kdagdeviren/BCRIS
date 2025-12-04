# 🎨 BCRIS Admin Panel Kullanım Kılavuzu

## 🚀 Giriş

BCRIS Admin Paneli, **Django Unfold** teması ile modern ve kullanıcı dostu bir arayüze sahiptir. Tüm sistem ayarları, özellikler, tedavi mesajları ve ML modelleri bu panelden yönetilebilir.

## 📍 Admin Panele Erişim

**URL:** http://127.0.0.1:8000/admin/

**Kullanıcı Adı:** `admin`  
**Şifre:** `admin123`

## 📊 Panel Bölümleri

### 1. 🗂️ Özellikler (Features)

#### Özellik Grupları (Feature Groups)
- **Patoloji, Onkoloji, Demografi, Komorbidite, Biyokimya, Radyoloji**
- Grupların sırasını değiştirebilirsiniz
- Her grubun Türkçe ve İngilizce adları vardır

#### Özellikler (Features)
- **62 adet özellik** (i1, i2, i3, ...)
- Her özellik için:
  - Kod (i1, i2, vb.)
  - Türkçe ve İngilizce isim
  - Hangi gruba ait olduğu
  - Sıra numarası
  - Aktif/Pasif durumu
  
**Özellik Düzenleme:**
- Özelliğe tıklayın
- Kategori seçeneklerini inline olarak ekleyin/düzenleyin
- Değişken bilgilerini inline olarak ekleyin/düzenleyin

#### Kategori Seçenekleri (Category Options)
- Her özellik için dropdown değerleri
- Örnek: ER için "Güçlü Pozitif", "Negatif", "Pozitif", "Zayıf Pozitif"
- Türkçe ve İngilizce etiketler
- Değer (integer)
- Sıra numarası

#### Değişken Bilgileri (Variable Info)
- Her özellik için detaylı açıklama
- **Açıklama:** Özelliğin ne olduğu
- **Nasıl Ölçülür:** Ölçüm yöntemi
- **Klinik Önemi:** Klinik açıdan önemi
- **Nasıl Bulunur:** Raporda nerede bulunur

### 2. 💊 Tedavi Mesajları (Treatment Messages)

- **150+ tedavi mesajı** otomatik import edildi
- Her mesaj için:
  - **Mesaj ID:** Benzersiz tanımlayıcı
  - **Başlık:** Türkçe ve İngilizce
  - **Mesaj:** Türkçe ve İngilizce
  - **Mesaj Tipi:** info, warning, critical
  - **Öncelik:** Yüksek öncelikli mesajlar önce gösterilir
  - **Koşullar (JSON):** Hangi özellik değerlerinde gösterileceği

**Koşul Örneği:**
```json
{
  "i2": 1,
  "i3": [1, 2]
}
```
Bu mesaj, i2=1 VE i3=1 veya i3=2 olduğunda gösterilir.

**Yeni Mesaj Ekleme:**
1. "Tedavi Mesajı Ekle" butonuna tıklayın
2. Tüm alanları doldurun
3. Koşulları JSON formatında girin
4. Kaydedin

### 3. 🧠 ML Modeller (ML Models)

- **Model Dosyası:** .joblib formatında model yükleyin
- **Feature List:** JSON formatında özellik listesi
- **Class Order:** JSON formatında sınıf sırası [0, 1, 2, 3]
- **Aktif Model:** Sadece bir model aktif olabilir

**Yeni Model Yükleme:**
1. "ML Model Ekle" butonuna tıklayın
2. Model dosyasını yükleyin (.joblib)
3. Feature list'i JSON olarak girin:
```json
["i1", "i2", "i3", ...]
```
4. Class order'ı JSON olarak girin:
```json
[0, 1, 2, 3]
```
5. "Aktif Model" işaretleyin
6. Kaydedin

**Model Değiştirme:**
- Liste görünümünde modeli seçin
- Actions menüsünden "Seçili modeli aktif yap" seçin
- Diğer modeller otomatik olarak pasif olur

### 4. ⚙️ Sistem Ayarları (System Settings)

- Key-Value formatında ayarlar
- Örnek kullanımlar:
  - `max_upload_size`: "10MB"
  - `default_language`: "tr"
  - `enable_notifications`: "true"

## 🎨 Unfold Tema Özellikleri

### Modern Arayüz
- ✅ Koyu/Açık tema desteği
- ✅ Responsive tasarım
- ✅ Material Design ikonları
- ✅ Gelişmiş arama ve filtreleme
- ✅ Inline düzenleme

### Dashboard
- **İstatistikler:**
  - Toplam Özellik Sayısı
  - Aktif Özellik Sayısı
  - Tedavi Mesajı Sayısı
  - Aktif Model Sayısı

### Sidebar Navigasyon
- **Özellikler** bölümü
  - Özellik Grupları
  - Özellikler
  - Kategori Seçenekleri
  - Değişken Bilgileri
- **Tedavi** bölümü
  - Tedavi Mesajları
- **Model** bölümü
  - ML Modeller
- **Sistem** bölümü
  - Sistem Ayarları

## 🔄 Veri Akışı

### Frontend → Backend → Database

1. **Kullanıcı** frontend'de özellik seçer
2. **Frontend** `/predict` endpoint'ine POST isteği gönderir
3. **Backend** veritabanından aktif modeli alır
4. **Backend** veritabanından özellikleri ve tedavi mesajlarını alır
5. **Backend** tahmin yapar ve sonucu döndürür
6. **Frontend** sonuçları gösterir

### Hard-Code'dan Database'e Geçiş

**Eski Sistem (Hard-Coded):**
```python
CATEGORY_OPTIONS = {
    'i1': [('--- Seçiniz ---', 0), ('İnvaziv Duktal Karsinom', 1), ...]
}
```

**Yeni Sistem (Database):**
```python
# Admin panelden yönetiliyor
feature = Feature.objects.get(code='i1')
options = feature.options.all()
```

## 📝 Önemli Notlar

### Veri Güvenliği
- ✅ Tüm veriler veritabanında güvenle saklanır
- ✅ Admin panele sadece yetkili kullanıcılar erişebilir
- ✅ Model dosyaları `media/ml_models/` klasöründe saklanır

### Performans
- ✅ Veritabanı sorguları optimize edilmiştir
- ✅ Aktif model cache'lenir
- ✅ Inline düzenleme ile hızlı güncelleme

### Yedekleme
```bash
# Veritabanı yedeği
python manage.py dumpdata > backup.json

# Veritabanı geri yükleme
python manage.py loaddata backup.json
```

## 🛠️ Gelişmiş Kullanım

### Toplu İşlemler
- Liste görünümünde birden fazla kayıt seçin
- Actions menüsünden işlem seçin
- Örnek: Birden fazla mesajı aynı anda aktif/pasif yapma

### Arama ve Filtreleme
- Üst kısımdaki arama kutusunu kullanın
- Sağ taraftaki filtreleri kullanın
- Örnek: Sadece aktif özellikleri göster

### İnline Düzenleme
- Liste görünümünde bazı alanlar direkt düzenlenebilir
- Örnek: Sıra numaralarını direkt değiştirme

## 🎯 Hızlı Başlangıç

1. **Admin panele giriş yapın:** http://127.0.0.1:8000/admin/
2. **Özellikleri inceleyin:** Özellikler → Özellikler
3. **Tedavi mesajlarını görün:** Tedavi → Tedavi Mesajları
4. **Modeli kontrol edin:** Model → ML Modeller
5. **Yeni özellik ekleyin:** Özellikler → Özellik Ekle
6. **Yeni mesaj ekleyin:** Tedavi → Tedavi Mesajı Ekle

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. Sunucu loglarını kontrol edin
2. Admin panel hata mesajlarını okuyun
3. Database migration'ları kontrol edin: `python manage.py showmigrations`

---

**Not:** Bu admin panel, tüm sistem ayarlarını veritabanından yönetir. Artık kod değişikliği yapmadan tüm özellikleri, mesajları ve modelleri güncelleyebilirsiniz! 🎉
