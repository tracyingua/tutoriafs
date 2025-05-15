from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from .models import UserProfile, TutorProfile, Subject, SubTopic, GradeLevel, AvailabilityTime,Topic,CredentialDocument,Review,TutorSubjectPricing,StudentProfile ,AssessmentQuestion, AnswerChoice,StudentAssessmentResponse


from .models import   TutorAssessmentQuestion,  TutorAnswerChoice, TutorAssessmentResponse,TutorSchedule
from .models import TutorSchedule, TutorSession


from django.utils.html import format_html
from .models import Conversation, Message



class CustomUserAdmin(UserAdmin):
    model = UserProfile
    list_display = ( 'id' ,'username', 'email', 'first_name', 'middle_name', 'last_name', 'phone_number', 'role', 'is_staff', 'is_active')

    fieldsets = (
    ('User Information', {'fields': ('username', 'email', 'password')}),  
    ('Personal Info', {'fields': ('first_name', 'middle_name', 'last_name', 'phone_number' ,'street','barangay','city', 'gender', 'role', 'profile_photo')}),  
    ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),  
    ('Important dates', {'fields': ('last_login', 'date_joined')}),  
 )

    add_fieldsets = (
        ('User Information', {'fields': ('username', 'email', 'password1', 'password2')}),  
        ('Personal Info', {'fields': ('first_name', 'middle_name', 'last_name', 'street','barangay','city', 'gender', 'role','profile_photo_preview')}),  
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),  
    )

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password'):
            obj.password = make_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

    def profile_photo_preview(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.profile_photo.url)
        return "No Photo"
    profile_photo_preview.short_description = "Profile Photo"


    def has_delete_permission(self, request, obj=None):
        return True  

admin.site.register(UserProfile, CustomUserAdmin)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('id' ,"first_name", "last_name" ,"parent",  "grade_level", "created_at")
    search_fields = ("profile_name", "email", "parent__username")
    list_filter = ("grade_level", "gender", "created_at")
    readonly_fields = ("created_at",) 



@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'tutoring_type', 'profile_photo_preview')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('subjects', 'topics', 'sub_topics', 'grade_levels', 'availability_times')

    def profile_photo_preview(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.profile_photo.url)
        return "No Photo"
    profile_photo_preview.short_description = "Profile Photo"

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name')
    search_fields = ('name', 'subject__name')

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(SubTopic)
class SubTopicAdmin(admin.ModelAdmin):
    list_display = ('topic', 'name')
    search_fields = ('name', 'topic__name')

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(AvailabilityTime)
class AvailabilityTimeAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'hours_available_display')
    list_filter = ('day',)

    def hours_available_display(self, obj):
        return obj.hours_available
    hours_available_display.short_description = 'Hours Available'

    def has_delete_permission(self, request, obj=None):
        return True




@admin.register(CredentialDocument)
class CredentialDocumentAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'document_link', 'uploaded_at')  
    search_fields = ('tutor__user__username', 'document')
    list_filter = ('uploaded_at',)
    ordering = ('-uploaded_at',)

    def document_link(self, obj):
        if obj.document:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.document.url, "View Document")
        return "-"
    document_link.short_description = "Document"
    
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("parent", "tutor", "rating", "created_at")
    search_fields = ("parent__username", "tutor__user__username")
    list_filter = ("rating", "created_at")
    ordering = ("-created_at",)




@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "tutor", "parent", "created_at")
    search_fields = ("tutor__username", "parent__username")
    ordering = ("-created_at",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "text", "timestamp", "is_read")
    search_fields = ("sender__username", "text")
    ordering = ("-timestamp",)



@admin.register(TutorSubjectPricing)
class TutorSubjectPricingAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'subject', 'price_per_hour')
    search_fields = ('tutor__user__username', 'subject__name')
    list_filter = ('subject',)




class AnswerChoiceInline(admin.TabularInline):  
    model = AnswerChoice
    extra = 3  

class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text',) 
    inlines = [AnswerChoiceInline]  

admin.site.register(AssessmentQuestion, AssessmentQuestionAdmin)
admin.site.register(AnswerChoice)


@admin.register(StudentAssessmentResponse)
class StudentAssessmentResponseAdmin(admin.ModelAdmin):
    list_display = ("student", "question", "selected_answer", "submitted_at")
    search_fields = ("student__first_name", "student__last_name", "question__question_text")
    list_filter = ("submitted_at",)




class TutorAnswerChoiceInline(admin.TabularInline):  
    model = TutorAnswerChoice
    extra = 3  

class TutorAssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text',)
    inlines = [TutorAnswerChoiceInline]

@admin.register(TutorAssessmentResponse)
class TutorAssessmentResponseAdmin(admin.ModelAdmin):
    list_display = ("tutor", "question", "selected_answer", "submitted_at")
    search_fields = ("tutor__user__first_name", "tutor__user__last_name", "question__question_text")
    list_filter = ("submitted_at",)

admin.site.register(TutorAssessmentQuestion, TutorAssessmentQuestionAdmin)
admin.site.register(TutorAnswerChoice)




@admin.register(TutorSchedule)
class TutorScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', "tutor", "parent", "student", "schedule_name", "start_date", "end_date", "status")
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("tutor__user__username", "parent__username", "schedule_name")  # FIXED
    ordering = ("start_date",)
    readonly_fields = ("created_at",)

@admin.register(TutorSession)
class TutorSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tutor_schedule', 'date', 'start_time', 'end_time', 'price', 
                   'subject', 'duration_display', 'status', 'substitute_name','substitute_contact' ,'substitute_street' ,'substitute_barangay','cancelled_by', 
                   'created_at')
    list_filter = ('status', 'date', 'subject', 'tutor_schedule__tutor__user__username',
                  'cancelled_by')
    search_fields = ('subject__name', 'tutor_schedule__tutor__user__username',
                   'cancellation_reason')
    list_select_related = ('subject', 'tutor_schedule', 'tutor_schedule__tutor', 
                         'tutor_schedule__tutor__user')
    readonly_fields = ('created_at', 'updated_at')
    

    fieldsets = (
        (None, {
            'fields': ('tutor_schedule', 'date', 'start_time', 'end_time', 
                      'subject', 'duration','substitute_name', 'substitute_contact','substitute_street','substitute_barangay', 'price', 'status')
        }),
        ('Cancellation Details', {
            'fields': ('cancelled_by', 'cancellation_reason'),
            'classes': ('collapse',)  
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def duration_display(self, obj):
        return f"{obj.duration} hours"
    duration_display.short_description = 'Duration'
    duration_display.admin_order_field = 'duration'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
          
            qs = qs.filter(tutor_schedule__tutor__user=request.user)
        return qs


    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if request.user.is_superuser:
            return list_filter + ('cancelled_by',)
        return list_filter


    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.status not in ['canceled', 'canceled_by_parent', 'canceled_by_tutor']:
            return readonly_fields + ('cancelled_by', 'cancellation_reason')
        return readonly_fields