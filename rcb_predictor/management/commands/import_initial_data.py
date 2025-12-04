from django.core.management.base import BaseCommand
from rcb_predictor.models import (
    FeatureGroup, Feature, CategoryOption, VariableInfo,
    TreatmentMessage, MLModel
)
from rcb_predictor.views import (
    CATEGORY_OPTIONS, FEATURES_ALL, FEATURE_NAMES_TR, FEATURE_NAMES_EN
)
from pathlib import Path
import json
import shutil


class Command(BaseCommand):
    help = 'Mevcut JSON ve hard-coded verileri veritabanına aktarır'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Veri aktarımı başlıyor...'))
        
        # 1. Özellik gruplarını oluştur
        self.import_feature_groups()
        
        # 2. Özellikleri oluştur
        self.import_features()
        
        # 3. Kategori seçeneklerini oluştur
        self.import_category_options()
        
        # 4. Değişken bilgilerini oluştur
        self.import_variable_info()
        
        # 5. Tedavi mesajlarını oluştur
        self.import_treatment_messages()
        
        # 6. ML Model'i oluştur
        self.import_ml_model()
        
        self.stdout.write(self.style.SUCCESS('✅ Tüm veriler başarıyla aktarıldı!'))

    def import_feature_groups(self):
        """Özellik gruplarını oluştur"""
        groups = [
            {"name_tr": "Patoloji", "name_en": "Pathology", "order": 1},
            {"name_tr": "Onkoloji", "name_en": "Oncology", "order": 2},
            {"name_tr": "Demografi", "name_en": "Demographics", "order": 3},
            {"name_tr": "Komorbidite", "name_en": "Comorbidity", "order": 4},
            {"name_tr": "Biyokimya", "name_en": "Biochemistry", "order": 5},
            {"name_tr": "Radyoloji", "name_en": "Radiology", "order": 6},
        ]
        
        for group_data in groups:
            group, created = FeatureGroup.objects.get_or_create(
                name_tr=group_data['name_tr'],
                defaults=group_data
            )
            if created:
                self.stdout.write(f"  ✅ Grup oluşturuldu: {group.name_tr}")

    def import_features(self):
        """Özellikleri oluştur"""
        # Grup eşleştirmeleri
        group_ranges = {
            "Patoloji": (0, 11),
            "Onkoloji": (11, 16),
            "Demografi": (16, 21),
            "Komorbidite": (21, 31),
            "Biyokimya": (31, 45),
            "Radyoloji": (45, len(FEATURES_ALL)),
        }
        
        for group_name, (start, end) in group_ranges.items():
            group = FeatureGroup.objects.get(name_tr=group_name)
            
            for i, code in enumerate(FEATURES_ALL[start:end]):
                idx = start + i
                feature, created = Feature.objects.get_or_create(
                    code=code,
                    defaults={
                        'name_tr': FEATURE_NAMES_TR[idx],
                        'name_en': FEATURE_NAMES_EN[idx],
                        'group': group,
                        'order': idx,
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f"  ✅ Özellik oluşturuldu: {code} - {feature.name_tr}")

    def import_category_options(self):
        """Kategori seçeneklerini oluştur"""
        for feature_code, options in CATEGORY_OPTIONS.items():
            try:
                feature = Feature.objects.get(code=feature_code)
                
                for order, (label, value) in enumerate(options):
                    CategoryOption.objects.get_or_create(
                        feature=feature,
                        value=value,
                        defaults={
                            'label_tr': label,
                            'label_en': label,  # Şimdilik aynı
                            'order': order
                        }
                    )
                
                self.stdout.write(f"  ✅ {feature_code} için {len(options)} seçenek eklendi")
            except Feature.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ⚠️ {feature_code} özelliği bulunamadı"))

    def import_variable_info(self):
        """Değişken bilgilerini JSON'dan oku ve oluştur"""
        variable_info_path = Path(__file__).resolve().parent.parent.parent.parent / 'variable_info.json'
        
        if not variable_info_path.exists():
            self.stdout.write(self.style.WARNING('  ⚠️ variable_info.json bulunamadı'))
            return
        
        with open(variable_info_path, 'r', encoding='utf-8') as f:
            variable_data = json.load(f)
        
        for feature_code, info in variable_data.items():
            try:
                feature = Feature.objects.get(code=feature_code)
                
                tr_info = info.get('tr', {})
                en_info = info.get('en', {})
                
                VariableInfo.objects.get_or_create(
                    feature=feature,
                    defaults={
                        'description_tr': tr_info.get('description', ''),
                        'description_en': en_info.get('description', ''),
                        'how_measured_tr': tr_info.get('how_measured', ''),
                        'how_measured_en': en_info.get('how_measured', ''),
                        'clinical_significance_tr': tr_info.get('clinical_significance', ''),
                        'clinical_significance_en': en_info.get('clinical_significance', ''),
                        'how_to_find_tr': tr_info.get('how_to_find', ''),
                        'how_to_find_en': en_info.get('how_to_find', ''),
                    }
                )
                
                self.stdout.write(f"  ✅ {feature_code} için değişken bilgisi eklendi")
            except Feature.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ⚠️ {feature_code} özelliği bulunamadı"))

    def import_treatment_messages(self):
        """Tedavi mesajlarını JSON'dan oku ve oluştur"""
        treatment_path = Path(__file__).resolve().parent.parent.parent.parent / 'treatment_messages.json'
        
        if not treatment_path.exists():
            self.stdout.write(self.style.WARNING('  ⚠️ treatment_messages.json bulunamadı'))
            return
        
        with open(treatment_path, 'r', encoding='utf-8') as f:
            treatment_data = json.load(f)
        
        for msg in treatment_data.get('messages', []):
            title = msg.get('title', '')
            message_text = msg.get('message', '')
            
            # Çift dil desteği kontrolü
            title_tr = title.get('tr', title) if isinstance(title, dict) else title
            title_en = title.get('en', title) if isinstance(title, dict) else title
            message_tr = message_text.get('tr', message_text) if isinstance(message_text, dict) else message_text
            message_en = message_text.get('en', message_text) if isinstance(message_text, dict) else message_text
            
            TreatmentMessage.objects.get_or_create(
                message_id=msg.get('id', ''),
                defaults={
                    'title_tr': title_tr,
                    'title_en': title_en,
                    'message_tr': message_tr,
                    'message_en': message_en,
                    'message_type': msg.get('type', 'info'),
                    'priority': msg.get('priority', 0),
                    'is_active': True,
                    'conditions_json': json.dumps(msg.get('conditions', {}), ensure_ascii=False)
                }
            )
            
            self.stdout.write(f"  ✅ Tedavi mesajı eklendi: {msg.get('id')}")

    def import_ml_model(self):
        """ML Model dosyasını kopyala ve veritabanına ekle"""
        model_path = Path(__file__).resolve().parent.parent.parent.parent / 'models' / 'best_model.joblib'
        feature_list_path = Path(__file__).resolve().parent.parent.parent.parent / 'models' / 'feature_list.json'
        class_order_path = Path(__file__).resolve().parent.parent.parent.parent / 'models' / 'class_order.json'
        
        if not model_path.exists():
            self.stdout.write(self.style.WARNING('  ⚠️ Model dosyası bulunamadı'))
            return
        
        # Feature list ve class order'ı oku
        with open(feature_list_path, 'r') as f:
            feature_list = json.load(f)
        
        with open(class_order_path, 'r') as f:
            class_order = json.load(f)
        
        # Media klasörünü oluştur
        media_models_dir = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'ml_models'
        media_models_dir.mkdir(parents=True, exist_ok=True)
        
        # Model dosyasını kopyala
        dest_path = media_models_dir / 'best_model.joblib'
        shutil.copy(model_path, dest_path)
        
        # Veritabanına ekle
        ml_model, created = MLModel.objects.get_or_create(
            name='Initial Model',
            defaults={
                'description': 'İlk yüklenen LightGBM modeli',
                'model_file': 'ml_models/best_model.joblib',
                'feature_list_json': json.dumps(feature_list, ensure_ascii=False),
                'class_order_json': json.dumps(class_order, ensure_ascii=False),
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f"  ✅ ML Model eklendi: {ml_model.name}")
        else:
            self.stdout.write(f"  ℹ️ ML Model zaten mevcut: {ml_model.name}")
