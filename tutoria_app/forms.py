from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

from .models import Subject, SubTopic, GradeLevel,StudentProfile,AssessmentQuestion, AnswerChoice ,TutorAssessmentQuestion, TutorAnswerChoice


class SignupForm(UserCreationForm):
    middle_name = forms.CharField(required=False)
    street = forms.CharField(max_length=255, required=True)
    barangay = forms.CharField(max_length=255, required=True)
    city = forms.CharField(max_length=100, initial="Zamboanga City", required=True)
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], required=True)
    role = forms.ChoiceField(choices=[('parent', 'Parent/Guardian'), ('tutor', 'Tutor')], required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'middle_name', 'last_name', 'username', 'email',
            'phone_number', 'street', 'barangay', 'city',
            'gender', 'role', 'password1', 'password2'
        ]

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'middle_name', 'last_name', 'username', 'email',
            'phone_number', 'street', 'barangay', 'city',
            'gender', 'role', 'password1', 'password2'
        ]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if UserProfile.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and UserProfile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("An account with this phone number already exists.")
        return phone_number
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']

class SubTopicForm(forms.ModelForm):
    class Meta:
        model = SubTopic
        fields = ['name']

class GradeLevelForm(forms.ModelForm):
    class Meta:
        model = GradeLevel
        fields = ['name']




class EditParentProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    middle_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False 
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'middle_name', 'last_name', 'email',
            'street', 'barangay', 'profile_photo'
        ]
        widgets = {
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street'
            }),
            'barangay': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Barangay'
            }),
            'profile_photo': forms.ClearableFileInput(attrs={
                'onchange': "previewImage(event)"
            }),
        }

class StudentRegistrationForm(forms.ModelForm):
    GRADE_CHOICES = [
        ('', 'Select Grade'),  
        ('Grade 1', 'Grade 1'),
        ('Grade 2', 'Grade 2'),
        ('Grade 3', 'Grade 3'),
        ('Grade 4', 'Grade 4'),
        ('Grade 5', 'Grade 5'),
        ('Grade 6', 'Grade 6'),
    ]

    GENDER_CHOICES = [
        ('', 'Select Gender'),  
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    grade_level = forms.ChoiceField(
        choices=GRADE_CHOICES,
        widget=forms.Select(attrs={'id': 'id_grade_level', 'class': 'grade', 'required': 'required'})
    )

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'gender', 'id': 'id_gender', 'required': 'required'})
    )

    middle_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'id': 'id_middle_name'})
    )

    class Meta:
        model = StudentProfile
        fields = ['first_name', 'last_name', 'middle_name', 'gender', 'birthday', 'grade_level', 'street', 'barangay', 'profile_photo']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date', 'id': 'id_birthday', 'required': 'required'}),
            'first_name': forms.TextInput(attrs={'id': 'id_first_name', 'required': 'required'}),  
            'last_name': forms.TextInput(attrs={'id': 'id_last_name', 'required': 'required'}),
            'middle_name': forms.TextInput(attrs={'id': 'id_middle_name'}),  # Middle name field added here
            'street': forms.TextInput(attrs={'id': 'id_street', 'required': 'required'}),
            'barangay': forms.TextInput(attrs={'id': 'id_barangay', 'required': 'required'}),
            'profile_photo': forms.FileInput(attrs={'id': 'id_profile_photo', 'accept': 'image/*', 'onchange': 'previewImage(event)', 'required': 'required'}),
        }



class AssessmentQuestionForm(forms.ModelForm):
    class Meta:
        model = AssessmentQuestion
        fields = ['question_text']  

class AnswerChoiceForm(forms.ModelForm):
    class Meta:
        model = AnswerChoice
        fields = ['text']  



class TutorAssessmentQuestionForm(forms.ModelForm):
    class Meta:
        model = TutorAssessmentQuestion
        fields = ["question_text"]

class TutorAnswerChoiceForm(forms.ModelForm):
    text = forms.CharField(required=True, label="Answer Choice")  # Make text required

    class Meta:
        model = TutorAnswerChoice
        fields = ["text"]


class StudentEditProfileForm(forms.ModelForm):
    GRADE_CHOICES = [
        ('', 'Select Grade'),  
        ('Grade 1', 'Grade 1'),
        ('Grade 2', 'Grade 2'),
        ('Grade 3', 'Grade 3'),
        ('Grade 4', 'Grade 4'),
        ('Grade 5', 'Grade 5'),
        ('Grade 6', 'Grade 6'),
    ]

    GENDER_CHOICES = [
        ('', 'Select Gender'),  
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    grade_level = forms.ChoiceField(
        choices=GRADE_CHOICES,
        widget=forms.Select(attrs={'id': 'id_grade_level', 'class': 'grade'})
    )

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'gender', 'id': 'id_gender'})
    )

    middle_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'id': 'id_middle_name'})
    )

    class Meta:
        model = StudentProfile
        fields = ['first_name', 'last_name', 'middle_name', 'gender', 'birthday', 'grade_level', 'street', 'barangay', 'profile_photo']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date', 'id': 'id_birthday'}),
            'first_name': forms.TextInput(attrs={'id': 'id_first_name'}),  
            'last_name': forms.TextInput(attrs={'id': 'id_last_name'}),
            'middle_name': forms.TextInput(attrs={'id': 'id_middle_name'}), 
            'street': forms.TextInput(attrs={'id': 'id_street'}),
            'barangay': forms.TextInput(attrs={'id': 'id_barangay'}),
            'profile_photo': forms.ClearableFileInput(attrs={'id': 'id_profile_photo', 'accept': 'image/*', 'onchange': 'previewImage(event)'}),
        }
