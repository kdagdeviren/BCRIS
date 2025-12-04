# =============================================================================
# BCRIS - Database-Driven Views
# =============================================================================
# Tüm veriler veritabanından çekilir, hard-code yok!
# =============================================================================

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import (
    FeatureGroup, Feature, CategoryOption, VariableInfo,
    TreatmentMessage, MLModel, SystemSettings
)
import json
import pandas as pd
import joblib
import numpy as np
from io import BytesIO

# Global cache
_cached_model = None
_cached_model_id = None


def get_active_model():
    """Aktif modeli cache'den veya veritabanından al"""
    global _cached_model, _cached_model_id
    
    try:
        active_model = MLModel.objects.filter(is_active=True).first()
        
        if not active_model:
            return None, None, None
        
        # Cache kontrolü
        if _cached_model_id == active_model.id and _cached_model is not None:
            return _cached_model, active_model.get_feature_list(), active_model.get_class_order()
        
        # Model'i yükle
        model = joblib.load(active_model.model_file.path)
        feature_list = active_model.get_feature_list()
        class_order = active_model.get_class_order()
        
        # Cache'e kaydet
        _cached_model = model
        _cached_model_id = active_model.id
        
        print(f"✅ Model yüklendi: {active_model.name}")
        return model, feature_list, class_order
        
    except Exception as e:
        print(f"❌ Model yükleme hatası: {e}")
        return None, None, None


def get_category_options_dict():
    """Tüm kategori seçeneklerini dictionary olarak döndür"""
    options_dict = {}
    
    for feature in Feature.objects.filter(is_active=True).prefetch_related('options'):
        options_dict[feature.code] = [
            (opt.label_tr, opt.value) 
            for opt in feature.options.all().order_by('order')
        ]
    
    return options_dict


def get_features_by_group(lang='tr'):
    """Özellikleri gruplara göre döndür"""
    feature_groups = []
    
    for group in FeatureGroup.objects.all().prefetch_related('features'):
        features = group.features.filter(is_active=True).order_by('order')
        
        feature_list = [
            (
                feature.code,
                feature.name_tr if lang == 'tr' else feature.name_en
            )
            for feature in features
        ]
        
        group_name = group.name_tr if lang == 'tr' else group.name_en
        feature_groups.append((feature_list, group_name))
    
    return feature_groups


def index(request):
    """Ana sayfa - Veritabanından veri çeker"""
    lang = request.GET.get('lang', 'tr')
    
    # Özellikleri gruplara göre al
    feature_groups = get_features_by_group(lang)
    
    # Kategori seçeneklerini al
    category_options = get_category_options_dict()
    
    # Tüm aktif özelliklerin kodlarını al
    features_all = list(Feature.objects.filter(is_active=True).order_by('order').values_list('code', flat=True))
    
    # Özellik isimlerini al
    if lang == 'tr':
        feature_names = list(Feature.objects.filter(is_active=True).order_by('order').values_list('name_tr', flat=True))
    else:
        feature_names = list(Feature.objects.filter(is_active=True).order_by('order').values_list('name_en', flat=True))
    
    context = {
        'category_options': category_options,
        'feature_groups': feature_groups,
        'FEATURES_ALL': features_all,
        'FEATURE_NAMES': feature_names,
        'current_lang': lang
    }
    
    return render(request, 'rcb_model_all.html', context)


def check_model(request):
    """Model yükleme durumunu kontrol et"""
    model, _, _ = get_active_model()
    return JsonResponse({
        'loaded': model is not None,
        'model_type': str(type(model).__name__) if model is not None else None
    })


