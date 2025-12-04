# =============================================================================
# Breast Cancer Response Intelligence System (BCRIS) - Django Version
# =============================================================================
# AI-Powered Residual Cancer Burden Prediction Platform
# LightGBM-based RCB category prediction web application
# =============================================================================

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import pandas as pd
import joblib
import numpy as np
from io import BytesIO
from pathlib import Path

# Model ve dosyalar
model = None
feature_list = None
class_order = None
treatment_messages = None

# Model ve JSON dosyalarının yolları
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'models' / 'best_model.joblib'
FEATURE_LIST_PATH = BASE_DIR / 'models' / 'feature_list.json'
CLASS_ORDER_PATH = BASE_DIR / 'models' / 'class_order.json'
TREATMENT_MESSAGES_PATH = BASE_DIR / 'treatment_messages.json'
VARIABLE_INFO_PATH = BASE_DIR / 'variable_info.json'

def load_model_files():
    """Model ve JSON dosyalarını yükle"""
    global model, feature_list, class_order, treatment_messages
    
    print("\n" + "="*60)
    print("Model ve JSON Dosyaları Yükleniyor...")
    print("="*60)
    
    # Model dosyasını yükle
    if MODEL_PATH.exists():
        try:
            model = joblib.load(MODEL_PATH)
            print(f"✅ Model dosyası yüklendi: {MODEL_PATH}")
            print(f"   Model tipi: {type(model).__name__}")
        except Exception as e:
            print(f"❌ Model dosyası yüklenemedi: {e}")
            model = None
    else:
        print(f"⚠️ Model dosyası bulunamadı: {MODEL_PATH}")
    
    # feature_list.json dosyasını yükle
    if FEATURE_LIST_PATH.exists():
        try:
            with open(FEATURE_LIST_PATH, 'r', encoding='utf-8') as f:
                feature_list = json.load(f)
            print(f"✅ Feature list yüklendi: {len(feature_list)} özellik")
        except Exception as e:
            print(f"❌ Feature list yüklenemedi: {e}")
            feature_list = None
    else:
        print(f"⚠️ Feature list dosyası bulunamadı: {FEATURE_LIST_PATH}")
    
    # class_order.json dosyasını yükle
    if CLASS_ORDER_PATH.exists():
        try:
            with open(CLASS_ORDER_PATH, 'r', encoding='utf-8') as f:
                class_order = json.load(f)
            print(f"✅ Class order yüklendi: {class_order}")
        except Exception as e:
            print(f"❌ Class order yüklenemedi: {e}")
            class_order = None
    else:
        print(f"⚠️ Class order dosyası bulunamadı: {CLASS_ORDER_PATH}")
    
    # treatment_messages.json dosyasını yükle
    if TREATMENT_MESSAGES_PATH.exists():
        try:
            with open(TREATMENT_MESSAGES_PATH, 'r', encoding='utf-8') as f:
                treatment_messages = json.load(f)
            print(f"✅ Treatment messages yüklendi")
        except json.JSONDecodeError as e:
            print(f"⚠️ Tedavi mesajları JSON hatası: {e}")
            treatment_messages = {'messages': [], 'settings': {'max_messages': 5, 'default_icon': '🧬', 'show_all_matching': True}}
        except Exception as e:
            print(f"❌ Treatment messages yüklenemedi: {e}")
            treatment_messages = {'messages': [], 'settings': {'max_messages': 5, 'default_icon': '🧬', 'show_all_matching': True}}
    else:
        print(f"⚠️ Treatment messages dosyası bulunamadı: {TREATMENT_MESSAGES_PATH}")
        treatment_messages = {'messages': [], 'settings': {'max_messages': 5, 'default_icon': '🧬', 'show_all_matching': True}}
    
    print("="*60)
    print(f"Model durumu: {'✅ Yüklü' if model is not None else '❌ Yüklenmedi'}")
    print(f"Feature list durumu: {'✅ Yüklü' if feature_list is not None else '❌ Yüklenmedi'}")
    print(f"Class order durumu: {'✅ Yüklü' if class_order is not None else '❌ Yüklenmedi'}")
    print("="*60 + "\n")

# Uygulama başlatıldığında model ve JSON dosyalarını yükle
load_model_files()

