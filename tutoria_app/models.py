from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
import os
from django.core.files.storage import default_storage
from django.contrib.auth.hashers import make_password, check_password
from django.utils.timezone import now, timedelta
import random
import uuid
from django.db.models import Avg
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import date
from django.utils import timezone  


def profile_photo_path(instance, filename):
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'  
    filename = f"{uuid.uuid4()}.{ext.lower()}" 
    return os.path.join("profile_photos", filename)

def credential_document_path(instance, filename):
    ext = filename.split('.')[-1] if '.' in filename else 'pdf' 
    filename = f"{uuid.uuid4()}.{ext.lower()}"  
    return os.path.join("credentials", filename)

def student_profile_photo_path(instance, filename):
    ext = filename.split('.')[-1] if '.' in filename else 'jpg' 
    filename = f"{uuid.uuid4()}.{ext.lower()}"  
    return os.path.join("profile_photos", "students", filename) 








class UserProfile(AbstractUser):
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    barangay = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, default='Zamboanga City')
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        default='male',
        blank=True,
        null=True
    )
    role = models.CharField(
        max_length=10,
        choices=[('parent', 'Parent/Guardian'), ('tutor', 'Tutor')],
        default='parent',
        blank=True,
        null=True
    )


    profile_photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)

    groups = models.ManyToManyField(Group, related_name="user_profiles", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="user_profiles", blank=True)

    reset_code_hash = models.CharField(max_length=255, blank=True, null=True)
    reset_code_expiry = models.DateTimeField(blank=True, null=True)

    def delete_old_profile_photo(self):
        """Delete the old profile photo from storage."""
        if self.pk:  
            try:
                old_instance = UserProfile.objects.get(pk=self.pk)
                if old_instance.profile_photo and old_instance.profile_photo != self.profile_photo:
                    if default_storage.exists(old_instance.profile_photo.name):
                        default_storage.delete(old_instance.profile_photo.name)
            except UserProfile.DoesNotExist:
                pass  

    def save(self, *args, **kwargs):
     
     """Allow safe modification of user data, even if modified outside Django."""
     

     """Delete old profile photo before saving a new one and ensure TutorProfile is created."""
     self.delete_old_profile_photo() 

     super().save(*args, **kwargs)  

     if self.role == 'tutor':
        TutorProfile.objects.get_or_create(user=self)

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True
    )


    def generate_reset_code(self):
        """Generate a 6-digit reset code, hash it, and set expiry time."""
        reset_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
        self.reset_code_hash = make_password(reset_code) 
        self.reset_code_expiry = now() + timedelta(minutes=5)  
        self.save()
        return reset_code  

    def is_reset_code_valid(self, code):
        """Check if the entered reset code is correct and not expired."""
        return (
            self.reset_code_hash
            and check_password(code, self.reset_code_hash) 
            and self.reset_code_expiry
            and self.reset_code_expiry > now()
        )

    def clear_reset_code(self):
        """Clear reset code after successful verification."""
        self.reset_code_hash = None
        self.reset_code_expiry = None
        self.save()

    def __str__(self):
        return self.username 


class StudentProfile(models.Model):
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="students"
    )
    profile_photo = models.ImageField(upload_to='student_profile_photos/', blank=True, null=True)  
    first_name = models.CharField(max_length=150, blank=True, null=True)  
    middle_name = models.CharField(max_length=150, blank=True, null=True)  
    last_name = models.CharField(max_length=150, blank=True, null=True)  
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        default='male'
    )
    birthday = models.DateField()
    grade_level = models.CharField(max_length=50)
    street = models.CharField(max_length=255, blank=True, null=True)
    barangay = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, default='Zamboanga City')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Child of {self.parent.username})"
    
    def get_age(self):
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))




