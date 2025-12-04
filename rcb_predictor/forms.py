"""
BCRIS - Forms
Hekim kayıt ve veri yükleme formları
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Physician, PatientDataUpload


class PhysicianSignUpForm(UserCreationForm):
    """Hekim kayıt formu"""
    full_name = forms.CharField(
        max_length=200,
        required=True,
        label="Ad Soyad",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dr. Ahmet Yılmaz'})
    )
    email = forms.EmailField(
        required=True,
        label="E-posta",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ahmet.yilmaz@hastane.com'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Telefon",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+90 555 123 4567'})
    )
    institution = forms.CharField(
        max_length=200,
        required=True,
        label="Kurum/Hastane",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ankara Üniversitesi Tıp Fakültesi'})
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        label="Bölüm",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tıbbi Onkoloji'})
    )
    title = forms.CharField(
        max_length=100,
        required=False,
        label="Ünvan",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prof. Dr. / Doç. Dr. / Uzm. Dr.'})
    )
    id_card_image = forms.ImageField(
        required=True,
        label="Kimlik Kartı (TC Kapalı)",
        help_text="Sağlık Bakanlığı onaylı kimlik kartınızın ön yüzünü yükleyin. TC kimlik numaranızı kapatmayı unutmayın (KVKK).",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kullanıcı adı'}),
        }
        labels = {
            'username': 'Kullanıcı Adı',
            'password1': 'Şifre',
            'password2': 'Şifre (Tekrar)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Şifre'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Şifre (Tekrar)'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Physician profili oluştur
            Physician.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data.get('phone', ''),
                institution=self.cleaned_data['institution'],
                department=self.cleaned_data.get('department', ''),
                title=self.cleaned_data.get('title', ''),
                id_card_image=self.cleaned_data['id_card_image'],
                approval_status='pending'
            )
        
        return user


class PatientDataUploadForm(forms.ModelForm):
    """Hasta verisi yükleme formu"""
    
    class Meta:
        model = PatientDataUpload
        fields = ('excel_file', 'description')
        widgets = {
            'excel_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.xlsx,.xls,.csv'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Veri seti hakkında notlar (opsiyonel)...'
            }),
        }
        labels = {
            'excel_file': 'Excel Dosyası',
            'description': 'Açıklama',
        }
        help_texts = {
            'excel_file': 'Hasta verilerini içeren Excel dosyasını yükleyin (.xlsx, .xls, .csv)',
        }
    
    def save(self, commit=True, physician=None):
        instance = super().save(commit=False)
        
        if physician:
            instance.physician = physician
        
        # Dosya bilgilerini kaydet
        if instance.excel_file:
            instance.original_filename = instance.excel_file.name
            instance.file_size = instance.excel_file.size
        
        if commit:
            instance.save()
        
        return instance