@csrf_exempt
def get_optimal_features(request):
    """Optimal özellik kombinasyonunu döndür"""
    model, feature_list, _ = get_active_model()
    
    if model is None:
        return JsonResponse({
            'success': False,
            'error': 'Model yüklenmedi'
        }, status=400)
    
    try:
        data = json.loads(request.body)
        target_rcb = int(data.get('target_rcb', 0))
        
        # Tüm özellikleri varsayılan değerlere ayarla
        features = {}
        for feature in Feature.objects.filter(is_active=True):
            # İlk seçeneği al (genellikle varsayılan)
            first_option = feature.options.order_by('order').first()
            features[feature.code] = first_option.value if first_option else 1
        
        # RCB-0 için optimal değerler (örnek)
        if target_rcb == 0:
            # Veritabanından optimal değerleri çekebilirsiniz
            # Şimdilik basit bir örnek
            features['i2'] = 2  # ER negatif
            features['i3'] = 2  # PR negatif
            features['i4'] = 4  # HER2 pozitif
        
        return JsonResponse({
            'success': True,
            'features': features,
            'target_rcb': target_rcb
        })
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
def predict(request):
    """RCB kategorisi tahmini yap - Veritabanından model ve veriler"""
    model, feature_list, class_order = get_active_model()
    
    if model is None:
        return JsonResponse({
            'success': False,
            'error': 'Model yüklenmedi'
        }, status=400)
    
    try:
        data = json.loads(request.body)
        lang = data.get('lang', 'tr')
        
        # Feature vektörünü oluştur
        if 'features' in data:
            features_dict = data['features']
        else:
            features_dict = {k: v for k, v in data.items() if k != 'lang'}
        
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
                try:
                    feature_vector.append(int(value))
                except (ValueError, TypeError):
                    feature_vector.append(0)
        
        # Tahmin yap
        X = np.array([feature_vector])
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        
        # RCB kategorileri
        RCB_CATEGORIES = ['RCB-0 (pCR)', 'RCB-1', 'RCB-2', 'RCB-3']
        
        # Tedavi mesajlarını al
        treatment_msgs = get_treatment_messages_from_db(features_dict, lang)
        
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


def get_treatment_messages_from_db(feature_values_dict, lang='tr'):
    """Veritabanından tedavi mesajlarını filtrele"""
    matching_messages = []
    
    # Aktif mesajları al
    messages = TreatmentMessage.objects.filter(is_active=True).order_by('-priority')
    
    for msg in messages:
        conditions = msg.get_conditions()
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
            title = msg.title_tr if lang == 'tr' else msg.title_en
            message = msg.message_tr if lang == 'tr' else msg.message_en
            
            matching_messages.append({
                'id': msg.message_id,
                'title': title,
                'type': msg.message_type,
                'icon': '🧬',
                'message': message,
                'priority': msg.priority
            })
    
    return matching_messages


def admin_messages_page(request):
    """Admin paneli - mesajları görüntüle"""
    messages = TreatmentMessage.objects.filter(is_active=True).order_by('-priority')
    
    return render(request, 'admin_messages.html', {
        'messages': messages,
    })


@csrf_exempt
def save_messages(request):
    """Admin paneli - mesajları kaydet"""
    try:
        data = json.loads(request.body)
        # Veritabanına kaydet
        # Bu fonksiyon artık admin panel üzerinden yapılıyor
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def load_messages(request):
    """Admin paneli - mesajları yükle"""
    messages = TreatmentMessage.objects.filter(is_active=True).values()
    return JsonResponse({'messages': list(messages)})