# Kategori seçenekleri
CATEGORY_OPTIONS = {
    'i1': [('--- Seçiniz ---', 0), ('İnvaziv Duktal Karsinom', 1), ('İnvaziv Lobüler Karsinom', 2), ('Mikst (Duktal + Lobüler)', 3), ('DCIS', 4), ('Diğer Nadir Tipler', 5)],
    'i2': [('--- Seçiniz ---', 0), ('Güçlü Pozitif', 1), ('Negatif', 2), ('Pozitif', 3), ('Zayıf Pozitif', 4)],
    'i3': [('--- Seçiniz ---', 0), ('Güçlü Pozitif', 1), ('Negatif', 2), ('Pozitif', 3), ('Zayıf Pozitif', 4)],
    'i4': [('--- Seçiniz ---', 0), ('Ekvokal', 1), ('HER2-düşük', 2), ('Negatif', 3), ('Pozitif', 4)],
    'i5': [('--- Seçiniz ---', 0), ('HER2-Düşük', 1), ('HER2-Zengin', 2), ('Luminal B (HER2 Negatif)', 4), ('Luminal B (HER2 Pozitif)', 5), ('Luminal A', 5), ('Triple Negatif', 6)],
    'i6': [('--- Seçiniz ---', 0), ('Düşük', 1), ('Orta', 2), ('Yüksek', 3)],
    'i7': [('--- Seçiniz ---', 0), ('Derece 1', 1), ('Derece 2', 2), ('Derece 3', 3)],
    'i8': [('--- Seçiniz ---', 0), ('Derece 1', 1), ('Derece 2', 2), ('Derece 3', 3)],
    'i9': [('--- Seçiniz ---', 0), ('Derece 1', 1), ('Derece 2', 2), ('Derece 3', 3)],
    'i10': [('--- Seçiniz ---', 0), ('G1', 1), ('G2', 2), ('G3', 3)],
    'i12': [('--- Seçiniz ---', 0), ('<%10', 1), ('%10-%50', 2), ('>%50', 3)],
    'i13': [('--- Seçiniz ---', 0), ('Var', 1), ('Yok', 2)],
    'i14': [('--- Seçiniz ---', 0), ('Yok', 1), ('Lenf Nodu', 2), ('Dermal Lenfatik', 3), ('Uzak Metastaz', 4)],
    'i15': [('--- Seçiniz ---', 0), ('Evre IA', 1), ('Evre IB', 2), ('Evre IIA', 3), ('Evre IIB', 4), ('Evre IIIA', 5), ('Evre IIIB', 6), ('Evre IIIC', 7), ('Evre IV', 8)],
    'i16': [('--- Seçiniz ---', 0), ('Sağ', 1), ('Sol', 2)],
    'i17': [('--- Seçiniz ---', 0), ('Zayıf', 1), ('Normal kilolu', 2), ('Fazla kilolu', 3), ('Obez (1. Derece)', 4), ('Obez (2. Derece)', 5), ('Obez (3. Derece)', 6)],
    'i18': [('--- Seçiniz ---', 0), ('Genç Erişkin', 1), ('Erken Orta Yaş', 2), ('Orta Yaş', 3), ('Geç Orta Yaş', 4), ('Yaşlı', 5), ('İleri Yaşlı', 6)],
    'i19': [('--- Seçiniz ---', 0), ('0(-)', 1), ('0(+)', 2), ('A(-)', 3), ('A(+)', 4), ('B(-)', 5), ('B(+)', 6), ('AB(-)', 7), ('AB(+)', 8)],
    'i21': [('--- Seçiniz ---', 0), ('Var', 1), ('Yok', 2)],
    'i22': [('--- Seçiniz ---', 0), ('Var', 1), ('Yok', 2)],
    'i23': [('--- Seçiniz ---', 0), ('Var', 1), ('Yok', 2)],
    'i24': [('--- Seçiniz ---', 0), ('Var', 1), ('Yok', 2)],
    'i25': [('--- Seçiniz ---', 0), ('Var', 1), ('Yok', 2)],
    'i26': [('--- Seçiniz ---', 0), ('Var', 1), ('Yok', 2)],
    'i27': [('--- Seçiniz ---', 0), ('Var', 1), ('Yok', 2)],
    'i28': [('--- Seçiniz ---', 0), ('Var', 1), ('Yok', 2)],
    'i29': [('--- Seçiniz ---', 0), ('Var', 1), ('Yok', 2)],
    'i30': [('--- Seçiniz ---', 0), ('Var', 1), ('Yok', 2)],
    'i31': [('--- Seçiniz ---', 0), ('Normal', 1), ('Düşük', 2), ('Yüksek', 3)],
    'i32': [('--- Seçiniz ---', 0), ('Normal', 1), ('Yüksek', 3)],
    'i33': [('--- Seçiniz ---', 0), ('Normal', 1), ('Yüksek', 3)],
    'i34': [('--- Seçiniz ---', 0), ('Normal', 1), ('Düşük', 2), ('Yüksek', 3)],
    'i35': [('--- Seçiniz ---', 0), ('Normal', 1), ('Yüksek', 3)],
    'i36': [('--- Seçiniz ---', 0), ('Normal', 1), ('Yüksek', 3)],
    'i37': [('--- Seçiniz ---', 0), ('Normal', 1), ('Yüksek', 3)],
    'i38': [('--- Seçiniz ---', 0), ('Normal', 1), ('Düşük', 2), ('Yüksek', 3)],
    'i39': [('--- Seçiniz ---', 0), ('Normal', 1), ('Düşük', 2), ('Yüksek', 3)],
    'i40': [('--- Seçiniz ---', 0), ('Normal', 1), ('Yüksek', 3)],
    'i41': [('--- Seçiniz ---', 0), ('Normal', 1), ('Düşük', 2), ('Yüksek', 3)],
    'i42': [('--- Seçiniz ---', 0), ('Normal', 1), ('Düşük', 2), ('Yüksek', 3)],
    'i43': [('--- Seçiniz ---', 0), ('Normal', 1), ('Düşük', 2), ('Yüksek', 3)],
    'i44': [('--- Seçiniz ---', 0), ('Normal', 1), ('Düşük', 2)],
    'i45': [('--- Seçiniz ---', 0), ('Düşük', 1), ('Orta', 2), ('Yüksek', 3)],
    'i46': [('--- Seçiniz ---', 0), ('Antrasiklin + Taksan', 1), ('Sadece Antrasiklin', 2), ('Sadece Taksan', 3), ('Platin Eklenenler', 4)],
    'i47': [('--- Seçiniz ---', 0), ('Tam Kür', 1), ('Eksik Kür', 2), ('Fazla Kür', 3)],
    'i48': [('--- Seçiniz ---', 0), ('BI-RADS 0', 1), ('BI-RADS 1', 2), ('BI-RADS 2', 3), ('BI-RADS 4A', 4), ('BI-RADS 4B', 5), ('BI-RADS 4C', 6), ('BI-RADS 5', 7)],
    'i49': [('--- Seçiniz ---', 0), ('A', 1), ('B', 2), ('C', 3), ('D', 4)],
    'i50': [('--- Seçiniz ---', 0), ('Üst Dış Kuadran (UOQ)', 1), ('Üst İç Kuadran (UIQ)', 2), ('Alt Dış Kuadran (LOQ)', 3), ('Alt İç Kuadran (LIQ)', 4), ('Retroareolar / Santral', 5), ('Diğer/Yardımcı Yönler', 6)],
    'i51': [('--- Seçiniz ---', 0), ('Architectural Distortion', 1), ('Asimetri', 2), ('Kalsifikasyon', 3), ('Solid kitle', 4)],
    'i52': [('--- Seçiniz ---', 0), ('Kalsifikasyona Eşlik Eden', 1), ('Kitleye Eşlik Eden', 2), ('Tek Başına', 3)],
    'i53': [('--- Seçiniz ---', 0), ('Düzensiz', 1), ('Oval', 2), ('Yuvarlak', 3)],
    'i54': [('--- Seçiniz ---', 0), ('Belirsiz', 1), ('Düzensiz', 2), ('Düzgün', 3), ('Mikrolobüle', 4), ('Spiküle', 5)],
    'i55': [('--- Seçiniz ---', 0), ('Düşük Dansite', 1), ('Eş Dansite', 2), ('Yüksek Dansite', 3)],
    'i56': [('--- Seçiniz ---', 0), ('Amorf', 1), ('Coarse/Popcorn', 2), ('İnce Lineer', 3), ('Kalsifikasyon Yok', 4), ('Kesin Benign', 5), ('Pleomorfik', 6), ('Yuvarlak/Punctate', 7)],
    'i57': [('--- Seçiniz ---', 0), ('Bölgesel', 1), ('Diffüz', 2), ('Gruplu', 3), ('Kalsifikasyon Yok', 4), ('Lineer', 5), ('Segmental', 6)],
    'i58': [('--- Seçiniz ---', 0), ('Asimetri Yok', 1), ('Fokal', 2), ('Gelişen', 3), ('Global', 4), ('Tek Projeksiyon', 5)],
    'i59': [('--- Seçiniz ---', 0), ('Multifokal', 1), ('Multisentrik', 2), ('Yok/Tek Odak', 3), ('Değerlendirilemedi', 4)],
    'i60': [('--- Seçiniz ---', 0), ('Bilinmiyor', 1), ('Evet', 2), ('Hayır', 3)],
    'i61': [('--- Seçiniz ---', 0), ('Evet', 1), ('Hayır', 2), ('Tek Projeksiyon - Şüpheli', 3)],
    'i62': [('--- Seçiniz ---', 0), ('Evet', 1), ('Hayır', 2), ('Tek Projeksiyon - Şüpheli', 3)],
    'i63': [('--- Seçiniz ---', 0), ('Evet', 1), ('Hayır', 2)],
    'i64': [('--- Seçiniz ---', 0), ('Evet', 1), ('Hayır', 2)]
}

