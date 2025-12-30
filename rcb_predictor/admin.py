from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import (
    FeatureGroup, Feature, CategoryOption, VariableInfo,
    TreatmentMessage, MLModel, SystemSettings,
    Physician, PatientDataUpload, MLTrainingLog, DownloadableFile
)


@admin.register(FeatureGroup)
class FeatureGroupAdmin(ModelAdmin):
    list_display = ['name_tr', 'name_en', 'order', 'feature_count']
    list_editable = ['order']
    search_fields = ['name_tr', 'name_en']
    ordering = ['order']
    
    @display(description="Özellik Sayısı")
    def feature_count(self, obj):
        return obj.features.count()


class CategoryOptionInline(admin.TabularInline):
    model = CategoryOption
    extra = 1
    fields = ['label_tr', 'label_en', 'value', 'order']


class VariableInfoInline(admin.StackedInline):
    model = VariableInfo
    extra = 0
    fields = [
        'description_tr', 'description_en',
        'how_measured_tr', 'how_measured_en',
        'clinical_significance_tr', 'clinical_significance_en',
        'how_to_find_tr', 'how_to_find_en'
    ]


@admin.register(Feature)
class FeatureAdmin(ModelAdmin):
    list_display = ['code', 'name_tr', 'name_en', 'group', 'order', 'is_active', 'include_in_prediction', 'prediction_status', 'option_count']
    list_filter = ['group', 'is_active', 'include_in_prediction']
    list_editable = ['order', 'is_active', 'include_in_prediction']
    search_fields = ['code', 'name_tr', 'name_en']
    ordering = ['order']
    inlines = [CategoryOptionInline, VariableInfoInline]
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('code', 'group', 'order', 'is_active')
        }),
        ('İsimler', {
            'fields': ('name_tr', 'name_en')
        }),
        ('Tahmin Ayarları', {
            'fields': ('include_in_prediction',),
            'description': 'Bu özellik tahmin hesaplamasında kullanılsın mı? Kapalıysa değer her zaman 0 kabul edilir.'
        }),
    )
    
    @display(description="Seçenek Sayısı")
    def option_count(self, obj):
        return obj.options.count()
    
    @display(description="Tahmin Durumu", ordering='include_in_prediction')
    def prediction_status(self, obj):
        if obj.include_in_prediction:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Kullanılıyor</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Hariç (0 kabul edilir)</span>'
            )


@admin.register(CategoryOption)
class CategoryOptionAdmin(ModelAdmin):
    list_display = ['feature', 'label_tr', 'label_en', 'value', 'order']
    list_filter = ['feature__group']
    list_editable = ['order']
    search_fields = ['label_tr', 'label_en', 'feature__code']
    ordering = ['feature', 'order']


@admin.register(VariableInfo)
class VariableInfoAdmin(ModelAdmin):
    list_display = ['feature', 'get_feature_name']
    search_fields = ['feature__code', 'feature__name_tr', 'description_tr']
    
    fieldsets = (
        ('Özellik', {
            'fields': ('feature',)
        }),
        ('Açıklama', {
            'fields': ('description_tr', 'description_en')
        }),
        ('Nasıl Ölçülür', {
            'fields': ('how_measured_tr', 'how_measured_en')
        }),
        ('Klinik Önemi', {
            'fields': ('clinical_significance_tr', 'clinical_significance_en')
        }),
        ('Nasıl Bulunur', {
            'fields': ('how_to_find_tr', 'how_to_find_en')
        }),
    )
    
    @display(description="Özellik Adı")
    def get_feature_name(self, obj):
        return obj.feature.name_tr


@admin.register(TreatmentMessage)
class TreatmentMessageAdmin(ModelAdmin):
    list_display = ['message_id', 'title_tr', 'message_type', 'priority', 'is_active']
    list_filter = ['message_type', 'is_active']
    list_editable = ['priority', 'is_active']
    search_fields = ['message_id', 'title_tr', 'title_en', 'message_tr']
    ordering = ['-priority', 'message_id']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('message_id', 'message_type', 'priority', 'is_active')
        }),
        ('Başlık', {
            'fields': ('title_tr', 'title_en')
        }),
        ('Mesaj', {
            'fields': ('message_tr', 'message_en')
        }),
        ('Koşullar', {
            'fields': ('conditions_json',),
            'description': 'JSON formatında koşullar. Örnek: {"i2": 1, "i3": [1, 2]}'
        }),
    )