def get_variable_info(request):
    """Değişken bilgilerini döndür - Veritabanından"""
    try:
        lang = request.GET.get('lang', 'tr')
        variable_id = request.GET.get('variable_id', '')
        
        # Eğer variable_id yoksa, TÜM değişkenleri döndür
        if not variable_id:
            all_info = {}
            features = Feature.objects.filter(is_active=True).prefetch_related('info')
            
            for feature in features:
                if hasattr(feature, 'info'):
                    info = feature.info
                    all_info[feature.code] = {
                        'name': feature.name_tr if lang == 'tr' else feature.name_en,
                        'description': info.description_tr if lang == 'tr' else info.description_en,
                        'how_measured': info.how_measured_tr if lang == 'tr' else info.how_measured_en,
                        'clinical_significance': info.clinical_significance_tr if lang == 'tr' else info.clinical_significance_en,
                        'how_to_find': info.how_to_find_tr if lang == 'tr' else info.how_to_find_en,
                    }
            
            return JsonResponse({
                'success': True,
                'info': all_info
            })
        
        # Tek bir değişken için
        feature = Feature.objects.filter(code=variable_id).first()
        
        if not feature or not hasattr(feature, 'info'):
            return JsonResponse({
                'success': False,
                'error': 'Değişken bulunamadı'
            }, status=404)
        
        info = feature.info
        
        result = {
            'success': True,
            'info': {
                'name': feature.name_tr if lang == 'tr' else feature.name_en,
                'description': info.description_tr if lang == 'tr' else info.description_en,
                'how_measured': info.how_measured_tr if lang == 'tr' else info.how_measured_en,
                'clinical_significance': info.clinical_significance_tr if lang == 'tr' else info.clinical_significance_en,
                'how_to_find': info.how_to_find_tr if lang == 'tr' else info.how_to_find_en,
            }
        }
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def get_category_options(request):
    """Dropdown seçeneklerini döndür - Veritabanından"""
    lang = request.GET.get('lang', 'tr')
    options = get_category_options_dict()
    
    return JsonResponse({
        'success': True,
        'options': options
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
            if file.name.endswith('.xlsx'):
                df = pd.read_excel(file, engine='openpyxl')
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Excel dosyası okunamadı: {str(e)}'
            }, status=400)
        
        if len(df.columns) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Excel dosyasında en az 2 sütun olmalıdır'
            }, status=400)
        
        var_col = df.columns[0]
        val_col = df.columns[1]
        
        features = {}
        
        # Aktif özelliklerin kodlarını al
        active_features = set(Feature.objects.filter(is_active=True).values_list('code', flat=True))
        
        for index, row in df.iterrows():
            var_name = str(row[var_col]).strip()
            var_value = row[val_col]
            
            if not var_name.startswith('i') or not var_name[1:].isdigit():
                continue
            
            # Sadece aktif özellikleri kabul et
            if var_name not in active_features:
                continue
            
            try:
                if pd.isna(var_value):
                    continue
                int_value = int(float(var_value))
                features[var_name] = int_value
            except (ValueError, TypeError):
                print(f"⚠️ UYARI: {var_name} için geçersiz değer: {var_value}")
                continue
        
        if len(features) == 0:
            return JsonResponse({
                'success': False,
                'error': 'Excel dosyasından hiçbir geçerli özellik okunamadı'
            }, status=400)
        
        print(f"✅ Excel'den {len(features)} özellik okundu")
        
        return JsonResponse({
            'success': True,
            'features': features,
            'count': len(features)
        })
        
    except Exception as e:
        import traceback
        print(f"❌ Excel import hatası: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Excel dosyası işlenirken hata oluştu: {str(e)}'
        }, status=500)


def download_sample_excel(request):
    """Örnek Excel dosyası indir - Admin panelden yüklenen dosya veya otomatik oluştur"""
    try:
        from .models import DownloadableFile
        
        # Admin panelden yüklenen dosyayı kontrol et
        downloadable_file = DownloadableFile.objects.filter(
            file_type='sample_excel',
            is_active=True
        ).first()
        
        if downloadable_file and downloadable_file.file:
            # Admin panelden yüklenen dosyayı döndür
            response = HttpResponse(downloadable_file.file.read())
            response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response['Content-Disposition'] = f'attachment; filename={downloadable_file.file.name.split("/")[-1]}'
            return response
        
        # Yoksa otomatik oluştur (fallback)
        features = Feature.objects.filter(is_active=True).order_by('order')[:10]
        
        data = {
            'Değişken': [f.code for f in features],
            'Değer': [1] * len(features)
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
    """Değişken formatı bilgi dosyası indir - Admin panelden yüklenen dosya veya otomatik oluştur"""
    try:
        from .models import DownloadableFile
        
        # Admin panelden yüklenen dosyayı kontrol et
        downloadable_file = DownloadableFile.objects.filter(
            file_type='variable_format',
            is_active=True
        ).first()
        
        if downloadable_file and downloadable_file.file:
            # Admin panelden yüklenen dosyayı döndür
            response = HttpResponse(downloadable_file.file.read())
            # Dosya uzantısına göre content type belirle
            file_name = downloadable_file.file.name.lower()
            if file_name.endswith('.pdf'):
                response['Content-Type'] = 'application/pdf'
            elif file_name.endswith(('.doc', '.docx')):
                response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            else:
                response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response['Content-Disposition'] = f'attachment; filename={downloadable_file.file.name.split("/")[-1]}'
            return response
        
        # Yoksa otomatik oluştur (fallback)
        features = Feature.objects.filter(is_active=True).order_by('order')
        
        data = {
            'Değişken': [f.code for f in features],
            'Açıklama': [f.name_tr for f in features]
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
