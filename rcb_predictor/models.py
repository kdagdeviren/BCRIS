from django.db import models
from django.core.validators import FileExtensionValidator
import json


class FeatureGroup(models.Model):
    """Özellik grupları (Patoloji, Onkoloji, vb.)"""
    name_tr = models.CharField(max_length=100, verbose_name="Grup Adı (TR)")
    name_en = models.CharField(max_length=100, verbose_name="Grup Adı (EN)")
    order = models.IntegerField(default=0, verbose_name="Sıra")
    
    class Meta:
        verbose_name = "Özellik Grubu"
        verbose_name_plural = "Özellik Grupları"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name_tr} ({self.order})"


class Feature(models.Model):
    """Özellikler (i1, i2, vb.)"""
    code = models.CharField(max_length=10, unique=True, verbose_name="Kod (i1, i2, ...)")
    name_tr = models.CharField(max_length=200, verbose_name="Özellik Adı (TR)")
    name_en = models.CharField(max_length=200, verbose_name="Özellik Adı (EN)")
    group = models.ForeignKey(FeatureGroup, on_delete=models.CASCADE, related_name='features', verbose_name="Grup")
    order = models.IntegerField(default=0, verbose_name="Sıra")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    include_in_prediction = models.BooleanField(
        default=True, 
        verbose_name="Tahminde Kullan",
        help_text="Bu özellik tahmin hesaplamasında kullanılsın mı? (False ise değer her zaman 0 kabul edilir)"
    )
    
    class Meta:
        verbose_name = "Özellik"
        verbose_name_plural = "Özellikler"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.code} - {self.name_tr}"


class CategoryOption(models.Model):
    """Kategori seçenekleri (dropdown değerleri)"""
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='options', verbose_name="Özellik")
    label_tr = models.CharField(max_length=200, verbose_name="Etiket (TR)")
    label_en = models.CharField(max_length=200, verbose_name="Etiket (EN)", blank=True)
    value = models.IntegerField(verbose_name="Değer")
    order = models.IntegerField(default=0, verbose_name="Sıra")
    
    class Meta:
        verbose_name = "Kategori Seçeneği"
        verbose_name_plural = "Kategori Seçenekleri"
        ordering = ['feature', 'order']
    
    def __str__(self):
        return f"{self.feature.code} - {self.label_tr} ({self.value})"


class VariableInfo(models.Model):
    """Değişken bilgileri"""
    feature = models.OneToOneField(Feature, on_delete=models.CASCADE, related_name='info', verbose_name="Özellik")
    description_tr = models.TextField(verbose_name="Açıklama (TR)")
    description_en = models.TextField(verbose_name="Açıklama (EN)", blank=True)
    how_measured_tr = models.TextField(verbose_name="Nasıl Ölçülür (TR)")
    how_measured_en = models.TextField(verbose_name="Nasıl Ölçülür (EN)", blank=True)
    clinical_significance_tr = models.TextField(verbose_name="Klinik Önemi (TR)")
    clinical_significance_en = models.TextField(verbose_name="Klinik Önemi (EN)", blank=True)
    how_to_find_tr = models.TextField(verbose_name="Nasıl Bulunur (TR)")
    how_to_find_en = models.TextField(verbose_name="Nasıl Bulunur (EN)", blank=True)
    
    class Meta:
        verbose_name = "Değişken Bilgisi"
        verbose_name_plural = "Değişken Bilgileri"
    
    def __str__(self):
        return f"Bilgi: {self.feature.code}"


class TreatmentMessage(models.Model):
    """Tedavi mesajları"""
    MESSAGE_TYPES = [
        ('info', 'Bilgi'),
        ('warning', 'Uyarı'),
        ('critical', 'Kritik'),
    ]
    
    message_id = models.CharField(max_length=100, unique=True, verbose_name="Mesaj ID")
    title_tr = models.CharField(max_length=200, verbose_name="Başlık (TR)")
    title_en = models.CharField(max_length=200, verbose_name="Başlık (EN)", blank=True)
    message_tr = models.TextField(verbose_name="Mesaj (TR)")
    message_en = models.TextField(verbose_name="Mesaj (EN)", blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='info', verbose_name="Mesaj Tipi")
    priority = models.IntegerField(default=0, verbose_name="Öncelik")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Koşullar JSON olarak saklanacak
    conditions_json = models.TextField(verbose_name="Koşullar (JSON)", help_text='Örnek: {"i2": 1, "i3": [1, 2]}')
    
    class Meta:
        verbose_name = "Tedavi Mesajı"
        verbose_name_plural = "Tedavi Mesajları"
        ordering = ['-priority', 'message_id']
    
    def __str__(self):
        return f"{self.message_id} - {self.title_tr}"
    
    def get_conditions(self):
        """JSON koşulları dict olarak döndür"""
        try:
            return json.loads(self.conditions_json)
        except:
            return {}
    
    def set_conditions(self, conditions_dict):
        """Dict'i JSON olarak kaydet"""
        self.conditions_json = json.dumps(conditions_dict, ensure_ascii=False, indent=2)


