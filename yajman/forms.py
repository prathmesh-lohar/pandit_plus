from django import forms
from pandit.models import booking, pandit_service, services_type  # Make sure to import services_type
from yajman.models import yajman_profile


class BookingForm(forms.ModelForm):
    name_of_pooja = forms.ModelChoiceField(
        queryset=pandit_service.objects.none(),  # Initialize with an empty queryset
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Pooja"
    )

    class Meta:
        model = booking
        exclude = ['yajman_id', 'pandit_id', 'status', 'payment_status', 'conform_date', 'conform_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'location': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        services_provide = kwargs.pop('services_provide', None)
        super().__init__(*args, **kwargs)
        if services_provide:
            self.fields['name_of_pooja'].queryset = services_provide
            
class YajmanProfileForm(forms.ModelForm):
    class Meta:
        model = yajman_profile
        fields = ['mobile', 'email', 'name', 'address', 'profile_picture', 'latitude', 'longitude']
        
    def __init__(self, *args, **kwargs):
        super(YajmanProfileForm, self).__init__(*args, **kwargs)
        self.fields['mobile'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mobile'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Name'})
        self.fields['address'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Address'})
        self.fields['latitude'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Latitude'})
        self.fields['longitude'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Longitude'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})
