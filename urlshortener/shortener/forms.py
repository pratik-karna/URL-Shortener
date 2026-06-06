from django import forms
from .models import ShortURL, generate_short_code
from django.utils import timezone


class ShortURLForm(forms.ModelForm):
    custom_short_code = forms.CharField(
        max_length=20, required=False,
        help_text='Leave blank for auto-generated code',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. my-link (optional)'})
    )
    expiry_hours = forms.IntegerField(
        required=False, min_value=1,
        help_text='Hours until this link expires (optional)',
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 24'})
    )

    class Meta:
        model = ShortURL
        fields = ['original_url', 'title']
        widgets = {
            'original_url': forms.URLInput(attrs={'placeholder': 'https://example.com/very-long-url'}),
            'title': forms.TextInput(attrs={'placeholder': 'Optional title for this link'}),
        }

    def clean_custom_short_code(self):
        code = self.cleaned_data.get('custom_short_code', '').strip()
        if code:
            if ShortURL.objects.filter(short_code=code).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError('This short code is already taken. Please choose another.')
            if not all(c.isalnum() or c in '-_' for c in code):
                raise forms.ValidationError('Only letters, numbers, hyphens and underscores allowed.')
        return code

    def save(self, commit=True):
        instance = super().save(commit=False)
        custom_code = self.cleaned_data.get('custom_short_code', '').strip()
        expiry_hours = self.cleaned_data.get('expiry_hours')

        if custom_code:
            instance.short_code = custom_code
            instance.custom_code = True
        elif not instance.pk:
            code = generate_short_code()
            while ShortURL.objects.filter(short_code=code).exists():
                code = generate_short_code()
            instance.short_code = code

        if expiry_hours:
            instance.expires_at = timezone.now() + timezone.timedelta(hours=expiry_hours)

        if commit:
            instance.save()
        return instance


class ShortURLEditForm(forms.ModelForm):
    expiry_hours = forms.IntegerField(
        required=False, min_value=1,
        help_text='Set new expiry from now (hours)',
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 24'})
    )
    clear_expiry = forms.BooleanField(required=False, label='Remove expiration')

    class Meta:
        model = ShortURL
        fields = ['original_url', 'title', 'is_active']

    def save(self, commit=True):
        instance = super().save(commit=False)
        expiry_hours = self.cleaned_data.get('expiry_hours')
        clear_expiry = self.cleaned_data.get('clear_expiry')

        if clear_expiry:
            instance.expires_at = None
        elif expiry_hours:
            instance.expires_at = timezone.now() + timezone.timedelta(hours=expiry_hours)

        if commit:
            instance.save()
        return instance