FEATURES_ALL = [
    'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9', 'i10', 'i12',
    'i13', 'i14', 'i15', 'i46', 'i47',
    'i16', 'i17', 'i18', 'i19', 'i45',
    'i21', 'i22', 'i23', 'i24', 'i25', 'i26', 'i27', 'i28', 'i29', 'i30',
    'i31', 'i32', 'i33', 'i34', 'i35', 'i36', 'i37', 'i38', 'i39', 'i40', 'i41', 'i42', 'i43', 'i44',
    'i48', 'i49', 'i50', 'i51', 'i52', 'i53', 'i54', 'i55', 'i56', 'i57', 'i58', 'i59', 'i60', 'i61', 'i62', 'i63', 'i64'
]

FEATURE_NAMES_TR = [
    'Histolojik Tip', 'ER', 'PR', 'HER2', 'Moleküler Tip', 'Ki-67',
    'Tübül Derecesi', 'Nükleer Derece', 'Mitotik Derece', 'Histolojik Grade', 'TIL Değeri',
    'Metastaz Durumu', 'Metastaz Yeri', 'Tanı Evresi', 'Rejim', 'Kür Yoğunluk',
    'Hangi Meme', 'VKI Sınıfı', 'Yaş Grubu', 'Kan Grubu', 'Güneşten Yararlanma',
    'HT', 'DM', 'KOAH', 'Sigara', 'Ailede Meme CA', 'Tiroid', 'Retinopati', 'Nöropati', 'Osteoporoz', 'Depresyon',
    'ALP', 'ALT', 'AST', 'BUN', 'CA15-3', 'CEA', 'CRP', 'GGT', 'Glukoz', 'HbA1c', 'Kreatinin', 'LDH', 'TSH', 'e-GFR',
    'BI-RADS', 'Meme Dansitesi', 'Lokalizasyon', 'Lezyon Türü', 'Mimari',
    'Kitle Şekli', 'Kitle Konturu', 'Kitle Dansitesi', 'Kalsifikasyon Morfolojisi',
    'Kalsifikasyon Dağılımı', 'Asimetri', 'Multifokalite', '2 Yıldır Stabil',
    'Cilt Çekintisi', 'Meme Başı Retraksiyonu', 'Ameliyat Öyküsü', 'Kozmetik Implant'
]

