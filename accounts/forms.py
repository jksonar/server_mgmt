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
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'departments', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Add user to the selected role group
            if self.cleaned_data['role']:
                group, created = Group.objects.get_or_create(name=self.cleaned_data['role'])
                user.groups.add(group)
            # Add user to departments
            if self.cleaned_data['departments']:
                user.departments.set(self.cleaned_data['departments'])
        return user

class AdminUserEditForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    role = forms.ChoiceField(
        choices=[
            ('', 'Select Role'),
            ('Admin', 'Admin - Full access to all servers'),
            ('Manager', 'Manager - Edit/view assigned servers'),
            ('Viewer', 'Viewer - View-only access')
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'departments', 'role']
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Set initial role based on user's groups
        if self.instance.pk:
            if self.instance.is_admin():
                self.fields['role'].initial = 'Admin'
            elif self.instance.is_manager():
                self.fields['role'].initial = 'Manager'
            elif self.instance.is_viewer():
                self.fields['role'].initial = 'Viewer'
        
        # Debug information
        print(f"Form initialized with fields: {self.fields.keys()}")
        print(f"Form instance: {self.instance}")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            # Store the current user before saving
            from django.contrib.auth import get_user_model
            current_user_id = None
            try:
                from django.contrib import auth
                if hasattr(self, 'request') and self.request:
                    current_user_id = auth.get_user(self.request).id
                    print(f"Current user ID: {current_user_id}")
            except Exception as e:
                print(f"Error getting current user: {e}")
                
            user.save()
            # Update user's role
            if self.cleaned_data['role']:
                print(f"Updating role to: {self.cleaned_data['role']}")
                # Remove from all role groups first
                role_groups = user.groups.filter(name__in=['Admin', 'Manager', 'Viewer'])
                # Directly iterate through the queryset to remove groups
                for group in role_groups:
                    user.groups.remove(group)
                # Add to the selected role group
                try:
                    group = Group.objects.get(name=self.cleaned_data['role'])
                    user.groups.add(group)
                except Group.DoesNotExist:
                    # Create the group if it doesn't exist
                    group = Group.objects.create(name=self.cleaned_data['role'])
                    user.groups.add(group)
            # Update departments
            if 'departments' in self.cleaned_data:
                user.departments.set(self.cleaned_data['departments'])
        return user

