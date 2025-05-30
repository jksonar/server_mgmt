from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from .models import User, Department

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
        
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class CustomerProfileForm(forms.ModelForm):
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'departments']

class AdminUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    role = forms.ChoiceField(
        choices=[
            ('', 'Select Role'),
            ('Admin', 'Admin - Full access to all servers'),
            ('Manager', 'Manager - Edit/view assigned servers'),
            ('Viewer', 'Viewer - View-only access')
        ],
        required=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'departments', 'role']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Add user to the selected role group
            if self.cleaned_data['role']:
                group = Group.objects.get(name=self.cleaned_data['role'])
                user.groups.add(group)
            # Add user to departments
            if self.cleaned_data['departments']:
                user.departments.set(self.cleaned_data['departments'])
        return user

class AdminUserEditForm(forms.ModelForm):
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    role = forms.ChoiceField(
        choices=[
            ('', 'Select Role'),
            ('Admin', 'Admin - Full access to all servers'),
            ('Manager', 'Manager - Edit/view assigned servers'),
            ('Viewer', 'Viewer - View-only access')
        ],
        required=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'departments', 'role']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial role based on user's groups
        if self.instance.pk:
            if self.instance.is_admin():
                self.fields['role'].initial = 'Admin'
            elif self.instance.is_manager():
                self.fields['role'].initial = 'Manager'
            elif self.instance.is_viewer():
                self.fields['role'].initial = 'Viewer'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Update user's role
            if self.cleaned_data['role']:
                # Remove from all role groups first
                user.groups.filter(name__in=['Admin', 'Manager', 'Viewer']).delete()
                # Add to the selected role group
                group = Group.objects.get(name=self.cleaned_data['role'])
                user.groups.add(group)
            # Update departments
            if 'departments' in self.cleaned_data:
                user.departments.set(self.cleaned_data['departments'])
        return user