class TutorProfile(models.Model):
    TUTORING_TYPE_CHOICES = [
        ('online', 'Online Tutoring'),
        ('in-person', 'In-Person Tutoring'),
        ('both', 'Both Online & In-Person'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutor_profile'
    )
    tutoring_type = models.CharField(
        max_length=20, choices=TUTORING_TYPE_CHOICES, default='online'
    )
    subjects = models.ManyToManyField('Subject', blank=True)
    topics = models.ManyToManyField('Topic', blank=True)
    sub_topics = models.ManyToManyField('SubTopic', blank=True)
    grade_levels = models.ManyToManyField('GradeLevel', blank=True)
    profile_photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)
    availability_times = models.ManyToManyField('AvailabilityTime', blank=True)

    is_over_18 = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  
    is_declined = models.BooleanField(default=False)  
    is_restricted = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.user.username} - Tutor Profile"

    def approve(self):
        """Approves the tutor"""
        self.is_approved = True
        self.is_declined = False
        self.is_restricted = False
        self.save()

    def decline(self):
        """Declines the tutor"""
        self.is_approved = False
        self.is_declined = True
        self.is_restricted = False
        self.save()

    def restrict(self):
        """Restricts the tutor"""
        self.is_restricted = True
        self.is_approved = False
        self.is_declined = False
        self.save()

    def unrestrict(self):
        """Removes restriction from the tutor"""
        self.is_restricted = False
        self.save()

    def delete_old_profile_photo(self):
        """Deletes the old profile photo when a new one is uploaded."""
        if self.pk:
            try:
                old_instance = TutorProfile.objects.get(pk=self.pk)
                if old_instance.profile_photo and old_instance.profile_photo != self.profile_photo:
                    if default_storage.exists(old_instance.profile_photo.name):
                        default_storage.delete(old_instance.profile_photo.name)
            except TutorProfile.DoesNotExist:
                pass  

    def is_profile_complete(self):
        """Checks if the tutor profile has all the necessary data filled."""
        return (
            self.profile_photo and 
            self.subjects.exists() and  
            self.topics.exists() and  
            self.sub_topics.exists() and 
            self.grade_levels.exists() and  
            self.availability_times.exists()  
        )




    def save(self, *args, **kwargs):
        """Delete old profile photo before saving a new one."""
        self.delete_old_profile_photo()
        super().save(*args, **kwargs)

    def average_rating(self):
        """Returns the average rating for the tutor"""
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

class Review(models.Model):
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="given_reviews",
        limit_choices_to={"role": "parent"}  
    )
    tutor = models.ForeignKey(
        TutorProfile,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.IntegerField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],  
        help_text="Rate from 1 (Terrible) to 5 (Amazing)"
    )  
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  
        verbose_name_plural = "Reviews"  

    def __str__(self):
        return f"Review by {self.parent.username} for {self.tutor.user.username} ({self.rating}/5)"


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    subject = models.ForeignKey(
        'Subject', 
        on_delete=models.CASCADE, 
        related_name="topics",
        null=True,  
        blank=True
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)  

    def __str__(self):
        return f"{self.subject.name} - {self.name}" if self.subject else self.name


class SubTopic(models.Model):
    topic = models.ForeignKey(
        'Topic', 
        on_delete=models.CASCADE, 
        related_name="subtopics",
        null=True,  
        blank=True
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True) 

    def __str__(self):
        return f"{self.topic.name} - {self.name}" if self.topic else self.name



class GradeLevel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class AvailabilityTime(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK, null=True, blank=True) 
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.day}: {self.start_time} - {self.end_time}" if self.day else f"Unknown Day: {self.start_time} - {self.end_time}"


class CredentialDocument(models.Model):
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="credentials")
    document = models.FileField(upload_to=credential_document_path , blank=True , null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.tutor.user.username} Credential"
    


class Conversation(models.Model):

    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tutor_conversations")
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="parent_conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {self.tutor.username} and {self.parent.username}"

class Message(models.Model):
    MESSAGE_TYPES = (
        ("text", "Text"),
        ("image", "Image"),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default="text")
    text = models.TextField(blank=True, null=True) 
    image = models.ImageField(upload_to="chat_images/", blank=True, null=True)  
    timestamp = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)
    

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp} ({self.message_type})"
    


class TutorSubjectPricing(models.Model):
    tutor = models.ForeignKey(
        TutorProfile, 
        on_delete=models.CASCADE, 
        related_name="subject_pricing"
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name="tutor_pricing"
    )
    price_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
     
       )


    class Meta:
        unique_together = ('tutor', 'subject')  

    def __str__(self):
        return f"{self.tutor.user.username} - {self.subject.name}: ${self.price_per_hour}/hr"
    
    def save(self, *args, **kwargs):
        """Ensure price is not null before saving"""
        if self.price_per_hour is None: 
            self.price_per_hour = 0.00
        super().save(*args, **kwargs)



class AssessmentQuestion(models.Model):
    question_text = models.TextField()

    def __str__(self):
        return self.question_text

class AnswerChoice(models.Model):
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return self.text
    

class StudentAssessmentResponse(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="assessment_responses")
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(AnswerChoice, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.first_name}'s response to {self.question.question_text}"

    
class TutorAssessmentQuestion(models.Model):
    question_text = models.TextField()
    linked_student_question = models.OneToOneField(
        AssessmentQuestion, on_delete=models.CASCADE, null=True, blank=True, related_name="linked_tutor_question"
    )

    def __str__(self):
        return self.question_text
    