class MLModel(models.Model):
    """Machine Learning Model dosyaları"""
    name = models.CharField(max_length=100, verbose_name="Model Adı")
    description = models.TextField(verbose_name="Açıklama", blank=True)
    model_file = models.FileField(
        upload_to='ml_models/',
        validators=[FileExtensionValidator(allowed_extensions=['joblib', 'pkl'])],
        verbose_name="Model Dosyası (.joblib)"
    )
    feature_list_json = models.TextField(verbose_name="Feature List (JSON)", help_text="Özellik listesi")
    class_order_json = models.TextField(verbose_name="Class Order (JSON)", help_text="Sınıf sırası [0, 1, 2, 3]")
    is_active = models.BooleanField(default=False, verbose_name="Aktif Model")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "ML Model"
        verbose_name_plural = "ML Modeller"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} {'(Aktif)' if self.is_active else ''}"
    
    def save(self, *args, **kwargs):
        # Eğer bu model aktif yapılıyorsa, diğerlerini pasif yap
        if self.is_active:
            MLModel.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    def get_feature_list(self):
        """JSON feature list'i list olarak döndür"""
        try:
            return json.loads(self.feature_list_json)
        except:
            return []
    
    def get_class_order(self):
        """JSON class order'ı list olarak döndür"""
        try:
            return json.loads(self.class_order_json)
        except:
            return [0, 1, 2, 3]


class SystemSettings(models.Model):
    """Sistem ayarları"""
    key = models.CharField(max_length=100, unique=True, verbose_name="Anahtar")
    value = models.TextField(verbose_name="Değer")
    description = models.TextField(verbose_name="Açıklama", blank=True)
    
    class Meta:
        verbose_name = "Sistem Ayarı"
        verbose_name_plural = "Sistem Ayarları"
    
    def __str__(self):
        return self.key


class Physician(models.Model):
    """Hekim kullanıcıları"""
    APPROVAL_STATUS = [
        ('pending', 'Onay Bekliyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ]
    
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='physician_profile', verbose_name="Kullanıcı")
    full_name = models.CharField(max_length=200, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta")
    phone = models.CharField(max_length=20, verbose_name="Telefon", blank=True)
    institution = models.CharField(max_length=200, verbose_name="Kurum/Hastane")
    department = models.CharField(max_length=100, verbose_name="Bölüm", blank=True)
    title = models.CharField(max_length=100, verbose_name="Ünvan", blank=True)
    
    # Kimlik doğrulama
    id_card_image = models.ImageField(
        upload_to='physician_ids/',
        verbose_name="Kimlik Kartı (TC Kapalı)",
        help_text="Sağlık Bakanlığı onaylı kimlik kartı - TC kimlik numarası kapatılmalı (KVKK)"
    )
    
    # Onay durumu
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default='pending',
        verbose_name="Onay Durumu"
    )
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name="Onay Tarihi")
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_physicians',
        verbose_name="Onaylayan"
    )
    rejection_reason = models.TextField(blank=True, verbose_name="Red Nedeni")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    class Meta:
        verbose_name = "Hekim"
        verbose_name_plural = "Hekimler"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.institution} ({self.get_approval_status_display()})"
    
    @property
    def is_approved(self):
        return self.approval_status == 'approved'