FEATURE_NAMES_EN = [
    'Histological Type', 'ER', 'PR', 'HER2', 'Molecular Type', 'Ki-67',
    'Tubule Grade', 'Nuclear Grade', 'Mitotic Grade', 'Histological Grade', 'TIL Value',
    'Metastasis Status', 'Metastasis Site', 'Diagnosis Stage', 'Regimen', 'Cure Intensity',
    'Which Breast', 'BMI Class', 'Age Group', 'Blood Group', 'Sun Exposure',
    'HT', 'DM', 'COPD', 'Smoking', 'Family History of Breast CA', 'Thyroid', 'Retinopathy', 'Neuropathy', 'Osteoporosis', 'Depression',
    'ALP', 'ALT', 'AST', 'BUN', 'CA15-3', 'CEA', 'CRP', 'GGT', 'Glucose', 'HbA1c', 'Creatinine', 'LDH', 'TSH', 'e-GFR',
    'BI-RADS', 'Breast Density', 'Localization', 'Lesion Type', 'Architecture',
    'Mass Shape', 'Mass Contour', 'Mass Density', 'Calcification Morphology',
    'Calcification Distribution', 'Asymmetry', 'Multifocality', 'Stable for 2 Years',
    'Skin Retraction', 'Nipple Retraction', 'Surgery History', 'Cosmetic Implant'
]