class TutorAnswerChoice(models.Model):
    question = models.ForeignKey(TutorAssessmentQuestion, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255, null=True, blank=True)
    linked_student_answer = models.OneToOneField(
        AnswerChoice, on_delete=models.SET_NULL, null=True, blank=True, related_name="linked_tutor_answer"
    )

    def __str__(self):
        return self.text if self.text else "No Answer Text"



class TutorAssessmentResponse(models.Model):
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="assessment_responses")
    question = models.ForeignKey(TutorAssessmentQuestion, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(TutorAnswerChoice, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tutor.user.username}'s response to {self.question.question_text}"




class TutorSchedule(models.Model):
    tutor = models.ForeignKey(
        "TutorProfile", 
        on_delete=models.CASCADE,
        related_name="tutor_schedules"
    )
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="parent_schedules"
    )
    student = models.ForeignKey(
        "StudentProfile", 
        on_delete=models.CASCADE, 
        related_name="scheduled_sessions",
        null=True, blank=True
    )
    schedule_name = models.CharField(max_length=100, default="Tutoring Schedule")
    start_date = models.DateField()
    end_date = models.DateField()
    repeat_days = models.JSONField(default=dict) 
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    completed_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
  
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Total price for all sessions in this schedule"
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Amount that has been paid (auto-calculated from completed sessions)"
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Remaining balance to be paid (total_price - paid_amount)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("declined", "Declined"),
        ("withdrawn", "Withdrawn"),
    ]

    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tutor.user.username} - {self.schedule_name} ({self.start_date} to {self.end_date}) - {self.total_hours}hrs"

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date must be after start date")

 
        if self.pk is None:  


            
            existing_schedules = TutorSchedule.objects.filter(
                tutor=self.tutor,
                parent=self.parent,
                student=self.student,
                status__in=["pending", "confirmed"],
                sessions__subject__in=self.sessions.values_list('subject', flat=True)
            ).distinct()

            if existing_schedules.exists():
                raise ValidationError(
                    "This student already has an active schedule with this tutor for one or more of the selected subjects"
                )

        self.total_hours = self.calculate_total_hours()
        self.completed_hours = self.calculate_completed_hours()
        self.total_price = self.calculate_total_price()
        self.paid_amount = self.calculate_paid_amount()
        self.balance = self.calculate_balance()

    def calculate_total_hours(self):
        """Calculate total hours from all sessions"""
        if hasattr(self, 'sessions'):
            return sum(
                float(session.duration)
                for session in self.sessions.all()
            )
        return 0.00

    def calculate_completed_hours(self):
        """Calculate hours only from completed sessions"""
        if hasattr(self, 'sessions'):
            return sum(
                float(session.duration)
                for session in self.sessions.all()
                if session.status == 'completed'
            )
        return 0.00

    def calculate_total_price(self):
        """Calculate total price from all sessions"""
        if hasattr(self, 'sessions'):
            return sum(
                float(session.price)
                for session in self.sessions.all()
            )
        return 0.00

    def calculate_paid_amount(self):
        """Calculate paid amount from completed sessions"""
        if hasattr(self, 'sessions'):
            return sum(
                float(session.price)
                for session in self.sessions.all()
                if session.status == 'completed'
            )
        return 0.00

    def calculate_balance(self):
        """Calculate remaining balance"""
        return float(self.total_price) - float(self.paid_amount)

    def update_hours(self):
        """Update both total_hours and completed_hours"""
        self.total_hours = self.calculate_total_hours()
        self.completed_hours = self.calculate_completed_hours()
        self.save()

    def update_financials(self):
        """Update all financial fields"""
        self.total_price = self.calculate_total_price()
        self.paid_amount = self.calculate_paid_amount()
        self.balance = self.calculate_balance()
        self.save()

    def create_sessions(self):
        from .models import TutorSession, AvailabilityTime

        session_objects = []
        errors = []

        for day_name, day_data in self.repeat_days.items():
            try:
                availability = AvailabilityTime.objects.get(tutor=self.tutor, day=day_name)
                day_sessions = self._generate_day_sessions(day_name, availability, day_data)
                session_objects.extend(day_sessions)
            except AvailabilityTime.DoesNotExist:
                errors.append(f"No availability set for {day_name}")
            except Exception as e:
                errors.append(str(e))

        if errors:
            raise ValidationError("\n".join(errors))

 
        created_sessions = TutorSession.objects.bulk_create(session_objects)
        
    
        for session in created_sessions:
            session.save()
        
        self.update_hours()
        self.update_financials()
        return created_sessions

    def _generate_day_sessions(self, day_name, availability, day_data):
        sessions = []
        current_date = self.start_date
        selected_hours = float(day_data.get('selectedHours', 1))

        while current_date <= self.end_date:
            if current_date.strftime('%A') == day_name:
                for slot in day_data.get('timeSlots', []):
                    try:
                        subject_id = slot['subject']
                        sessions.append(TutorSession(
                            tutor_schedule=self,
                            date=current_date,
                            subject_id=subject_id,
                            duration=selected_hours,
                            status='pending'
                        ))
                    except KeyError:
                        continue
            current_date += timedelta(days=1)

        return sessions

    def get_session_dates(self):
        session_dates = []
        current_date = self.start_date

        while current_date <= self.end_date:
            day_name = current_date.strftime("%A")
            if day_name in self.repeat_days:
                day_data = self.repeat_days[day_name]
                for slot in day_data.get('timeSlots', []):
                    session_dates.append({
                        "date": current_date,
                        "subject_id": slot.get("subject"),
                        "duration": float(day_data.get("selectedHours", 1)),
                        "day": day_name
                    })
            current_date += timedelta(days=1)

        return session_dates