class PatientDataUpload(models.Model):
    """Hekimler tarafından yüklenen hasta verileri"""
    PROCESSING_STATUS = [
        ('pending', 'İşlem Bekliyor'),
        ('reviewing', 'İnceleniyor'),
        ('processed', 'İşlendi'),
        ('rejected', 'Reddedildi'),
        ('integrated', 'ML\'e Entegre Edildi'),
    ]
    
    physician = models.ForeignKey(Physician, on_delete=models.CASCADE, related_name='uploads', verbose_name="Hekim")
    
    # Dosya bilgileri
    excel_file = models.FileField(
        upload_to='patient_data/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls', 'csv'])],
        verbose_name="Excel Dosyası"
    )
    original_filename = models.CharField(max_length=255, verbose_name="Orijinal Dosya Adı")
    file_size = models.IntegerField(verbose_name="Dosya Boyutu (bytes)", null=True)
    
    # Veri bilgileri
    patient_count = models.IntegerField(default=0, verbose_name="Hasta Sayısı")
    description = models.TextField(blank=True, verbose_name="Açıklama", help_text="Veri seti hakkında notlar")
    
    # İşlem durumu
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS,
        default='pending',
        verbose_name="İşlem Durumu"
    )
    
    # Admin notları
    admin_notes = models.TextField(blank=True, verbose_name="Admin Notları")
    processed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_uploads',
        verbose_name="İşleyen"
    )
    processed_date = models.DateTimeField(null=True, blank=True, verbose_name="İşlenme Tarihi")
    
    # İşlenmiş veri
    processed_data_json = models.TextField(
        blank=True,
        verbose_name="İşlenmiş Veri (JSON)",
        help_text="ML formatına çevrilmiş veri"
    )
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Yüklenme Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Hasta Verisi"
        verbose_name_plural = "Hasta Verileri"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.physician.full_name} - {self.original_filename} ({self.patient_count} hasta)"
    
    def get_processed_data(self):
        """JSON veriyi dict olarak döndür"""
        try:
            return json.loads(self.processed_data_json) if self.processed_data_json else {}
        except:
            return {}
    
    def set_processed_data(self, data_dict):
        """Dict'i JSON olarak kaydet"""
        self.processed_data_json = json.dumps(data_dict, ensure_ascii=False, indent=2)


class MLTrainingLog(models.Model):
    """ML model eğitim logları"""
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='training_logs', verbose_name="Model")
    
    # Eğitim bilgileri
    training_date = models.DateTimeField(auto_now_add=True, verbose_name="Eğitim Tarihi")
    trained_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="Eğiten")
    
    # Veri bilgileri
    total_patients = models.IntegerField(verbose_name="Toplam Hasta Sayısı")
    training_patients = models.IntegerField(verbose_name="Eğitim Hasta Sayısı")
    test_patients = models.IntegerField(verbose_name="Test Hasta Sayısı")
    
    # Performans metrikleri
    accuracy = models.FloatField(verbose_name="Doğruluk (%)")
    precision = models.FloatField(null=True, blank=True, verbose_name="Precision")
    recall = models.FloatField(null=True, blank=True, verbose_name="Recall")
    f1_score = models.FloatField(null=True, blank=True, verbose_name="F1 Score")
    
    # Detaylar
    metrics_json = models.TextField(blank=True, verbose_name="Detaylı Metrikler (JSON)")
    notes = models.TextField(blank=True, verbose_name="Notlar")
    
    # Kullanılan veri setleri
    data_sources = models.ManyToManyField(
        PatientDataUpload,
        blank=True,
        related_name='training_logs',
        verbose_name="Kullanılan Veri Setleri"
    )
    
    class Meta:
        verbose_name = "ML Eğitim Logu"
        verbose_name_plural = "ML Eğitim Logları"
        ordering = ['-training_date']
    
    def __str__(self):
        return f"{self.model.name} - {self.training_date.strftime('%Y-%m-%d')} - Doğruluk: {self.accuracy}%"



class DownloadableFile(models.Model):
    """İndirilebilir dosyalar (Örnek Excel, Değişken Formatı vb.)"""
    FILE_TYPES = [
        ('sample_excel', 'Örnek Excel Dosyası'),
        ('variable_format', 'Değişken Formatı Bilgi Dosyası'),
    ]
    
    file_type = models.CharField(max_length=50, choices=FILE_TYPES, unique=True, verbose_name="Dosya Tipi")
    file = models.FileField(
        upload_to='downloadable_files/',
        verbose_name="Dosya",
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls', 'pdf', 'docx', 'doc', 'txt'])]
    )
    description_tr = models.TextField(blank=True, verbose_name="Açıklama (TR)")
    description_en = models.TextField(blank=True, verbose_name="Açıklama (EN)")
    uploaded_at = models.DateTimeField(auto_now=True, verbose_name="Yüklenme Tarihi")
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Yükleyen")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    class Meta:
        verbose_name = "İndirilebilir Dosya"
        verbose_name_plural = "İndirilebilir Dosyalar"
        ordering = ['file_type']
    
    def __str__(self):
        return f"{self.get_file_type_display()} - {self.file.name}"
    
    def get_file_size_mb(self):
        """Dosya boyutunu MB olarak döndür"""
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return 0