RCB_CATEGORIES = ['RCB-0 (pCR)', 'RCB-1', 'RCB-2', 'RCB-3']


# View fonksiyonları
def index(request):
    """Ana sayfa"""
    lang = request.GET.get('lang', 'tr')
    
    # Dil'e göre feature names seç
    feature_names = FEATURE_NAMES_TR if lang == 'tr' else FEATURE_NAMES_EN
    
    # Tab isimleri
    tab_names_tr = ["Patoloji", "Onkoloji", "Demografi", "Komorbidite", "Biyokimya", "Radyoloji"]
    tab_names_en = ["Pathology", "Oncology", "Demographics", "Comorbidity", "Biochemistry", "Radiology"]
    tab_names = tab_names_tr if lang == 'tr' else tab_names_en
    
    # Özellikleri zip'leyerek gönder
    feature_groups = [
        (list(zip(FEATURES_ALL[:11], feature_names[:11])), tab_names[0]),
        (list(zip(FEATURES_ALL[11:16], feature_names[11:16])), tab_names[1]),
        (list(zip(FEATURES_ALL[16:21], feature_names[16:21])), tab_names[2]),
        (list(zip(FEATURES_ALL[21:31], feature_names[21:31])), tab_names[3]),
        (list(zip(FEATURES_ALL[31:45], feature_names[31:45])), tab_names[4]),
        (list(zip(FEATURES_ALL[45:], feature_names[45:])), tab_names[5])
    ]
    
    context = {
        'category_options': CATEGORY_OPTIONS,
        'feature_groups': feature_groups,
        'FEATURES_ALL': FEATURES_ALL,
        'FEATURE_NAMES': feature_names,
        'current_lang': lang
    }
    
    return render(request, 'rcb_model_all.html', context)


def check_model(request):
    """Model yükleme durumunu kontrol et"""
    global model
    return JsonResponse({
        'loaded': model is not None,
        'model_type': str(type(model).__name__) if model is not None else None
    })


@csrf_exempt
def get_optimal_features(request):
    """Belirli bir RCB kategorisi için optimal özellik kombinasyonunu döndür"""
    global model, feature_list
    
    if model is None:
        return JsonResponse({
            'success': False,
            'error': 'Model yüklenmedi'
        }, status=400)
    
    try:
        data = json.loads(request.body)
        target_rcb = data.get('target_rcb', 0)
        
        # target_rcb'yi kesinlikle integer'a çevir
        try:
            target_rcb = int(target_rcb)
        except (ValueError, TypeError):
            print(f"⚠️ UYARI: target_rcb integer'a çevrilemedi: {target_rcb}, varsayılan olarak 0 kullanılıyor")
            target_rcb = 0
        
        # Literatüre dayalı optimal özellik kombinasyonları
        optimal_features = get_optimal_features_by_rcb(target_rcb)
        
        return JsonResponse({
            'success': True,
            'features': optimal_features,
            'target_rcb': target_rcb
        })
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


