from django import forms
from .models import pandit_profile,pandit_service,booking

class PanditProfileForm(forms.ModelForm):
    class Meta:
        model = pandit_profile
        fields = ['mobile', 'email', 'name', 'Exp', 'address',  'availability']
        
    def __init__(self, *args, **kwargs):
        super(PanditProfileForm, self).__init__(*args, **kwargs)
        self.fields['mobile'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mobile'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Name'})
        self.fields['Exp'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Experience'})
        self.fields['address'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Address'})
       
        self.fields['availability'].widget.attrs.update({'class': 'form-select'})


class Pandit_availability_form(forms.ModelForm):
    class Meta:
        model = pandit_profile  # Ensure the model is specified here
        fields = ['availability']  # Only the 'availability' field
        
    
class PanditServiceForm(forms.ModelForm):
    class Meta:
        model = pandit_service
        fields = ['type_of_pooja', 'service', 'rate_type', 'rate']

    def __init__(self, *args, **kwargs):
        super(PanditServiceForm, self).__init__(*args, **kwargs)
        # Adding Bootstrap classes to each field
        self.fields['type_of_pooja'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Select Type of Pooja'})
        self.fields['service'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Select Service'})
        self.fields['rate_type'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Select Rate Type'})
        self.fields['rate'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Rate'})
        
        
class BookingForm(forms.ModelForm):
    class Meta:
        model = booking
        fields = ['conform_date', 'conform_time', 'status']  # Include only the required fields