class TutorSession(models.Model):
    tutor_schedule = models.ForeignKey(
        "TutorSchedule",
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    date = models.DateField()
    start_time = models.TimeField(
        null=True, 
        blank=True, 
        help_text="Time of the session (optional)"
    )
    
    cancelled_by = models.CharField(
        max_length=10,
        choices=[('tutor', 'Tutor'), ('parent', 'Parent')],
        null=True,
        blank=True
    )
    cancellation_reason = models.TextField(null=True, blank=True)
    end_time = models.TimeField(
        null=True,
        blank=True,
        help_text="End time of the session (auto-calculated if not set)",
        default=None
    )

    substitute_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Name of substitute tutor"
    )
    substitute_contact = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Contact number of substitute tutor"
    )
    substitute_street = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Street address of substitute tutor"
    )
    substitute_barangay = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Barangay of substitute tutor"
    )
    is_substitute = models.BooleanField(
        default=False,
        help_text="Whether this session was taught by a substitute tutor"
    )
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.CASCADE,
        related_name="tutor_sessions"
    )
    duration = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        help_text="Duration in hours (1-3 hours)"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Calculated price for this session based on duration and subject rate"
    )

    SESSION_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("declined", "Declined"),
        ("canceled", "Canceled"),
        ("canceled_by_parent", "Canceled by Parent"),  
        ("canceled_by_tutor", "Canceled by Tutor"), 
        ("withdrawn", "Withdrawn"),
        ("missed", "Missed"), 
    ]


    CANCELLATION_REASON_CHOICES = [
        ("schedule_conflict", "Schedule conflict"),
        ("student_request", "Student request"),
        ("emergency", "Emergency"),
        ("other", "Other"),
    ]
    status = models.CharField(
        max_length=20,
        choices=SESSION_STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']
        unique_together = ('tutor_schedule', 'date', 'subject')

    def clean(self):
        if not (1 <= float(self.duration) <= 3):
            raise ValidationError("Duration must be between 1 and 3 hours")

    def calculate_price(self):
        """Calculate the price for this session based on duration and subject rate"""
        try:
            pricing = TutorSubjectPricing.objects.get(
                tutor=self.tutor_schedule.tutor,
                subject=self.subject
            )
            return float(self.duration) * float(pricing.price_per_hour)
        except TutorSubjectPricing.DoesNotExist:
            return 0.00

    def save(self, *args, **kwargs):
        """Calculate and set the price before saving"""
        if not self.price:  
            self.price = self.calculate_price()
            
  
        self.check_missed_session()
            
        super().save(*args, **kwargs)

    def check_missed_session(self):
        """
        Automatically update status to 'missed' if:
        - The session date is in the past
        - Current status is 'pending'
        - Not already marked as missed
        """
        if (self.date < timezone.now().date() and 
            self.status == 'pending' and 
            self.status != 'missed'):
            self.status = 'missed'
          
    def __str__(self):
        return (
            f"{self.tutor_schedule.tutor.user.username} - "
            f"{self.subject.name} - "
            f"{self.date} ({self.duration}hrs) at {self.start_time if self.start_time else 'TBA'}"
        )

    @classmethod
    def update_past_due_sessions(cls):
        """
        Class method to update all sessions that are past due and still pending
        This can be called from a management command or cron job
        """
        past_due_sessions = cls.objects.filter(
            date__lt=timezone.now().date(),
            status='pending'
        )
        
        updated_count = past_due_sessions.update(status='missed')
        return updated_count


@receiver(post_save, sender=TutorSession)
@receiver(post_delete, sender=TutorSession)
def update_schedule_hours_and_financials(sender, instance, **kwargs):
    """
    Update the parent schedule's hours and financials when a session is saved or deleted
    """
    if instance.tutor_schedule:
        instance.tutor_schedule.update_hours()
        instance.tutor_schedule.update_financials()