def get_optimal_features_by_rcb(target_rcb):
    """Literatüre dayalı optimal özellik kombinasyonlarını döndür"""
    try:
        target_rcb = int(target_rcb)
    except (ValueError, TypeError):
        target_rcb = 0
    
    target_feature_list = feature_list if feature_list else FEATURES_ALL
    
    # Tüm özellikleri varsayılan değerlere ayarla
    features = {}
    for feat in target_feature_list:
        if feat in CATEGORY_OPTIONS and len(CATEGORY_OPTIONS[feat]) > 1:
            features[feat] = CATEGORY_OPTIONS[feat][1][1] if len(CATEGORY_OPTIONS[feat]) > 1 else 1
        else:
            features[feat] = 1
    
    # RCB kategorisine göre optimal değerleri ayarla (sadece RCB-0 örneği)
    if target_rcb == 0:
        features['i1'] = 1  # İnvaziv Duktal Karsinom
        features['i2'] = 2  # ER negatif
        features['i3'] = 2  # PR negatif
        features['i4'] = 4  # HER2 pozitif
        features['i5'] = 2  # HER2-Zengin
        features['i6'] = 3  # Ki-67 yüksek
        # ... diğer özellikler
    
    return features


@csrf_exempt
def predict(request):
    """RCB kategorisi tahmini yap"""
    global model, feature_list
    
    if model is None:
        return JsonResponse({
            'success': False,
            'error': 'Model yüklenmedi'
        }, status=400)
    
    try:
        data = json.loads(request.body)
        lang = data.get('lang', 'tr')
        
        # JavaScript'ten gelen veri formatını kontrol et
        # Eğer 'features' key'i varsa onu kullan, yoksa tüm data'yı features olarak kabul et
        if 'features' in data:
            features_dict = data['features']
        else:
            # lang key'ini çıkar, geri kalanlar features
            features_dict = {k: v for k, v in data.items() if k != 'lang'}
        
        # Feature vektörünü oluştur
        target_feature_list = feature_list if feature_list else FEATURES_ALL
        feature_vector = []
        for feat in target_feature_list:
            value = features_dict.get(feat, 0)
            try:
                feature_vector.append(int(value))
            except (ValueError, TypeError):
                feature_vector.append(0)
        
        # Tahmin yap
        X = np.array([feature_vector])
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        
        # Tedavi mesajlarını ekle
        treatment_msgs = get_treatment_messages(features_dict, lang)
        
        # Flask ile uyumlu response formatı
        result = {
            'success': True,
            'prediction': int(prediction),
            'prediction_label': RCB_CATEGORIES[int(prediction)],
            'probabilities': probabilities.tolist(),
            'categories': RCB_CATEGORIES,
            'treatment_messages': treatment_msgs
        }
        
        return JsonResponse(result)
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


def get_treatment_messages(feature_values_dict, lang='tr'):
    """Seçilen özelliklere göre uygun tedavi mesajlarını filtrele"""
    global treatment_messages
    
    if treatment_messages is None or 'messages' not in treatment_messages:
        return []
    
    if lang not in ['tr', 'en']:
        lang = 'tr'
    
    matching_messages = []
    
    for msg in treatment_messages.get('messages', []):
        conditions = msg.get('conditions', {})
        matches = True
        
        for feature, expected_value in conditions.items():
            actual_value = feature_values_dict.get(feature, 0)
            
            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    matches = False
                    break
            else:
                if actual_value != expected_value:
                    matches = False
                    break
        
        if matches:
            title = msg.get('title', '')
            message = msg.get('message', '')
            
            if isinstance(title, dict):
                title = title.get(lang, title.get('tr', ''))
            
            if isinstance(message, dict):
                message = message.get(lang, message.get('tr', ''))
            
            matching_messages.append({
                'id': msg.get('id', ''),
                'title': title,
                'type': msg.get('type', 'info'),
                'icon': '🧬',
                'message': message,
                'priority': msg.get('priority', 0)
            })
    
    # Priority'ye göre sırala
    matching_messages.sort(key=lambda x: x.get('priority', 0), reverse=True)
    
    return matching_messages


def admin_messages_page(request):
    """Admin paneli - mesajları görüntüle"""
    global treatment_messages
    if treatment_messages is None:
        treatment_messages = {'messages': [], 'settings': {'max_messages': 5, 'default_icon': '🧬', 'show_all_matching': True}}
    
    return render(request, 'admin_messages.html', {
        'messages': treatment_messages.get('messages', []),
        'settings': treatment_messages.get('settings', {})
    })


@csrf_exempt
def save_messages(request):
    """Admin paneli - mesajları kaydet"""
    global treatment_messages
    try:
        data = json.loads(request.body)
        treatment_messages = data
        with open(TREATMENT_MESSAGES_PATH, 'w', encoding='utf-8') as f:
            json.dump(treatment_messages, f, ensure_ascii=False, indent=2)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def load_messages(request):
    """Admin paneli - mesajları yükle"""
    global treatment_messages
    return JsonResponse(treatment_messages)


