from django import forms
from django.contrib.auth.models import User
from accounts.models import UserProfile

class StaffUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text="Leave blank to keep current password.")
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    staff_role = forms.ChoiceField(choices=UserProfile.STAFF_ROLE_CHOICES, required=False)
    phone = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                profile = self.instance.profile
                self.fields['role'].initial = profile.role
                self.fields['staff_role'].initial = profile.staff_role
                self.fields['phone'].initial = profile.phone
            except UserProfile.DoesNotExist:
                pass

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data.get('role')
            profile.staff_role = self.cleaned_data.get('staff_role')
            profile.phone = self.cleaned_data.get('phone')
            profile.save()
        return user