@admin.register(MLModel)
class MLModelAdmin(ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Model Bilgileri', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Model Dosyası', {
            'fields': ('model_file',)
        }),
        ('Konfigürasyon', {
            'fields': ('feature_list_json', 'class_order_json'),
            'description': 'JSON formatında feature list ve class order'
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['activate_model']
    
    @admin.action(description='Seçili modeli aktif yap')
    def activate_model(self, request, queryset):
        # Tüm modelleri pasif yap
        MLModel.objects.update(is_active=False)
        # Seçili modeli aktif yap
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} model aktif yapıldı.")


@admin.register(SystemSettings)
class SystemSettingsAdmin(ModelAdmin):
    list_display = ['key', 'value_preview', 'description']
    search_fields = ['key', 'value', 'description']
    
    @display(description="Değer Önizleme")
    def value_preview(self, obj):
        if len(obj.value) > 50:
            return obj.value[:50] + '...'
        return obj.value


@admin.register(Physician)
class PhysicianAdmin(ModelAdmin):
    list_display = ['full_name', 'institution', 'email', 'approval_status', 'created_at', 'upload_count', 'id_card_download']
    list_filter = ['approval_status', 'is_active', 'created_at']
    search_fields = ['full_name', 'email', 'institution']
    readonly_fields = ['created_at', 'updated_at', 'approval_date', 'id_card_preview']
    
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user', 'full_name', 'email', 'phone')
        }),
        ('Kurum Bilgileri', {
            'fields': ('institution', 'department', 'title')
        }),
        ('Kimlik Doğrulama', {
            'fields': ('id_card_image', 'id_card_preview')
        }),
        ('Onay Durumu', {
            'fields': ('approval_status', 'approval_date', 'approved_by', 'rejection_reason')
        }),
        ('Durum', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_physicians', 'reject_physicians']
    
    @admin.action(description='Seçili hekimleri onayla')
    def approve_physicians(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            approval_status='approved',
            approval_date=timezone.now(),
            approved_by=request.user
        )
        self.message_user(request, f"{count} hekim onaylandı.")
    
    @admin.action(description='Seçili hekimleri reddet')
    def reject_physicians(self, request, queryset):
        count = queryset.update(approval_status='rejected')
        self.message_user(request, f"{count} hekim reddedildi.")
    
    @display(description="Yükleme Sayısı")
    def upload_count(self, obj):
        return obj.uploads.count()
    
    @display(description="Kimlik İndir")
    def id_card_download(self, obj):
        if obj.id_card_image:
            return format_html(
                '<a href="{}" download class="button" style="background: #10b981; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 11px;">📥 İndir</a>',
                obj.id_card_image.url
            )
        return format_html('<span style="color: #999;">-</span>')
    
    @display(description="Kimlik Kartı Önizleme")
    def id_card_preview(self, obj):
        if obj.id_card_image:
            return format_html(
                '<div style="padding: 15px; background: #fff7ed; border: 2px solid #fb923c; border-radius: 8px;">'
                '<p style="margin-bottom: 10px; color: #c2410c; font-weight: 600;">⚠️ KVKK Uyarısı: TC kimlik numarası kapatılmış olmalı!</p>'
                '<img src="{}" style="max-width: 500px; max-height: 300px; border: 2px solid #ddd; border-radius: 8px; display: block; margin-bottom: 10px;" />'
                '<div style="display: flex; gap: 10px; flex-wrap: wrap;">'
                '<a href="{}" target="_blank" class="button" style="background: #fb923c; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; display: inline-block; font-weight: 600;">🔍 Tam Boyutta Görüntüle</a>'
                '<a href="{}" download class="button" style="background: #10b981; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; display: inline-block; font-weight: 600;">📥 Kimlik Kartını İndir</a>'
                '</div>'
                '</div>',
                obj.id_card_image.url,
                obj.id_card_image.url,
                obj.id_card_image.url
            )
        return format_html('<p style="color: #999;">Kimlik kartı yüklenmemiş</p>')


@admin.register(PatientDataUpload)
class PatientDataUploadAdmin(ModelAdmin):
    list_display = ['physician_name', 'original_filename', 'patient_count', 'processing_status', 'uploaded_at', 'download_link']
    list_filter = ['processing_status', 'uploaded_at', 'physician__institution']
    search_fields = ['physician__full_name', 'original_filename', 'description']
    readonly_fields = ['uploaded_at', 'updated_at', 'file_size', 'download_button']
    
    fieldsets = (
        ('Hekim Bilgisi', {
            'fields': ('physician',)
        }),
        ('Dosya Bilgileri', {
            'fields': ('excel_file', 'download_button', 'original_filename', 'file_size', 'patient_count', 'description')
        }),
        ('İşlem Durumu', {
            'fields': ('processing_status', 'processed_by', 'processed_date')
        }),
        ('Admin İşlemleri', {
            'fields': ('admin_notes', 'processed_data_json'),
            'classes': ('collapse',)
        }),
        ('Tarihler', {
            'fields': ('uploaded_at', 'updated_at')
        }),
    )
    
    actions = ['mark_as_reviewing', 'mark_as_processed', 'mark_as_integrated']
    
    @admin.action(description='İnceleniyor olarak işaretle')
    def mark_as_reviewing(self, request, queryset):
        count = queryset.update(processing_status='reviewing')
        self.message_user(request, f"{count} veri seti inceleniyor olarak işaretlendi.")
    
    @admin.action(description='İşlendi olarak işaretle')
    def mark_as_processed(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            processing_status='processed',
            processed_by=request.user,
            processed_date=timezone.now()
        )
        self.message_user(request, f"{count} veri seti işlendi olarak işaretlendi.")
    
    @admin.action(description='ML\'e entegre edildi olarak işaretle')
    def mark_as_integrated(self, request, queryset):
        count = queryset.update(processing_status='integrated')
        self.message_user(request, f"{count} veri seti ML'e entegre edildi.")
    
    @display(description="Hekim")
    def physician_name(self, obj):
        return obj.physician.full_name
    
    @display(description="Dosya İndir")
    def download_link(self, obj):
        if obj.excel_file:
            return format_html(
                '<a href="{}" download class="button" style="background: #417690; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">📥 İndir</a>',
                obj.excel_file.url
            )
        return "-"
    
    @display(description="Dosya İndirme Linki")
    def download_button(self, obj):
        if obj.excel_file:
            file_size_mb = obj.file_size / (1024 * 1024) if obj.file_size else 0
            return format_html(
                '<div style="padding: 15px; background: #f0f9ff; border: 2px solid #0ea5e9; border-radius: 8px;">'
                '<p style="margin-bottom: 10px;"><strong>📄 Dosya:</strong> {}</p>'
                '<p style="margin-bottom: 10px;"><strong>📊 Boyut:</strong> {:.2f} MB</p>'
                '<a href="{}" download class="button" style="background: #0ea5e9; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; display: inline-block; font-weight: 600;">📥 Dosyayı İndir</a>'
                '</div>',
                obj.original_filename,
                file_size_mb,
                obj.excel_file.url
            )
        return format_html('<p style="color: #999;">Dosya yüklenmemiş</p>')


@admin.register(MLTrainingLog)
class MLTrainingLogAdmin(ModelAdmin):
    list_display = ['model', 'training_date', 'total_patients', 'accuracy', 'trained_by']
    list_filter = ['training_date', 'model']
    search_fields = ['model__name', 'notes']
    readonly_fields = ['training_date']
    filter_horizontal = ['data_sources']
    
    fieldsets = (
        ('Model Bilgisi', {
            'fields': ('model', 'trained_by', 'training_date')
        }),
        ('Veri Bilgileri', {
            'fields': ('total_patients', 'training_patients', 'test_patients', 'data_sources')
        }),
        ('Performans Metrikleri', {
            'fields': ('accuracy', 'precision', 'recall', 'f1_score')
        }),
        ('Detaylar', {
            'fields': ('metrics_json', 'notes'),
            'classes': ('collapse',)
        }),
    )



@admin.register(DownloadableFile)
class DownloadableFileAdmin(ModelAdmin):
    list_display = ['file_type_display', 'file_name', 'version', 'file_size', 'uploaded_at', 'uploaded_by', 'is_active', 'download_button']
    list_filter = ['file_type', 'is_active', 'uploaded_at']
    search_fields = ['description_tr', 'description_en', 'version']
    readonly_fields = ['uploaded_at', 'uploaded_by', 'file_size', 'download_panel']
    
    fieldsets = (
        ('Dosya Bilgileri', {
            'fields': ('file_type', 'file', 'version', 'is_active')
        }),
        ('Açıklamalar', {
            'fields': ('description_tr', 'description_en')
        }),
        ('Sistem Bilgileri', {
            'fields': ('uploaded_at', 'uploaded_by', 'file_size', 'download_panel'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description="Dosya Tipi")
    def file_type_display(self, obj):
        return obj.get_file_type_display()
    
    @display(description="Dosya Adı")
    def file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return "-"
    
    @display(description="Boyut (MB)")
    def file_size(self, obj):
        return f"{obj.get_file_size_mb()} MB"
    
    @display(description="İndir")
    def download_button(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" class="button" style="background-color: #4CAF50; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px;">📥 İndir</a>',
                obj.file.url
            )
        return "-"
    
    @display(description="Dosya İndirme")
    def download_panel(self, obj):
        if obj.file:
            version_info = f"<p style='margin: 5px 0;'><strong>Versiyon:</strong> {obj.version}</p>" if obj.version else ""
            return format_html(
                '''
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;">
                    <p style="margin: 0 0 10px 0; font-weight: bold; color: #1976D2;">📁 Dosya Bilgileri</p>
                    <p style="margin: 5px 0;"><strong>Dosya Adı:</strong> {}</p>
                    {}
                    <p style="margin: 5px 0;"><strong>Boyut:</strong> {} MB</p>
                    <p style="margin: 10px 0 0 0;">
                        <a href="{}" class="button" style="background-color: #2196F3; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block;">
                            📥 Dosyayı İndir
                        </a>
                    </p>
                </div>
                ''',
                obj.file.name.split('/')[-1],
                version_info,
                obj.get_file_size_mb(),
                obj.file.url
            )
        return "Dosya yüklenmemiş"
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yeni kayıt
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