def get_variable_info(request):
    """Değişken bilgilerini döndür"""
    try:
        lang = request.GET.get('lang', 'tr')
        variable_id = request.GET.get('variable_id', '')
        
        if not VARIABLE_INFO_PATH.exists():
            return JsonResponse({
                'success': False,
                'error': 'Değişken bilgileri dosyası bulunamadı'
            }, status=404)
        
        with open(VARIABLE_INFO_PATH, 'r', encoding='utf-8') as f:
            variable_info = json.load(f)
        
        if variable_id and variable_id in variable_info:
            info = variable_info[variable_id].get(lang, variable_info[variable_id].get('tr', {}))
            return JsonResponse({
                'success': True,
                'info': info
            })
        
        return JsonResponse({
            'success': False,
            'error': 'Değişken bulunamadı'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def get_category_options(request):
    """Dropdown seçeneklerini döndür"""
    lang = request.GET.get('lang', 'tr')
    return JsonResponse({
        'success': True,
        'options': CATEGORY_OPTIONS
    })


@csrf_exempt
def import_excel(request):
    """Excel dosyasından özellik değerlerini oku"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Sadece POST metodu desteklenir'
        }, status=405)
    
    try:
        # Flask'ta 'excel_file' adıyla gönderiliyor
        if 'excel_file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Excel dosyası bulunamadı'
            }, status=400)
        
        file = request.FILES['excel_file']
        
        if not file.name:
            return JsonResponse({
                'success': False,
                'error': 'Dosya seçilmedi'
            }, status=400)
        
        # Excel dosyasını oku
        try:
            # Pandas ile Excel oku (hem .xlsx hem .xls destekler)
            if file.name.endswith('.xlsx'):
                df = pd.read_excel(file, engine='openpyxl')
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Excel dosyası okunamadı: {str(e)}. Lütfen geçerli bir Excel dosyası yükleyin.'
            }, status=400)
        
        # Excel formatını kontrol et
        if len(df.columns) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Excel dosyasında en az 2 sütun olmalıdır (Değişken, Değer)'
            }, status=400)
        
        # İlk iki sütunu al
        var_col = df.columns[0]
        val_col = df.columns[1]
        
        # Özellikleri dictionary'ye çevir
        features = {}
        
        for index, row in df.iterrows():
            var_name = str(row[var_col]).strip()
            var_value = row[val_col]
            
            # Değişken adını kontrol et (i1, i2, ... formatında olmalı)
            if not var_name.startswith('i') or not var_name[1:].isdigit():
                continue  # Geçersiz değişken adı, atla
            
            # Değeri integer'a çevir
            try:
                if pd.isna(var_value):
                    continue  # Boş değer, atla
                int_value = int(float(var_value))  # Float olarak oku, sonra int'e çevir
                features[var_name] = int_value
            except (ValueError, TypeError):
                print(f"⚠️ UYARI: {var_name} için geçersiz değer: {var_value}")
                continue
        
        if len(features) == 0:
            return JsonResponse({
                'success': False,
                'error': 'Excel dosyasından hiçbir geçerli özellik okunamadı. Lütfen dosya formatını kontrol edin.'
            }, status=400)
        
        print(f"✅ Excel'den {len(features)} özellik okundu")
        
        return JsonResponse({
            'success': True,
            'features': features,
            'count': len(features)
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Excel import hatası: {str(e)}")
        print(error_trace)
        return JsonResponse({
            'success': False,
            'error': f'Excel dosyası işlenirken hata oluştu: {str(e)}'
        }, status=500)


def download_sample_excel(request):
    """Örnek Excel dosyası indir"""
    try:
        # Örnek Excel dosyası oluştur
        data = {
            'Değişken': FEATURES_ALL[:10],
            'Değer': [1] * 10
        }
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Özellikler')
        
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=ornek_veri.xlsx'
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def download_variable_format(request):
    """Değişken formatı bilgi dosyası indir"""
    try:
        # Değişken formatı bilgisi oluştur
        data = {
            'Değişken': FEATURES_ALL,
            'Açıklama': FEATURE_NAMES_TR
        }
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Değişken Formatı')
        
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=degisken_formati.xlsx'
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
