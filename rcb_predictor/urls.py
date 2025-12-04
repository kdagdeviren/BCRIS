from django.urls import path
from . import views, views_auth

app_name = 'rcb_predictor'

urlpatterns = [
    # Ana sayfa ve tahmin (herkese açık)
    path('', views.index, name='index'),
    path('check_model/', views.check_model, name='check_model'),
    path('get_optimal_features/', views.get_optimal_features, name='get_optimal_features'),
    path('predict/', views.predict, name='predict'),
    path('get_variable_info/', views.get_variable_info, name='get_variable_info'),
    path('get_category_options/', views.get_category_options, name='get_category_options'),
    path('import_excel/', views.import_excel, name='import_excel'),
    path('download_sample_excel/', views.download_sample_excel, name='download_sample_excel'),
    path('download_variable_format/', views.download_variable_format, name='download_variable_format'),
    
    # Admin mesajları
    path('admin/messages/', views.admin_messages_page, name='admin_messages'),
    path('admin/messages/save/', views.save_messages, name='save_messages'),
    path('admin/messages/load/', views.load_messages, name='load_messages'),
    
    # Hekim authentication
    path('login/', views_auth.physician_login_view, name='physician_login'),
    path('signup/', views_auth.physician_signup, name='physician_signup'),
    path('logout/', views_auth.physician_logout_view, name='physician_logout'),
    
    # Hekim paneli (giriş gerekli)
    path('physician/dashboard/', views_auth.physician_dashboard, name='physician_dashboard'),
    path('physician/upload/', views_auth.physician_upload_data, name='physician_upload_data'),
    path('physician/uploads/', views_auth.physician_uploads_list, name='physician_uploads_list'),
    
    # Teşekkür sayfası (herkese açık)
    path('thanks/', views_auth.thanks_page, name='thanks'),
    
    # Trailing slash olmayan versiyonlar (eski Flask URL'leri için)
    path('check_model', views.check_model, name='check_model_no_slash'),
    path('get_optimal_features', views.get_optimal_features, name='get_optimal_features_no_slash'),
    path('predict', views.predict, name='predict_no_slash'),
    path('get_variable_info', views.get_variable_info, name='get_variable_info_no_slash'),
    path('get_category_options', views.get_category_options, name='get_category_options_no_slash'),
    path('import_excel', views.import_excel, name='import_excel_no_slash'),
]
