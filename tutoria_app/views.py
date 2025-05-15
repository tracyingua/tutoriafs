
from django.shortcuts import render, redirect, get_object_or_404
import threading
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .forms import SignupForm,EditParentProfileForm ,StudentRegistrationForm, StudentEditProfileForm
from django.contrib.auth.decorators import login_required, user_passes_test
from tutoria_app.models import UserProfile,Review, TutorSchedule, TutorSession
from .models import TutorProfile, Subject, Topic, SubTopic, GradeLevel,CredentialDocument,Avg,TutorSubjectPricing, AssessmentQuestion, AnswerChoice ,  StudentProfile, StudentAssessmentResponse, TutorAssessmentQuestion, TutorAnswerChoice, TutorAssessmentResponse
from tutoria_app.utils import get_matching_tutors 
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import os
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from .decorators import admin_required
from .decorators import user_login_required
import re
from django.db.models import Q
from .models import Conversation, Message
from django.http import JsonResponse
import json
from .forms import TutorAssessmentQuestionForm, TutorAnswerChoiceForm
from .models import TutorSchedule, Subject
from itertools import groupby
from django.views.decorators.http import require_POST
from django.utils import timezone
from operator import attrgetter
import time
from .models import Subject, Topic, SubTopic
import random
from django.db.models import Case, When, Value, IntegerField
import string
import time
import random
import string
from .serializers import TutorScheduleSerializer
from django.core.paginator import Paginator

from django.db.models import Sum

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from .models import StudentProfile, TutorSession

from datetime import time as time_parser

from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField









def student_matches(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    matching_tutors = get_matching_tutors(student)  

    context = {
        "student": student,
        "matching_tutors": matching_tutors,
    }
    return render(request, "users/student_matches.html", context)











def index (request):

    return render (request, "users/index.html")



def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                
                if user.role == "tutor":
                    return redirect('user_about')
                    
                return render(request, 'users/signup.html', {
                    'form': SignupForm(),
                    'success': True,
                    'modal_title': "Signup Successful!",
                    'modal_message': "Welcome to Tutoria! Your account has been created successfully."
                })
            except Exception as e:
                return render(request, 'users/signup.html', {
                    'form': form,
                    'error': True,
                    'error_title': "Signup Failed!",
                    'error_message': f"An error occurred: {str(e)}"
                })
        else:
            error_message = "Please fix the following errors:"
            for field, errors in form.errors.items():
                error_message += f"\n{field.capitalize()}: {errors[0]}"
            
            return render(request, 'users/signup.html', {
                'form': form,
                'error': True,
                'error_title': "Signup Failed!",
                'error_message': error_message
            })
    else:
        form = SignupForm()
    return render(request, 'users/signup.html', {'form': form})

def signin(request):
    if request.method == "POST":
        username_or_email = request.POST.get('email')
        password = request.POST.get('password')
        user = None

    
        if '@' in username_or_email:
            try:
                user = UserProfile.objects.get(email=username_or_email)
                username_or_email = user.username  
            except UserProfile.DoesNotExist:
                user = None

        user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            if user.is_superuser:
                return render(request, 'users/login.html', {
                    'error': True,
                    'error_message': "Superusers are not allowed to log in here."
                })

       
            login(request, user)
            request.session['user_id'] = user.id  
            request.session['user_role'] = user.role 

    
            if user.role == "tutor":
                try:
                    tutor_profile = TutorProfile.objects.get(user=user)

                  
                    if (
                        not tutor_profile.subjects.exists() or
                        not tutor_profile.topics.exists() or
                        not tutor_profile.grade_levels.exists() or
                        not tutor_profile.profile_photo
                    ):
                        messages.warning(request, "Please complete your tutor profile before proceeding.")
                        return redirect('user_about')  

                    if tutor_profile.is_restricted:
                        return render(request, 'users/login.html', {
                            'error': True,
                            'error_message': "Your account has been restricted. Please contact support."
                        })
                    
                    request.session['profile_photo'] = tutor_profile.profile_photo.url if tutor_profile.profile_photo else None
                except TutorProfile.DoesNotExist:
                    
                    messages.warning(request, "Please complete your tutor profile before proceeding.")
                    return redirect('user_about')

            elif user.role == "parent":
                request.session['profile_photo'] = user.profile_photo.url if user.profile_photo else None

            return redirect('tutoria') 

        else:
            return render(request, 'users/login.html', {
                'error': True,
                'error_message': "Invalid email/username or password. Please try again."
            })

    return render(request, 'users/login.html')


def logout_function(request):
    logout(request)
    return redirect('signin')  


def forgot(request):
    """Step 1: Request email and send reset code."""
    if request.method == "POST":
        email = request.POST.get("email")
        
        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect("forgot")

      
        reset_code = user.generate_reset_code()
        
  
        send_mail(
            "Your Password Reset Code",
            f"Your password reset code is: {reset_code}\nThis code expires in 5 minutes.",
            "noreply@tutoria.com",
            [email],
            fail_silently=False,
        )

        messages.success(request, "A reset code has been sent to your email.")
     
        return redirect("code", user_id=user.id)

    return render(request, "users/forgot.html")


def code(request, user_id):
  
    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        messages.error(request, "Invalid request.")
        return redirect("forgot_password")

    if request.method == "POST":
        code = request.POST.get("code")

   
        for _ in messages.get_messages(request):
            pass  

        if user.is_reset_code_valid(code):
            user.clear_reset_code()
            messages.success(request, "Your password has been reset. You can now log in.")
            return redirect("reset_password", user_id=user.id)

        messages.error(request, "Invalid or expired code.")
        return redirect("code", user_id=user.id)

    return render(request, "users/code.html", {"user_id": user_id})

def reset_password(request, user_id):
    """Step 3: Reset the password after code verification."""
    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        messages.error(request, "Invalid request.")
        return redirect("forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")


        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect("reset_password", user_id=user.id)

   
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password", user_id=user.id)

     
        user.set_password(new_password)
        user.save()

    
        return redirect("congrats_reset")

    return render(request, "users/reset_password.html", {"user_id": user_id})



#renders the upload tutors
def find_tutor(request):
    """Finds tutors based on the selected student's assessment responses and selected topic."""

    parent = request.user  
    students = StudentProfile.objects.filter(parent=parent)  
    all_subjects = Subject.objects.all()  

    selected_student = None
    matched_tutors = []

    topic_id = request.GET.get("topic")

    if request.method == "POST":
        student_id = request.POST.get("student_id")
        if student_id:
            request.session["selected_student_id"] = student_id  
            return redirect("find_tutor")  

    student_id = request.session.get("selected_student_id")
    if student_id:
        selected_student = get_object_or_404(StudentProfile, id=student_id, parent=parent)
        all_tutors = get_matching_tutors(selected_student)  

        current_user_tutor_profile = getattr(parent, "tutor_profile", None)

        matched_tutors = [
            {
                "tutor": tutor["tutor"],
                "match_score": tutor["match_score"],
                "grade_levels": list(tutor["tutor"].grade_levels.values_list("name", flat=True)),
                "subjects": list(tutor["tutor"].subjects.values_list("name", flat=True)),
                "topics": list(tutor["tutor"].topics.values_list("name", flat=True)), 
                "tutoring_type": tutor["tutor"].tutoring_type, 
            }
            for tutor in all_tutors
            if (selected_student.grade_level in tutor["tutor"].grade_levels.values_list("name", flat=True)
                and (not current_user_tutor_profile or tutor["tutor"] != current_user_tutor_profile)
                and tutor["tutor"].is_approved  # Only approved tutors
                and not tutor["tutor"].is_declined  
                and not tutor["tutor"].is_restricted 
            )
        ]

        if topic_id:
            matched_tutors = [
                tutor for tutor in matched_tutors 
                if int(topic_id) in tutor["tutor"].topics.values_list("id", flat=True)
            ]

    return render(request, "users/find_tutor.html", {
        "students": students,
        "selected_student": selected_student,
        "tutors": matched_tutors,
        "all_subjects": all_subjects,
    })



def user_profile(request):
    profile_photo = None

    if request.user.is_authenticated:
        try:
            tutor_profile = TutorProfile.objects.get(user=request.user) 
            profile_photo = tutor_profile.profile_photo.url if tutor_profile.profile_photo else None
        except TutorProfile.DoesNotExist:
            profile_photo = None

    return {'profile_photo': profile_photo}




@user_login_required                                                       
def tutoria(request):
   
    return render(request, 'users/tutoria.html' )


@user_login_required
def user_chat(request, conversation_id=None):
    user = request.user
    conversations = Conversation.objects.filter(Q(tutor=user) | Q(parent=user))

    selected_conversation = None
    messages_with_avatars = []
    chat_partner = None
    chat_partner_tutor_profile = None
    chat_partner_profile_photo = None
    conversation_images = []
    filtered_users = []
    unread_message_user_ids = set()

    # ✅ Combine logic for both roles
    tutor_profiles_as_parent = TutorSchedule.objects.filter(
        parent=user,
        student__in=user.students.all()
    ).values_list('tutor', flat=True).distinct()

    parent_ids_as_tutor = TutorSchedule.objects.filter(
        tutor=user.tutor_profile
    ).values_list('parent', flat=True).distinct()

    filtered_users = UserProfile.objects.filter(
        Q(tutor_profile__id__in=tutor_profiles_as_parent) |
        Q(id__in=parent_ids_as_tutor)
    ).exclude(id=user.id).distinct()

    # ✅ Check for unread messages
    for u in filtered_users:
        has_unread = Message.objects.filter(
            conversation__in=conversations,
            sender=u,
            is_read=False
        ).exists()
        if has_unread:
            unread_message_user_ids.add(u.id)

    # ✅ Handle selected conversation
    if conversation_id:
        selected_conversation = get_object_or_404(Conversation, id=conversation_id)

        if user not in [selected_conversation.tutor, selected_conversation.parent]:
            raise Http404("You don't have permission to view this conversation")

        chat_partner = (
            selected_conversation.parent
            if selected_conversation.tutor == user
            else selected_conversation.tutor
        )

        if chat_partner.profile_photo:
            chat_partner_profile_photo = chat_partner.profile_photo.url

        messages = Message.objects.filter(
            conversation=selected_conversation
        ).order_by("timestamp")

        for message in messages:
            avatar_url = None
            if message.sender.profile_photo:
                avatar_url = message.sender.profile_photo.url
            elif hasattr(message.sender, 'tutor_profile') and message.sender.tutor_profile.profile_photo:
                avatar_url = message.sender.tutor_profile.profile_photo.url

            messages_with_avatars.append({
                'message': message,
                'avatar_url': avatar_url,
                'sender_name': message.sender.get_full_name(),
                'timestamp': timezone.localtime(message.timestamp).strftime("%b %d, %Y %I:%M %p")
            })

        conversation_images = messages.filter(image__isnull=False).values_list("image", flat=True)

        if hasattr(chat_partner, 'tutor_profile'):
            chat_partner_tutor_profile = chat_partner.tutor_profile

    return render(request, 'users/chat.html', {
        'users': filtered_users,
        'conversations': conversations,
        'selected_conversation': selected_conversation,
        'messages_with_avatars': messages_with_avatars,
        'chat_partner': chat_partner,
        'chat_partner_tutor_profile': chat_partner_tutor_profile,
        'chat_partner_profile_photo': chat_partner_profile_photo,
        'current_user_id': user.id,
        'conversation_images': conversation_images,
        'current_user_role': request.user.role,  
        'unread_message_user_ids': unread_message_user_ids,
    })

@user_login_required
def start_conversation(request, user_id):
    user = request.user
    other_user = get_object_or_404(UserProfile, id=user_id)

 
    conversation = Conversation.objects.filter(
        (Q(tutor=user) & Q(parent=other_user)) | (Q(tutor=other_user) & Q(parent=user))
    ).first()

    if not conversation:
        conversation = Conversation.objects.create(tutor=user, parent=other_user)

    return redirect('chat_detail', conversation_id=conversation.id)


# Function to generate a unique filename for the image
def generate_unique_filename(image_name, user_id):
    # Generate a unique timestamp and a random string to avoid filename conflicts
    timestamp = int(time.time())  # Use a timestamp for uniqueness
    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))  # Random string
    return f"chat_images/{user_id}_{timestamp}_{random_suffix}_{image_name}"


@csrf_exempt
def send_message(request):
    if request.method == "POST":
        user = request.user
        conversation_id = request.POST.get("conversation_id")
        message_text = request.POST.get("message", "").strip()
        image = request.FILES.get("image")  # Get the image from the request

        print(f" Received conversation_id: {conversation_id}, User: {user}")

        # Validate the conversation ID
        if not conversation_id or not conversation_id.isdigit():
            print(" Invalid conversation ID")
            return JsonResponse({"error": "Invalid conversation ID"}, status=400)

        # Fetch the conversation from the database
        conversation = Conversation.objects.filter(id=int(conversation_id)).first()

        if not conversation:
            print(" Conversation not found!")
            return JsonResponse({"error": "Invalid conversation"}, status=400)

        # Check if the user is part of the conversation
        if user not in [conversation.tutor, conversation.parent]:
            print(f"🚫 User {user} is not part of this conversation but sending anyway (for testing)")

        # Create a new message instance
        message = Message(conversation=conversation, sender=user)
        
        # Assign the text message if provided
        if message_text:
            message.text = message_text

        # Assign the image if provided, with a unique filename
        if image:
            image_name = generate_unique_filename(image.name, user.id)  # Generate unique image filename
            image_path = default_storage.save(image_name, image)
            message.image = image_path

        # Save the message to the database
        message.save()

        # Prepare the response data
        response_data = {
            "message": message.text if message.text else "",
            "image_url": message.image.url if message.image else "",
            "type": "image" if message.image else "text",
            "sender": message.sender.username,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"), 
        }

        print(f" Message sent: {response_data}")
        return JsonResponse(response_data)


    print(" Invalid request method")
    return JsonResponse({"error": "Invalid request"}, status=400)

 
@user_login_required
def get_new_messages(request):
    conversation_id = request.GET.get("conversation_id")
    last_message_id = request.GET.get("last_message_id", "0")

    if not conversation_id:
        return JsonResponse({"error": "Missing conversation_id"}, status=400)

    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        if request.user not in [conversation.tutor, conversation.parent]:
            return JsonResponse({"error": "Unauthorized access"}, status=403)

        last_message_id = int(last_message_id)
        new_messages = Message.objects.filter(
            conversation=conversation,
            id__gt=last_message_id
        ).order_by("id")

        messages_list = []
        for message in new_messages:
            sender = message.sender
            
            sender_avatar = ""
            if message.sender.profile_photo:
                sender_avatar = message.sender.profile_photo.url
            elif hasattr(message.sender, "tutor_profile") and message.sender.tutor_profile.profile_photo:
                sender_avatar = message.sender.tutor_profile.profile_photo.url

            messages_list.append({
                "id": message.id,
                "content": message.text if message.text else "",
                "image_url": message.image.url if message.image else "",
                "type": "image" if message.image else "text",
                "sender_id": sender.id,
                "sender_username": sender.username,
                "sender_avatar": sender_avatar,
                "timestamp": timezone.localtime(message.timestamp).strftime("%b %d, %Y %I:%M %p")
            })

        return JsonResponse({"messages": messages_list})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
def subjects(request):
    all_subjects = Subject.objects.all()

  
    cleaned_subjects = []
    for subject in all_subjects:
     
        cleaned_name = re.sub(r"\(.*?\)", "", subject.name).strip()
        cleaned_subjects.append({
            "original_id": subject.id,      
            "original_name": subject.name,  
            "cleaned_name": cleaned_name     
        })

    return render(request, "users/subjects.html", {
        "subjects": cleaned_subjects
    })

def subjects_2(request, subject_name):
    subject = get_object_or_404(Subject, name=subject_name)  
    topics = Topic.objects.filter(subject=subject) 

    context = {
        'subject': subject,
        'topics': topics,
    }
    return render(request, 'users/subjects_2.html', context)












@user_login_required
def user_about(request):
    tutor_profile, created = TutorProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        tutoring_type = request.POST.get("tutoring_type")
        subject_ids = request.POST.getlist("subjects[]")
        topic_ids = request.POST.getlist("topics[]")
        sub_topic_ids = request.POST.getlist("sub_topic[]")
        grade_ids = request.POST.getlist("grade[]")
        availability_data = [
            {
                'day': day,
                'start_time': start,
                'end_time': end
            }
            for day, start, end in zip(
                request.POST.getlist('days[]'),
                request.POST.getlist('start_times[]'),
                request.POST.getlist('end_times[]')
            )
        ]

        request.session['tutor_profile_data'] = {
            'tutoring_type': tutoring_type,
            'subjects': subject_ids,
            'topics': topic_ids,
            'sub_topics': sub_topic_ids,
            'grade_levels': grade_ids,
            'availability': availability_data
        }

        messages.success(request, "Phase 1 saved! Proceed to subject pricing.")
        return redirect('subject_price')  

    context = {
        'tutor_profile': tutor_profile,
        'subjects': Subject.objects.all(),
        'topics': Topic.objects.all(),
        'sub_topics': SubTopic.objects.all(),
        'grade_levels': GradeLevel.objects.all(),
    }
    return render(request, 'users/user_about.html', context)


@user_login_required
def subject_price(request):
    """Phase 2: Tutor selects subject pricing before assessment."""
    phase1_data = request.session.get('tutor_profile_data')
    if not phase1_data:
        messages.error(request, "Phase 1 data is missing. Please complete it first.")
        return redirect('user_about')

    selected_subjects = Subject.objects.filter(id__in=phase1_data.get('subjects', []))

    if request.method == "POST":
        subject_prices = request.POST.getlist('subject_price[]')
        subject_ids = [str(subject.id) for subject in selected_subjects]

        if not subject_prices or len(subject_prices) != len(subject_ids):
            messages.error(request, "Please enter pricing for all selected subjects.")
            return redirect('subject_price')

        tutor_pricing = {subject_id: price for subject_id, price in zip(subject_ids, subject_prices)}
        request.session['tutor_pricing_data'] = tutor_pricing  

        messages.success(request, "Phase 2 saved! Proceed to assessment.")
        return redirect('tutor_assessment')  

    context = {
        'subjects': selected_subjects
    }
    return render(request, 'users/subject_price.html', context)



@user_login_required
def tutor_assessment(request):
    """Phase 3: Tutor must complete assessment before final phase."""
    phase1_data = request.session.get('tutor_profile_data')
    pricing_data = request.session.get('tutor_pricing_data')

    if not phase1_data or not pricing_data:
        messages.error(request, "You must complete previous steps first.")
        return redirect('user_about')

    if not hasattr(request.user, 'tutor_profile'):  
        messages.error(request, "You must complete previous steps first.")
        return redirect('user_about')

    tutor = request.user.tutor_profile  
    questions = TutorAssessmentQuestion.objects.prefetch_related('choices').all()

    if request.method == "POST":
        responses = []
       
        TutorAssessmentResponse.objects.filter(tutor=tutor).delete()
        
        for question in questions:
            answer_ids = request.POST.get(f"question_{question.id}", "").split(",")
            
            for answer_id in answer_ids:
                if answer_id:  
                    try:
                        selected_answer = TutorAnswerChoice.objects.get(id=answer_id)
                        responses.append(
                            TutorAssessmentResponse(
                                tutor=tutor,
                                question=question,
                                selected_answer=selected_answer
                            )
                        )
                    except (TutorAnswerChoice.DoesNotExist, ValueError):
                        messages.error(request, "Invalid answer selection.")
                        return redirect("tutor_assessment")

        if responses:
            TutorAssessmentResponse.objects.bulk_create(responses)
            request.session['tutor_assessment_completed'] = True
            messages.success(request, "Phase 3 saved! Proceed to profile completion.")
            return redirect("user_about_2")

    context = {"questions": questions}
    return render(request, "users/tutor_assessment.html", context)





@user_login_required
def user_about_2(request):
    """Final Phase: Tutor uploads files & completes profile."""
    user = request.user  


    phase1_data = request.session.get('tutor_profile_data')
    pricing_data = request.session.get('tutor_pricing_data')
    assessment_completed = request.session.get('tutor_assessment_completed')

    if not phase1_data or not pricing_data or not assessment_completed:
        messages.error(request, "You must complete all previous steps before proceeding.")
        return redirect('user_about')

    try:
        tutor_profile = user.tutor_profile  
    except TutorProfile.DoesNotExist:
        messages.error(request, "Tutor profile not found. Please start over.")
        return redirect('user_about')

    if request.method == "POST":
        profile_photo = request.FILES.get('profile_photo')
        uploaded_files = request.FILES.getlist('credential_documents')

        if not profile_photo and not uploaded_files:
            messages.error(request, "You must upload at least a profile photo or a credential document.")
            return redirect('user_about_2')

 
        if profile_photo:
            ext = profile_photo.name.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{ext.lower()}"
            file_path = os.path.join("profile_photos", unique_filename)
            saved_path = default_storage.save(file_path, ContentFile(profile_photo.read()))
            tutor_profile.profile_photo = saved_path  

     
        if uploaded_files:
            for file in uploaded_files:
                if file.size > 5 * 1024 * 1024:
                    messages.error(request, f"{file.name} is too large. Max size is 5MB.")
                    continue  

                ext = file.name.split('.')[-1]
                unique_filename = f"{uuid.uuid4()}.{ext.lower()}"
                doc_path = os.path.join("credentials", unique_filename)
                saved_doc_path = default_storage.save(doc_path, ContentFile(file.read()))

                CredentialDocument.objects.create(tutor=tutor_profile, document=saved_doc_path)

  
        tutor_profile.is_over_18 = request.POST.get('is_over_18') == 'on'
        tutor_profile.tutoring_type = phase1_data.get('tutoring_type', tutor_profile.tutoring_type)
        tutor_profile.subjects.set(Subject.objects.filter(id__in=phase1_data.get('subjects', [])))
        tutor_profile.topics.set(Topic.objects.filter(id__in=phase1_data.get('topics', [])))
        tutor_profile.sub_topics.set(SubTopic.objects.filter(id__in=phase1_data.get('sub_topics', [])))
        tutor_profile.grade_levels.set(GradeLevel.objects.filter(id__in=phase1_data.get('grade_levels', [])))


        for availability in phase1_data.get('availability', []):
            tutor_profile.availability_times.create(
                day=availability['day'],
                start_time=availability['start_time'],
                end_time=availability['end_time']
            )

     
        for subject_id, price in pricing_data.items():
            subject = Subject.objects.get(id=subject_id)
            TutorSubjectPricing.objects.create(tutor=tutor_profile, subject=subject, price_per_hour=price)

        tutor_profile.save()

    
        request.session.pop('tutor_profile_data', None)
        request.session.pop('tutor_pricing_data', None)
        request.session.pop('tutor_assessment_completed', None)

        messages.success(request, "Profile completed successfully!")
        return redirect('congrats')  

    selected_subjects = tutor_profile.subjects.all()
    context = {
        "user_first_name": user.first_name,
        "user_last_name": user.last_name,
        "subjects": selected_subjects, 
        "tutor_profile": tutor_profile,
    }

    return render(request, 'users/user_about_2.html', context)



def congrats(request):
  
    return render(request, 'users/congrats.html')


def congrats_reset(request):
  
    return render(request, 'users/congrats-reset.html')
from django.shortcuts import get_object_or_404, render
from django.db.models import Case, When, Value, IntegerField
from django.contrib.auth.decorators import login_required as user_login_required
from django.utils import timezone
from datetime import datetime, timedelta
from .models import TutorProfile, SubTopic, StudentProfile, TutorSchedule, TutorSubjectPricing


@user_login_required
def teacher_profile(request, id):
    tutor = get_object_or_404(TutorProfile, id=id)
    subjects = tutor.subjects.all()
    topics = tutor.topics.all()

    # Get student ID from session (check both possible session keys)
    student_id = request.session.get('selected_student_id') or request.session.get('student_id')
    
    student_info = None
    if student_id:
        try:
            student = StudentProfile.objects.get(id=student_id, parent=request.user)
            student_info = {
                "id": student.id,
                "first_name": student.first_name,
                "middle_name": student.middle_name,
                "last_name": student.last_name,
                "grade_level": student.grade_level,
            }
        except StudentProfile.DoesNotExist:
            messages.warning(request, "Selected student not found or you don't have permission")

    has_existing_schedule = False
    if student_id:
        has_existing_schedule = TutorSchedule.objects.filter(
            tutor=tutor,
            student_id=student_id,
            status__in=["pending", "confirmed"]
        ).exists()

    subject_pricing = TutorSubjectPricing.objects.filter(tutor=tutor)

    subjects_progress = []
    for pricing in subject_pricing:
        subject = pricing.subject
        total_topics = subject.topics.count()
        total_subtopics = SubTopic.objects.filter(topic__subject=subject).count()

        tutor_topics = tutor.topics.filter(subject=subject).count()
        tutor_subtopics = tutor.sub_topics.filter(topic__subject=subject).count()

        total_count = total_topics + total_subtopics
        tutor_count = tutor_topics + tutor_subtopics

        progress_percentage = (tutor_count / total_count * 100) if total_count else 0

        subjects_progress.append({
            "subject": subject,
            "subject_name": subject.name,
            "grade_level": ", ".join(tutor.grade_levels.values_list("name", flat=True)),
            "price": pricing.price_per_hour,
            "has_existing_schedule": has_existing_schedule,
            "progress": round(progress_percentage, 2),
        })

    # Weekday sorting logic
    DAY_ORDER = {
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6,
        'Sunday': 7
    }

    availability_times = tutor.availability_times.annotate(
        day_order=Case(
            *[When(day=day, then=Value(order)) for day, order in DAY_ORDER.items()],
            output_field=IntegerField()
        )
    ).order_by('day_order', 'start_time')

    available_days = tutor.availability_times.values_list("day", flat=True).distinct()
    available_days_list = sorted(available_days, key=lambda x: DAY_ORDER.get(x, 8)) if available_days else []

    tutor_grade_levels = tutor.grade_levels.values_list("name", flat=True)
    phone_number = getattr(tutor.user, "phone_number", "Not Available")

    return render(request, 'users/teacher_profile.html', {
        "tutor": tutor,
        "phone_number": phone_number,
        "subjects_progress": subjects_progress,
        "tutor_grade_levels": tutor_grade_levels,
        "subjects": subjects,
        "topics": topics,
        "available_days": available_days_list,
        "availability_times": availability_times,
        "student": student_info,
        "selected_student_id": student_id,
        "has_existing_schedule": has_existing_schedule,
    })





@user_login_required
def teacher_profile_2(request, id):
    tutor = get_object_or_404(TutorProfile, id=id)
    
    # Get student ID from session (check both possible session keys)
    student_id = request.session.get('selected_student_id') or request.session.get('student_id')
    
    student_info = None
    if student_id:
        try:
            student = StudentProfile.objects.get(id=student_id, parent=request.user)
            student_info = {
                "id": student.id,
                "first_name": student.first_name,
                "middle_name": student.middle_name,
                "last_name": student.last_name,
                "grade_level": student.grade_level,
            }
        except StudentProfile.DoesNotExist:
            messages.warning(request, "Selected student not found or you don't have permission")

    credentials = tutor.credentials.all()
    feedbacks = tutor.reviews.all().order_by('-created_at')

    # Weekday sorting logic
    DAY_ORDER = {
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6,
        'Sunday': 7
    }

    availability_times = tutor.availability_times.annotate(
        day_order=Case(
            *[When(day=day, then=Value(order)) for day, order in DAY_ORDER.items()],
            output_field=IntegerField()
        )
    ).order_by('day_order', 'start_time')

    available_days = tutor.availability_times.values_list("day", flat=True).distinct()
    available_days_list = sorted(available_days, key=lambda x: DAY_ORDER.get(x, 8)) if available_days else []

    topics = tutor.topics.all()
    subjects = tutor.subjects.all()

    subjects_data = [
        {'id': subject.id, 'name': subject.name}
        for subject in subjects
    ]

    return render(request, 'users/teacher_profile_2.html', {
        'tutor': tutor,
        'credentials': credentials,
        'feedbacks': feedbacks,
        'available_days': available_days_list,
        'availability_times': availability_times,
        'subjects': subjects_data,
        'topics': topics,
        'student': student_info,
        'selected_student_id': student_id,
    })

@user_login_required
def get_tutor_availability(request, tutor_id):
    try:
        tutor = get_object_or_404(TutorProfile, id=tutor_id)
        availability = {}

        for time_slot in tutor.availability_times.all():
          
            if not time_slot.day or not time_slot.start_time or not time_slot.end_time:
                continue
                
            day = time_slot.day
            if day not in availability:
                availability[day] = {
                    "time_slots": [],
                    "total_hours": 0
                }
            
    
            today = timezone.now().date()
            start_dt = timezone.make_aware(datetime.combine(today, time_slot.start_time))
            end_dt = timezone.make_aware(datetime.combine(today, time_slot.end_time))
            
     
            if end_dt <= start_dt:
                end_dt += timedelta(days=1)
                
            duration = (end_dt - start_dt).total_seconds() / 3600

            availability[day]["time_slots"].append({
                "start": time_slot.start_time.strftime("%H:%M"),
                "end": time_slot.end_time.strftime("%H:%M"),
                "duration": round(duration, 2)
            })
            availability[day]["total_hours"] += duration

        return JsonResponse({"availability": availability})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
    

@user_login_required
def submit_feedback(request, tutor_id):
    tutor = get_object_or_404(TutorProfile, id=tutor_id)

    if request.method == "POST":
        print("Received POST data:", request.POST)

        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "").strip()

        if not rating:
            messages.add_message(request, messages.ERROR, "Please select a rating.", extra_tags="sch-error")
            return redirect(request.META.get("HTTP_REFERER", "home"))

        if not comment:
            messages.add_message(request, messages.ERROR, "Please provide a comment.", extra_tags="sch-error")
            return redirect(request.META.get("HTTP_REFERER", "home"))

        if request.user.role != "parent":
            messages.add_message(request, messages.ERROR, "Only parents can submit feedback.", extra_tags="sch-error")
            return redirect(request.META.get("HTTP_REFERER", "home"))

      
        Review.objects.filter(parent=request.user, tutor=tutor).delete()

    
        Review.objects.create(
            parent=request.user,
            tutor=tutor,
            rating=int(rating),
            comment=comment
        )

        messages.add_message(request, messages.SUCCESS, "Your feedback has been updated successfully!", extra_tags="sch-success")
        return redirect(request.META.get("HTTP_REFERER", "home"))

    return redirect("home")




def select_student(request, student_id):
    """ Store selected student ID in session and redirect to Find a Tutor """
    request.session['selected_student_id'] = student_id
    return redirect('find_tutor') 


@user_login_required
def parent_profile(request):
    if not request.user.is_authenticated:
        return redirect('signin')  

    if request.session.get('user_role') != 'parent':
        return redirect('tutoria')  

    user = request.user  
    students = StudentProfile.objects.filter(parent=user)  

    return render(request, 'users/parent_profile.html', {
        'user': user,  
        'students': students,  
    })


@user_login_required
def edit_parent_profile(request):
    user = request.user  

    if request.method == "POST":
        form = EditParentProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
         
            if 'profile_photo' in request.FILES:
               
                if user.profile_photo:
                    try:
                        os.remove(user.profile_photo.path)
                    except (ValueError, OSError):
                        pass
            
         
            form.save()
            
           
            request.session['profile_photo'] = user.profile_photo.url if user.profile_photo else None
            
            messages.success(request, "Your profile has been successfully updated!", extra_tags='edit_parent_profile_success')
            return redirect('edit_parent_profile')
    else:
        form = EditParentProfileForm(instance=user)

    return render(request, 'users/edit_parent_profile.html', {
        'form': form,
        'user': user
    })

@login_required

#REGISTER A STUDENT
def register_student(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.parent = request.user
            student.save()
            messages.success(request, "Student registered successfully!", extra_tags='student_registration_success')
            return redirect('student_assessment', student_id=student.id)
    else:
      
        parent = request.user
        initial_data = {
            'street': parent.street,
            'barangay': parent.barangay,
        }
        form = StudentRegistrationForm(initial=initial_data)

    return render(request, 'users/register_student.html', {
        'form': form,
        'success_message': 'student_registration_success'
    })




@user_login_required
def edit_student(request, student_id):
    """Allows a parent to edit a student's profile"""
    student = get_object_or_404(StudentProfile, id=student_id, parent=request.user)

    if request.method == "POST":
        form = StudentEditProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student profile updated successfully!", extra_tags='edit_profile_success')
            return redirect("edit_student", student_id=student.id)  

    else:
        form = StudentEditProfileForm(instance=student)

    return render(request, "users/edit_student.html", {"form": form, "student": student})


@user_login_required
def student_assessment(request, student_id):
    parent = request.user  

    try:
        student = StudentProfile.objects.get(id=student_id, parent=parent)
    except StudentProfile.DoesNotExist:
        return redirect("register_student") 

    questions = AssessmentQuestion.objects.prefetch_related("choices").all()

    if request.method == "POST":
        selected_answers = request.POST.getlist("answers")  

        for answer_id in selected_answers:
            answer = AnswerChoice.objects.get(id=answer_id)
            StudentAssessmentResponse.objects.create(
                student=student,
                question=answer.question,
                selected_answer=answer
            )

        messages.success(request, "Student assessment completed successfully! You can now register another student.")
        return redirect("register_student") 

    return render(request, "users/student_assessment.html", {
        "questions": questions,
        "student": student
    })


@require_POST
@login_required
def cancel_session(request):
    booking_id = request.POST.get('booking_id')
    reason_type = request.POST.get('reason_type', '')
    custom_reason = request.POST.get('reason', '')
    
    try:
        session = TutorSession.objects.select_related(
            'tutor_schedule__tutor__user',
            'tutor_schedule__parent'
        ).get(id=booking_id)
        
        # Determine who is canceling
        if request.user == session.tutor_schedule.tutor.user:
            canceler = 'tutor'
            new_status = 'canceled_by_tutor'
        elif request.user == session.tutor_schedule.parent:
            canceler = 'parent'
            new_status = 'canceled_by_parent'
        else:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied'
            }, status=403)
        
        if session.status not in ['pending', 'confirmed']:
            return JsonResponse({
                'success': False,
                'error': 'Only pending or confirmed sessions can be cancelled'
            }, status=400)

        # Build cancellation reason text
        if reason_type == 'other' and custom_reason:
            cancellation_reason = f"Other: {custom_reason}"
        elif reason_type:
            # Get human-readable version of the reason
            reason_display = dict(TutorSession.CANCELLATION_REASON_CHOICES).get(reason_type, reason_type)
            cancellation_reason = reason_display
        else:
            cancellation_reason = "No reason provided"

        # Update session
        session.status = new_status
        session.cancelled_by = canceler
        session.cancellation_reason = cancellation_reason
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Session cancelled by {canceler}',
            'new_status': new_status,
            'canceled_by': canceler
        })
        
    except TutorSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session not found'
        }, status=404)
    

@require_POST
@login_required
def withdraw_schedule(request):
    try:
        schedule_id = request.POST.get('schedule_id')
        
        if not schedule_id:
            return JsonResponse({
                'success': False,
                'error': 'Schedule ID is required'
            }, status=400)
            
        schedule = TutorSchedule.objects.get(
            id=schedule_id,
            parent=request.user
        )
        
        if schedule.status == 'withdrawn':
            return JsonResponse({
                'success': False,
                'error': 'This schedule has already been withdrawn'
            })
            
   
        schedule.sessions.exclude(status='completed').update(status='withdrawn')
        
 
        schedule.status = 'withdrawn'
        schedule.save()
        
   
        schedule.update_financials()
        
        return JsonResponse({
            'success': True,
            'message': 'Schedule and non-completed sessions have been withdrawn'
        })
        
    except TutorSchedule.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Schedule not found or you don\'t have permission'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
def student_profile(request, student_id):
    """Retrieve student profile with assigned tutor schedules and sessions."""
    student = get_object_or_404(StudentProfile, id=student_id)

    # Fetch the tutor schedules associated with this student
    tutor_schedules = TutorSchedule.objects.filter(student=student).order_by('tutor', 'start_date')

    grouped_schedules = []
    for schedule in tutor_schedules:
        # Fetch the associated tutor session
        tutor_session = TutorSession.objects.filter(tutor_schedule=schedule).first()

        # Get subject from the related session
        subject = tutor_session.subject if tutor_session else None
        subject_name = subject.name if subject else "No subject"
        subject_id = subject.id if subject else None

        grouped_schedules.append({
            'tutor': schedule.tutor,
            'subject': subject_name,
            'subject_id': subject_id,
            'start_date': schedule.start_date,
            'end_date': schedule.end_date,
            'status': schedule.status,
            'id': schedule.id  
        })

    return render(request, 'users/student_profile.html', {
        "student": student,
        "grouped_schedules": grouped_schedules,
        "tutor_schedules": tutor_schedules     
    })


def student_sessions(request, student_id, subject_id):
    """Retrieve all sessions for a specific student and subject."""
    student = get_object_or_404(StudentProfile, id=student_id)
    subject = get_object_or_404(Subject, id=subject_id)
    
    tutor_sessions = TutorSession.objects.filter(
        tutor_schedule__student=student,
        subject=subject
    ).order_by('date', 'start_time').select_related('tutor_schedule__tutor', 'tutor_schedule__tutor__user')
    
    paginator = Paginator(tutor_sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    total_hours = tutor_sessions.aggregate(total=Sum('duration'))['total'] or 0
    completed_hours = tutor_sessions.filter(status='completed').aggregate(
        completed=Sum('duration')
    )['completed'] or 0
    
    completion_percentage = 0
    if total_hours > 0:
        completion_percentage = min(100, (completed_hours / total_hours) * 100)
    
    tutor_schedule = TutorSchedule.objects.filter(
        student=student,
        sessions__subject=subject
    ).first()
    
    total_amount = tutor_schedule.total_price if tutor_schedule else 0
    paid_amount = tutor_schedule.paid_amount if tutor_schedule else 0
    balance_due = tutor_schedule.balance if tutor_schedule else 0
    
 
    main_tutor = None
    substitute_tutors = set()

    for session in tutor_sessions:
        if session.is_substitute:
            substitute_tutors.add(f"{session.substitute_name} - Substitute")
        elif not main_tutor:
          
            main_tutor_obj = session.tutor_schedule.tutor
            main_tutor = f"{main_tutor_obj.user.get_full_name()} - Main Tutor"


    if not main_tutor and tutor_sessions.exists():
        fallback_tutor = tutor_sessions.first().tutor_schedule.tutor
        main_tutor = f"{fallback_tutor.user.get_full_name()} - Main Tutor"


    tutors_involved = [main_tutor] + sorted(substitute_tutors) if main_tutor else sorted(substitute_tutors)

    return render(request, 'users/student_sessions.html', {
        "student": student,
        "subject": subject,
        "main_tutor": main_tutor,
        "substitute_tutors": substitute_tutors,
        "tutors_involved": tutors_involved,
        "page_obj": page_obj,
        "total_hours": total_hours,
        "completed_hours": completed_hours,
        "completion_percentage": completion_percentage,
        "total_amount": total_amount,
        "paid_amount": paid_amount,
        "balance_due": balance_due,
    })



def tutor_profile(request):
    if request.session.get("user_role") != "tutor":
        return redirect("tutoria")  

    tutor = get_object_or_404(TutorProfile, user=request.user)

    subjects = TutorSubjectPricing.objects.filter(tutor=tutor)  
    print("Subjects for tutor:", subjects)  

    selected_subjects = list(tutor.subjects.values_list("id", flat=True))  
    selected_grade_levels = list(tutor.grade_levels.values_list("id", flat=True))
    selected_topics = list(tutor.topics.values_list("id", flat=True))  
    selected_subtopics = list(tutor.sub_topics.values_list("id", flat=True))  

    topics = Topic.objects.filter(subject_id__in=selected_subjects)
    subtopics = SubTopic.objects.filter(topic_id__in=topics.values_list("id", flat=True))

    grade_levels = tutor.grade_levels.all()
    reviews = Review.objects.filter(tutor=tutor)
    credentials = CredentialDocument.objects.filter(tutor=tutor)

    average_rating = reviews.aggregate(Avg("rating"))["rating__avg"] or 0  

    context = {
        "tutor": tutor,
        "subjects": subjects,
        "all_subjects": Subject.objects.all(),
        "all_topics": topics,
        "all_subtopics": subtopics,
        "selected_subjects": json.dumps(selected_subjects),
        "selected_topics": json.dumps(selected_topics),
        "selected_subtopics": json.dumps(selected_subtopics),
        "reviews": reviews,
        "grade_levels": grade_levels,
        "selected_grade_levels": json.dumps(selected_grade_levels),
        "credentials": credentials,
        "average_rating": round(average_rating, 1),
        
        "is_approved": tutor.is_approved,
        "is_declined": tutor.is_declined,
        "is_restricted": tutor.is_restricted,
    }

    return render(request, "users/tutor_profile.html", context)

def get_topics_for_subjects(request):
    subjects = request.GET.getlist("subjects[]") 

    print(f"Subjects received from AJAX: {subjects}")  
    if not subjects:
        return JsonResponse({"topics": [], "subtopics": [], "grade_levels": []})  

   
    topics = Topic.objects.filter(subject_id__in=subjects).values("id", "name", "subject_id")


    topic_ids = [topic["id"] for topic in topics]
    subtopics = SubTopic.objects.filter(topic_id__in=topic_ids).values("id", "name", "topic_id")

 
    tutor = get_object_or_404(TutorProfile, user=request.user)
    all_grade_levels = GradeLevel.objects.values("id", "name")

    response_data = {
        "topics": list(topics),
        "subtopics": list(subtopics),
        "grade_levels": list(all_grade_levels),  
    }

    print(f"Response Data Sent: {response_data}")  

    return JsonResponse(response_data)


@user_login_required

#TUTOR BOOKINGS
def tutor_bookings(request):
    tutor_user = request.user

    try:
        tutor_profile = TutorProfile.objects.select_related('user').get(user=tutor_user)
        today = timezone.now().date()

        # Get all related sessions from today onwards
        bookings = TutorSession.objects.filter(
            tutor_schedule__tutor=tutor_profile,
            date__gte=today
        ).select_related(
            'tutor_schedule',
            'tutor_schedule__student',
            'tutor_schedule__parent',
            'tutor_schedule__tutor__user',
            'subject'
        ).annotate(
            status_priority=Case(
                When(tutor_schedule__status='confirmed', then=Value(1)),
                When(tutor_schedule__status='pending', then=Value(2)),
                When(tutor_schedule__status='declined', then=Value(3)),
                default=Value(4),
                output_field=IntegerField()
            )
        ).order_by('tutor_schedule__student', 'status_priority', 'date')

   
        schedule_counts = TutorSchedule.objects.filter(tutor=tutor_profile).values('status').annotate(count=Count('id'))
        status_map = {'pending': 0, 'confirmed': 0, 'completed': 0}
        for item in schedule_counts:
            status = item['status']
            if status in status_map:
                status_map[status] = item['count']

        context = {
            'bookings': bookings,
            'current_date': today,
            'pending_count': status_map['pending'],
            'confirmed_count': status_map['confirmed'],
            'completed_count': status_map['completed'],
        }
        return render(request, 'users/tutor_bookings.html', context)

    except TutorProfile.DoesNotExist:
        context = {
            'error_message': "You don't have a tutor profile set up yet.",
            'bookings': None,
            'pending_count': 0,
            'confirmed_count': 0,
            'completed_count': 0,
        }
        return render(request, 'users/tutor_bookings.html', context)

#TUTOR BOOKING DETAILS
def tutor_booking_details(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)

    # Fetch the tutor schedule for the student and the tutor
    tutor_schedule = TutorSchedule.objects.filter(
        student=student,
        tutor__user=request.user
    ).first()

    # Fetch bookings associated with the student and the tutor
    bookings_queryset = TutorSession.objects.filter(
        tutor_schedule__student=student,
        tutor_schedule__tutor__user=request.user
    ).select_related('subject', 'tutor_schedule')

    # Pagination: 10 items per page
    paginator = Paginator(bookings_queryset, 10)
    page_number = request.GET.get('page')
    bookings_page = paginator.get_page(page_number)

    # Add display fields to paginated bookings
    for booking in bookings_page:
        booking.day_of_week = booking.date.strftime('%A')
        booking.display_start_time = booking.start_time.strftime('%I:%M %p') if booking.start_time else "Not Assigned"
        booking.display_end_time = booking.end_time.strftime('%I:%M %p') if booking.end_time else "Not Assigned"

    total_sessions = bookings_queryset.count()
    total_duration = bookings_queryset.aggregate(total=Sum('duration'))['total'] or 0
    completed_hours = bookings_queryset.filter(status='completed').aggregate(
        completed=Sum('duration')
    )['completed'] or 0

    total_amount = tutor_schedule.total_price if tutor_schedule else 0
    paid_amount = tutor_schedule.paid_amount if tutor_schedule else 0
    balance_due = tutor_schedule.balance if tutor_schedule else 0

    # Fetch parent details (assuming a 'ParentProfile' related to 'StudentProfile')
    parent = student.parent if hasattr(student, 'parent') else None
    parent_name = f"{parent.first_name} {parent.last_name}" if parent else None
    parent_contact = parent.phone_number if parent else None

    return render(request, 'users/tutor_bookings_details.html', {
        'student': student,
        'bookings': bookings_page,  # Pass paginated bookings
        'total_sessions': total_sessions,
        'total_duration': total_duration,
        'completed_hours': completed_hours,
        'tutor_schedule': tutor_schedule,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'balance_due': balance_due,
        'parent_name': parent_name,  # Pass parent's name
        'parent_contact': parent_contact,  # Pass parent's contact number
    })



@user_login_required
@require_POST

#ACCEPT BOOKING
def accept_booking(request):
    booking_id = request.POST.get('booking_id')
    booking = get_object_or_404(TutorSession, id=booking_id)
    

    if booking.tutor_schedule.tutor.user != request.user:
        return JsonResponse({"error": "You don't have permission to modify this booking."}, status=403)
    
    if booking.status != 'pending':
        return JsonResponse({"error": "This booking is already processed."}, status=400)

    try:
        start_time_str = request.POST.get('start_time')
        if not start_time_str:
            raise ValidationError("Start time is required.")
        
   
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
        except ValueError:
            raise ValidationError("Invalid time format. Use HH:MM.")
        
  
        duration_hours = float(booking.duration)
        start_datetime = datetime.combine(booking.date, start_time)
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        end_time = end_datetime.time()
        
 
        booking.start_time = start_time
        booking.end_time = end_time
        booking.status = 'confirmed'
        booking.save()
        
        return JsonResponse({
            "success": True, 
            "message": "Booking accepted successfully.",
            "start_time": start_time.strftime('%H:%M'),
            "end_time": end_time.strftime('%H:%M')
        })
    
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=400)

@require_POST

#DECLINE BOOKING
def decline_booking(request):
    booking_id = request.POST.get('booking_id')
    booking = get_object_or_404(TutorSession, id=booking_id)
    
    # Verify the booking belongs to the tutor
    if booking.tutor_schedule.tutor.user != request.user:
        return JsonResponse({"error": "You don't have permission to modify this booking."}, status=403)
    
    if booking.status != 'pending':
        return JsonResponse({"error": "This booking is already processed."}, status=400)

    try:
        booking.status = 'declined'
        booking.save()
        return JsonResponse({"success": True, "message": "Booking declined successfully."})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    

@user_login_required
@require_POST


def complete_booking(request):
    booking_id = request.POST.get('booking_id')
    booking = get_object_or_404(TutorSession, id=booking_id)
    
    if booking.tutor_schedule.tutor.user != request.user:
        return JsonResponse({"error": "You don't have permission to modify this booking."}, status=403)
    
    if booking.status != 'confirmed':
        return JsonResponse({"error": "Only confirmed sessions can be completed."}, status=400)

    booking.status = 'completed'
    booking.save()
    return JsonResponse({"success": True, "message": "Session marked as completed."})

@user_login_required
@require_POST
def cancel_booking(request):
    booking_id = request.POST.get('booking_id')
    reason = request.POST.get('reason')
    other_reason = request.POST.get('other_reason', '')
    booking = get_object_or_404(TutorSession, id=booking_id)
    
    if booking.tutor_schedule.tutor.user != request.user:
        return JsonResponse({"error": "You don't have permission to modify this booking."}, status=403)
    
    if booking.status != 'confirmed':
        return JsonResponse({"error": "Only confirmed sessions can be cancelled."}, status=400)


    booking.status = 'canceled_by_tutor'  
    booking.cancelled_by = 'tutor'
    

    if reason == 'other':
        full_reason = f"Other: {other_reason}"
    else:
        reason_display = dict(TutorSession.CANCELLATION_REASON_CHOICES).get(reason, reason)
        full_reason = reason_display
    
    booking.cancellation_reason = full_reason
    booking.save()
    
    return JsonResponse({
        "success": True, 
        "message": "Session cancelled successfully.",
        "reason": full_reason
    })


@user_login_required
def update_tutor_profile(request):
    if request.method == "POST":
        tutor_profile = get_object_or_404(TutorProfile, user=request.user)

        try:
       
            subjects = request.POST.getlist("subjects[]")
            topics = request.POST.getlist("topics[]")
            subtopics = request.POST.getlist("subtopics[]")
            tutoring_type = request.POST.get("tutoring_type")
            phone_number = request.POST.get("phone_number")
            grade_levels = request.POST.getlist("grade_levels[]")
            removed_credentials = json.loads(request.POST.get("removed_credentials", "[]"))

      
            tutor_profile.tutoring_type = tutoring_type
            tutor_profile.user.phone_number = phone_number
            tutor_profile.user.save()

        
            existing_subjects = set(tutor_profile.subjects.values_list("id", flat=True))

       
            tutor_profile.subjects.set(Subject.objects.filter(id__in=subjects))
            tutor_profile.topics.set(Topic.objects.filter(id__in=topics))
            tutor_profile.sub_topics.set(SubTopic.objects.filter(id__in=subtopics))
            tutor_profile.grade_levels.set(GradeLevel.objects.filter(id__in=grade_levels))

   
            selected_subjects = set(map(int, subjects))
            removed_subjects = existing_subjects - selected_subjects
            new_subjects = selected_subjects - existing_subjects

            if removed_subjects:
                TutorSubjectPricing.objects.filter(tutor=tutor_profile, subject_id__in=removed_subjects).delete()

            default_price = (
                TutorSubjectPricing.objects.filter(tutor=tutor_profile).first().price_per_hour
                if TutorSubjectPricing.objects.filter(tutor=tutor_profile).exists()
                else 500.00
            )

 
            for subject_id in new_subjects:
                subject = Subject.objects.get(id=subject_id)
                TutorSubjectPricing.objects.create(
                    tutor=tutor_profile, subject=subject, price_per_hour=default_price
                )

       
            if removed_credentials:
                CredentialDocument.objects.filter(id__in=removed_credentials).delete()

       
            if "credentials" in request.FILES:
                for uploaded_file in request.FILES.getlist("credentials"):
                    CredentialDocument.objects.create(tutor=tutor_profile, document=uploaded_file)

            tutor_profile.save()

            return JsonResponse({"success": True, "message": "Profile updated successfully!"})

        except Exception as e:
            print(f"Error updating tutor profile: {e}")
            return JsonResponse({"error": "An error occurred while updating the profile."}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)



@user_login_required

def update_tutor_profile_2(request):
    if request.method == "POST":
        user = request.user
        user_profile = get_object_or_404(UserProfile, username=user.username)
        tutor_profile = get_object_or_404(TutorProfile, user=user)

      
        user_profile.first_name = request.POST.get("first_name", user_profile.first_name)
        user_profile.middle_name = request.POST.get("middle_name", user_profile.middle_name)
        user_profile.last_name = request.POST.get("last_name", user_profile.last_name)
        user_profile.gender = request.POST.get("gender", user_profile.gender)
        user_profile.street = request.POST.get("street", user_profile.street)
        user_profile.barangay = request.POST.get("barangay", user_profile.barangay)
        user_profile.email = request.POST.get("email", user_profile.email)
        user_profile.save()

     
        if "profile_picture" in request.FILES:
            tutor_profile.profile_photo = request.FILES["profile_picture"]
            tutor_profile.save()

            
            request.session["profile_photo"] = tutor_profile.profile_photo.url

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)



def update_subject_prices(request):
    if request.method == "POST":
        try:
            for key, value in request.POST.items():
                if key.startswith("price_"):  
                    subject_id = key.split("_")[1]  
                    subject = get_object_or_404(TutorSubjectPricing, id=subject_id)
                    subject.price_per_hour = float(value)  
                    subject.save()

            return JsonResponse({"success": True, "message": "Prices updated successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})



from django.views.decorators.http import require_GET


from datetime import timedelta
from django.core.exceptions import ValidationError

@require_GET
def check_schedule(request):
    student_id = request.GET.get('student_id')
    tutor_id = request.GET.get('tutor_id')
    subject_id = request.GET.get('subject_id')
    
    if not all([student_id, tutor_id, subject_id]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        existing = TutorSchedule.objects.filter(
            student_id=student_id,
            tutor_id=tutor_id,
            status__in=["pending", "confirmed"],
            sessions__subject_id=subject_id
        ).exists()
        
        subject_name = Subject.objects.get(id=subject_id).name if existing else None
        
        return JsonResponse({
            'exists': existing,
            'subject_name': subject_name
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
from django.views.decorators.http import require_GET

@require_POST
@csrf_exempt

#create schedule
def create_schedule(request):
    try:
        data = json.loads(request.body)
        required_fields = ["tutor_id", "parent_id", "start_date", "end_date", "repeat_days"]
        for field in required_fields:
            if field not in data:
                return JsonResponse({"success": False, "error": f"Missing field: {field}"})

        student_id = request.session.get("selected_student_id")
        if not student_id:
            return JsonResponse({"success": False, "error": "Student ID not found"})

        repeat_days = data.get("repeat_days", {})
        schedule_subjects = set()
        
        for day_data in repeat_days.values():
            if isinstance(day_data, dict) and day_data.get("subjects"):
                schedule_subjects.update(day_data["subjects"])
        
        if schedule_subjects:
            existing = TutorSchedule.objects.filter(
                tutor_id=data["tutor_id"],
                student_id=student_id,
                status__in=["pending", "confirmed"]
            )
            
            for schedule in existing:
                existing_subjects = set(schedule.sessions.values_list('subject', flat=True))
                conflicts = schedule_subjects & existing_subjects
                
                if conflicts:
                    names = Subject.objects.filter(
                        id__in=conflicts
                    ).values_list('name', flat=True)
                    return JsonResponse({
                        "success": False,
                        "error": f"Active schedule exists for: {', '.join(names)}"
                    })

        try:
            start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError) as e:
            return JsonResponse({"success": False, "error": f"Invalid date: {str(e)}"})

        schedule = TutorSchedule.objects.create(
            tutor_id=data["tutor_id"],
            parent_id=data["parent_id"],
            student_id=student_id,
            start_date=start_date,
            end_date=end_date,
            repeat_days=data["repeat_days"],
            status="pending"
        )

        if data.get("create_sessions", False):
            created = []
            current_date = start_date
            
            while current_date <= end_date:
                day_name = current_date.strftime('%A')
                day_data = repeat_days.get(day_name)
                
                if day_data and day_data.get("subjects"):
                    duration = day_data.get("selectedHours", 1)
                    
                    for subject_id in day_data["subjects"]:
                        try:
                            session = TutorSession.objects.create(
                                tutor_schedule=schedule,
                                date=current_date,
                                subject_id=subject_id,
                                duration=duration,
                                status="pending"
                            )
                            created.append(session.id)
                        except Subject.DoesNotExist:
                            continue
                
                current_date += timedelta(days=1)
            
            schedule.status = "pending"
            schedule.save()
            
            return JsonResponse({
                "success": True,
                "message": f"Created schedule with {len(created)} sessions",
                "schedule_id": schedule.id
            })
                
        return JsonResponse({
            "success": True,
            "message": "Schedule created",
            "schedule_id": schedule.id
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@require_POST
@csrf_exempt

#generate session after create the schedule
def generate_sessions(request, schedule_id):
    try:
        schedule = TutorSchedule.objects.get(id=schedule_id)
        repeat_days = schedule.repeat_days
        
        TutorSession.objects.filter(tutor_schedule=schedule).delete()
        
        created_sessions = []
        current_date = schedule.start_date
        
        while current_date <= schedule.end_date:
            day_name = current_date.strftime('%A')
            day_data = repeat_days.get(day_name)
            
            if day_data and day_data.get("subjects"):
                duration = day_data.get("selectedHours", 1)
                
                for subject_id in day_data["subjects"]:
                    try:
                        subject = Subject.objects.get(id=subject_id)
                        
                        session = TutorSession.objects.create(
                            tutor_schedule=schedule,
                            date=current_date,
                            subject=subject,
                            duration=duration,
                            status="pending"
                        )
                        created_sessions.append(session.id)
                    except Subject.DoesNotExist:
                        continue
            
            current_date += timedelta(days=1)
        
        schedule.status = "confirmed"
        schedule.save()
        
        return JsonResponse({
            "success": True,
            "message": f"Created {len(created_sessions)} sessions",
            "session_ids": created_sessions
        })
    
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
    
def get_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'notifications': [], 'unread_count': 0})

    notifications = []

    # Tutor notifications
    if request.user.role == 'tutor':
        # Pending booking requests
        pending_schedules = TutorSchedule.objects.filter(
            tutor=request.user.tutor_profile,
            status='pending'
        ).count()

        if pending_schedules > 0:
            notifications.append({
                'message': f'You have {pending_schedules} pending booking request(s)',
                'type': 'schedule_request',
                'status': 'pending',
                'schedule_id': None  # Will be filled if needed
            })

        # Recent session status changes (last 7 days)
        recent_sessions = TutorSession.objects.filter(
            tutor_schedule__tutor=request.user.tutor_profile,
            updated_at__gte=datetime.now() - timedelta(days=7)
        ).exclude(status='pending').order_by('-updated_at')[:5]

        for session in recent_sessions:
            if session.status == 'confirmed':
                notifications.append({
                    'message': f'Session confirmed for {session.tutor_schedule.student.first_name}',
                    'type': 'session_update',
                    'status': session.status,
                    'session_id': session.id,
                    'date': session.date.strftime('%b %d, %Y'),
                    'from_who': session.tutor_schedule.student.first_name,
                    'subject': session.subject.name
                })
            elif session.status in ['canceled', 'canceled_by_parent', 'canceled_by_tutor']:
                notifications.append({
                    'message': f'Session canceled for {session.tutor_schedule.student.first_name}',
                    'type': 'session_update',
                    'status': session.status,
                    'session_id': session.id,
                    'date': session.date.strftime('%b %d, %Y'),
                    'reason': session.cancellation_reason or 'No reason provided',
                    'from_who': session.tutor_schedule.student.first_name if session.status == 'canceled_by_parent' else 'You'
                })
            elif session.status == 'completed':
                notifications.append({
                    'message': f'Session completed with {session.tutor_schedule.student.first_name}',
                    'type': 'session_update',
                    'status': session.status,
                    'session_id': session.id,
                    'date': session.date.strftime('%b %d, %Y'),
                    'from_who': session.tutor_schedule.student.first_name
                })


    elif request.user.role == 'parent':
   
        accepted_schedules = TutorSchedule.objects.filter(
            parent=request.user,
            status='confirmed'
        ).count()

        if accepted_schedules > 0:
            notifications.append({
                'message': f'Tutor accepted {accepted_schedules} schedule(s)',
                'type': 'schedule_update',
                'status': 'confirmed'
            })

   
        recent_sessions = TutorSession.objects.filter(
            tutor_schedule__parent=request.user,
            updated_at__gte=datetime.now() - timedelta(days=7)
        ).exclude(status='pending').order_by('-updated_at')[:5]

        for session in recent_sessions:
            if session.status == 'confirmed':
                notifications.append({
                    'message': f'Session confirmed with {session.tutor_schedule.tutor.user.first_name}',
                    'type': 'session_update',
                    'status': session.status,
                    'session_id': session.id,
                    'date': session.date.strftime('%b %d, %Y'),
                    'from_who': session.tutor_schedule.tutor.user.first_name,
                    'subject': session.subject.name
                })
            elif session.status in ['canceled', 'canceled_by_parent', 'canceled_by_tutor']:
                notifications.append({
                    'message': f'Session canceled with {session.tutor_schedule.tutor.user.first_name}',
                    'type': 'session_update',
                    'status': session.status,
                    'session_id': session.id,
                    'date': session.date.strftime('%b %d, %Y'),
                    'reason': session.cancellation_reason or 'No reason provided',
                    'from_who': 'You' if session.status == 'canceled_by_parent' else session.tutor_schedule.tutor.user.first_name
                })
            elif session.status == 'completed':
                notifications.append({
                    'message': f'Session completed with {session.tutor_schedule.tutor.user.first_name}',
                    'type': 'session_update',
                    'status': session.status,
                    'session_id': session.id,
                    'date': session.date.strftime('%b %d, %Y'),
                    'from_who': session.tutor_schedule.tutor.user.first_name
                })

    return JsonResponse({
        'notifications': notifications,
        'unread_count': len(notifications),
    })


 
@require_POST
def update_booking_status(request):
    student_id = request.POST.get('student_id')
    action = request.POST.get('action')
    
    try:
    
        schedules = TutorSchedule.objects.filter(student_id=student_id, tutor=request.user.tutor_profile)
        sessions = TutorSession.objects.filter(tutor_schedule__student_id=student_id, tutor_schedule__tutor     =request.user.tutor_profile)
        
        if action == 'accept':
            new_status = 'confirmed'
        elif action == 'decline':
            new_status = 'declined'
        else:
            return JsonResponse({'success': False, 'message': 'Invalid action'})

        schedules.update(status=new_status)
        

        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})



def view_all_student_schedules(request):
    """Retrieve and display all tutor schedules for the logged-in parent."""
    parent = request.user
    tutor_schedules = TutorSchedule.objects.filter(parent=parent).order_by('start_date')

    grouped_schedules = []
    for schedule in tutor_schedules:
        student = schedule.student
        subjects = list(set(session.subject.name for session in schedule.sessions.all()))
        
        # Calculate completion percentage
        completion_percentage = 0
        if schedule.total_hours > 0:
            completion_percentage = round((schedule.completed_hours / schedule.total_hours) * 100, 2)

        grouped_schedules.append({
            'schedule': schedule,
            'student': student,
            'student_name': f"{student.first_name} {student.last_name}" if student else "No student assigned",
            'tutor': schedule.tutor,
            'subjects': ", ".join(subjects) if subjects else "No subjects scheduled",
            'start_date': schedule.start_date,
            'end_date': schedule.end_date,
            'status': schedule.get_status_display(),
            'completion_percentage': completion_percentage,
            'completed_hours': schedule.completed_hours,
            'total_hours': schedule.total_hours,
        })

    return render(request, 'users/student_schedules.html', {
        "grouped_schedules": grouped_schedules, 
        "tutor_schedules": tutor_schedules,
    })




#ADMIN SIDE

def adminlogin(request):
    if request.method == "POST":
        username_or_email = request.POST.get('email')
        password = request.POST.get('password')

        user = None

       
        if '@' in username_or_email:
            try:
                user = UserProfile.objects.get(email=username_or_email)
                username_or_email = user.username 
            except UserProfile.DoesNotExist:
                user = None

      
        user = authenticate(request, username=username_or_email, password=password)

       
        if user is not None and (user.is_superuser or user.groups.filter(name='Admin').exists()):
            login(request, user)
            return redirect('dashboard')  

        else:
            return render(request, 'admin/adminlogin.html', {
                'error': True,
                'error_message': "Invalid admin credentials. Please try again."
            })

    return render(request, 'admin/adminlogin.html')

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Admin').exists())





@admin_required
@user_passes_test(is_admin, login_url='adminlogin')
def pending(request):
    pending_tutors_list = TutorProfile.objects.filter(
        is_approved=False,
        is_declined=False,
        is_restricted=False
    ).select_related('user').order_by('-id')  # Order by newest first
    
    paginator = Paginator(pending_tutors_list, 5)  # Show 10 tutors per page
    page_number = request.GET.get('page')
    pending_tutors = paginator.get_page(page_number)
    
    return render(request, 'admin/pending.html', {'pending_tutors': pending_tutors})


def send_email_async(subject, message, recipient_list, html_message=None):
    def email_thread():
        send_mail(
            subject=subject,
            message=message,  
            from_email="tutoriafs2024@gmail.com",
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=html_message,  
        )
    
    threading.Thread(target=email_thread).start()

@admin_required
@csrf_exempt
def approve_tutor(request, tutor_id):
    if request.method == "POST":
        tutor = get_object_or_404(TutorProfile, id=tutor_id)
        tutor.approve()

        user_email = tutor.user.email  
        subject = " Tutor Approval Notification"
        message = f"Dear {tutor.user.first_name},\n\nCongratulations! Your tutor profile has been approved. You can now access tutor features on our platform.\n\nBest regards,\nTutoria Team!"
        
   
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #4CAF50;"> Congratulations, {tutor.user.first_name}!</h2>
            <p>Your tutor profile has been <strong style="color: green;">approved</strong>. You can now access all tutor features on our platform.</p>
            <a href="https://yourwebsite.com/login" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; border-radius: 5px;">Login Now</a>
            <p>Best regards,</p>
            <p><strong>Tutoria Team</strong></p>
        </body>
        </html>
        """

        send_email_async(subject, message, [user_email], html_message=html_message)

        return JsonResponse({'status': 'approved'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@admin_required
@csrf_exempt
def decline_tutor(request, tutor_id):
    if request.method == "POST":
        tutor = get_object_or_404(TutorProfile, id=tutor_id)
        tutor.decline()

        user_email = tutor.user.email  
        subject = " Tutor Application Update"
        message = f"Dear {tutor.user.first_name},\n\nWe regret to inform you that your tutor application has been declined. If you have any questions, please contact support.\n\nBest regards,\nTutoria Team"

        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #FF5733;"> Dear {tutor.user.first_name},</h2>
            <p>We regret to inform you that your tutor application has been <strong style="color: red;">declined</strong>. If you have any questions, please contact support.</p>
            <a href="mailto:tutoriafs2024@gmail.com" style="background-color: #FF5733; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; border-radius: 5px;">Contact Support</a>
            <p>Best regards,</p>
            <p><strong>Tutoria Team</strong></p>
        </body>
        </html>mj   
        """

        send_email_async(subject, message, [user_email], html_message=html_message)

        return JsonResponse({'status': 'declined'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)



@admin_required
@user_passes_test(is_admin, login_url='adminlogin')
def approved(request):
    approved_tutors_list = TutorProfile.objects.filter(
        is_approved=True,
        is_declined=False
    ).select_related('user').order_by('-id') 
    
    paginator = Paginator(approved_tutors_list, 5) 
    page_number = request.GET.get('page')
    approved_tutors = paginator.get_page(page_number)
    
    return render(request, 'admin/approved.html', {'approved_tutors': approved_tutors})

@csrf_exempt
def restrict_tutor(request, tutor_id):
    if request.method == "POST":
        tutor = get_object_or_404(TutorProfile, id=tutor_id)
        tutor.is_restricted = True
        tutor.is_approved = False  
        tutor.save()

        user_email = tutor.user.email  
        subject = "Tutor Restriction Notice"
        message = f"Dear {tutor.user.first_name},\n\nWe regret to inform you that your tutor profile has been restricted due to a violation of our policies. If you believe this is a mistake, please contact support.\n\nBest regards,\nTutoria Team!"
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #ff0000;">Important Notice, {tutor.user.first_name}</h2>
            <p>Your tutor profile has been <strong style="color: red;">restricted</strong> due to policy violations.</p>
            <p>If you have any concerns, please contact our support team.</p>
            <p>Best regards,</p>
            <p><strong>Tutoria Team</strong></p>
        </body>
        </html>
        """

        send_email_async(subject, message, [user_email], html_message=html_message)

        return JsonResponse({'status': 'restricted'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)



@admin_required
@user_passes_test(is_admin, login_url='adminlogin')
def declined(request):
    # Get declined tutors ordered by most recently declined first
    declined_tutors_list = TutorProfile.objects.filter(
        is_declined=True
    ).select_related('user').annotate(
        status_order=Case(
            When(is_restricted=True, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('-status_order', '-id')
    
    # Pagination - 10 tutors per page
    paginator = Paginator(declined_tutors_list, 10)
    page_number = request.GET.get('page')
    declined_tutors = paginator.get_page(page_number)
    
    return render(request, 'admin/declined.html', {
        'declined_tutors': declined_tutors
    })


@admin_required
@user_passes_test(is_admin, login_url='adminlogin')
def restricted(request):
    restricted_tutors = TutorProfile.objects.filter(is_restricted=True)  
    return render(request, 'admin/restricted.html', {'restricted_tutors': restricted_tutors})



def admin_logout_function(request):
    logout(request)
    return redirect('adminlogin')  




def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

def curriculum_management(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        response_data = {'success': False, 'message': ''}

        try:
            if form_type == 'subject':
                subject_name = request.POST.get('subject_name', '').strip()
                if not subject_name:
                    response_data['message'] = "Subject name cannot be empty!"
                else:
                    subject, created = Subject.objects.get_or_create(name=subject_name)
                    if created:
                        response_data.update({
                            'success': True,
                            'message': f"Subject '{subject_name}' added successfully!",
                            'data': {
                                'id': subject.id,
                                'name': subject.name
                            }
                        })
                    else:
                        response_data['message'] = f"Subject '{subject_name}' already exists!"

            elif form_type == 'topic':
                subject_id = request.POST.get('subject_id')
                topic_name = request.POST.get('topic_name', '').strip()
                topic_description = request.POST.get('topic_description', '').strip()
                
                if not topic_name:
                    response_data['message'] = "Topic name cannot be empty!"
                else:
                    try:
                        subject = Subject.objects.get(id=subject_id)
                        topic, created = Topic.objects.get_or_create(
                            name=topic_name,
                            subject=subject,
                            defaults={'description': topic_description}
                        )
                        if created:
                            response_data.update({
                                'success': True,
                                'message': f"Topic '{topic_name}' added successfully!",
                                'data': {
                                    'id': topic.id,
                                    'name': topic.name,
                                    'subject': subject.name,
                                    'description': topic.description
                                }
                            })
                        else:
                            response_data['message'] = f"Topic '{topic_name}' already exists for this subject!"
                    except Subject.DoesNotExist:
                        response_data['message'] = "Invalid subject selected!"

            elif form_type == 'subtopic':
                topic_id = request.POST.get('topic_id')
                subtopic_name = request.POST.get('subtopic_name', '').strip()
                subtopic_description = request.POST.get('subtopic_description', '').strip()
                
                if not subtopic_name:
                    response_data['message'] = "SubTopic name cannot be empty!"
                else:
                    try:
                        topic = Topic.objects.get(id=topic_id)
                        subtopic, created = SubTopic.objects.get_or_create(
                            name=subtopic_name,
                            topic=topic,
                            defaults={'description': subtopic_description}
                        )
                        if created:
                            response_data.update({
                                'success': True,
                                'message': f"SubTopic '{subtopic_name}' added successfully!",
                                'data': {
                                    'id': subtopic.id,
                                    'name': subtopic.name,
                                    'topic': topic.name,
                                    'description': subtopic.description
                                }
                            })
                        else:
                            response_data['message'] = f"SubTopic '{subtopic_name}' already exists for this topic!"
                    except Topic.DoesNotExist:
                        response_data['message'] = "Invalid topic selected!"

            # Always return JSON response for AJAX requests
            if is_ajax(request):
                return JsonResponse(response_data)
            else:
                if response_data['success']:
                    messages.success(request, response_data['message'])
                else:
                    messages.error(request, response_data['message'])
                return redirect('curriculum_management')

        except Exception as e:
            response_data['message'] = f"An error occurred: {str(e)}"
            if is_ajax(request):
                return JsonResponse(response_data, status=500)
            else:
                messages.error(request, response_data['message'])
                return redirect('curriculum_management')
    
    # For GET requests
    subjects = Subject.objects.all().prefetch_related('topics')
    topics = Topic.objects.all().select_related('subject')
    subtopics = SubTopic.objects.all().select_related('topic__subject')
    
    return render(request, 'admin/curriculum_management.html', {
        'subjects': subjects,
        'topics': topics,
        'subtopics': subtopics
    })

@require_POST
def delete_subject(request, subject_id):
    return delete_item(request, 'subject', subject_id)

@require_POST
def delete_topic(request, topic_id):
    return delete_item(request, 'topic', topic_id)

@require_POST
def delete_subtopic(request, subtopic_id):
    return delete_item(request, 'subtopic', subtopic_id)

def delete_item(request, item_type, item_id):
    model_map = {
        'subject': Subject,
        'topic': Topic,
        'subtopic': SubTopic
    }
    
    if item_type not in model_map:
        return JsonResponse({
            'success': False,
            'message': 'Invalid item type'
        }, status=400)
    
    try:
        item = model_map[item_type].objects.get(id=item_id)
        item_name = item.name
        item.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{item_type.capitalize()} "{item_name}" deleted successfully!'
        })
    
    except model_map[item_type].DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': f'{item_type.capitalize()} not found'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting {item_type}: {str(e)}'
        }, status=500)

@require_POST
def edit_subject(request, subject_id):
    return edit_item(request, 'subject', subject_id)

@require_POST
def edit_topic(request, topic_id):
    return edit_item(request, 'topic', topic_id)

@require_POST
def edit_subtopic(request, subtopic_id):
    return edit_item(request, 'subtopic', subtopic_id)

@require_POST
def edit_item(request, item_type, item_id):
    try:
        # Parse JSON data from request
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
        
        model_map = {
            'subject': {
                'model': Subject,
                'fields': ['name'],
                'foreign_keys': {}
            },
            'topic': {
                'model': Topic,
                'fields': ['name', 'description'],
                'foreign_keys': {
                    'subject': Subject
                }
            },
            'subtopic': {
                'model': SubTopic,
                'fields': ['name', 'description'],
                'foreign_keys': {
                    'topic': Topic
                }
            }
        }

        if item_type not in model_map:
            return JsonResponse({
                'success': False,
                'message': 'Invalid item type'
            }, status=400)

        config = model_map[item_type]
        item = config['model'].objects.get(id=item_id)

        # Validate required fields
        for field in config['fields']:
            if not data.get(field, '').strip():
                return JsonResponse({
                    'success': False,
                    'message': f'{field.capitalize()} is required'
                }, status=400)

        # Update fields
        for field in config['fields']:
            if field in data:
                setattr(item, field, data[field].strip())

        # Update foreign keys
        for fk_field, fk_model in config['foreign_keys'].items():
            if fk_field in data:
                try:
                    related_obj = fk_model.objects.get(id=data[fk_field])
                    setattr(item, fk_field, related_obj)
                except (ValueError, fk_model.DoesNotExist):
                    return JsonResponse({
                        'success': False,
                        'message': f'Invalid {fk_field} selected'
                    }, status=400)

        item.save()

        return JsonResponse({
            'success': True,
            'message': f'{item_type.capitalize()} updated successfully!',
            'data': {
                'id': item.id,
                'name': item.name,
                **({'description': item.description} if hasattr(item, 'description') else {}),
                **({'subject_id': item.subject.id} if hasattr(item, 'subject') else {}),
                **({'topic_id': item.topic.id} if hasattr(item, 'topic') else {})
            }
        })

    except config['model'].DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': f'{item_type.capitalize()} not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


from .forms import AssessmentQuestionForm, AnswerChoiceForm


def add_assessment_question(request):
    if request.method == "POST":    
        question_form = AssessmentQuestionForm(request.POST)
        answer_forms = [AnswerChoiceForm(request.POST, prefix=str(i)) for i in range(4)]  

        if question_form.is_valid() and all(form.is_valid() for form in answer_forms):
            question = question_form.save()  

            for form in answer_forms:
                answer = form.save(commit=False)
                answer.question = question 
                answer.save()

            messages.success(request, "Question and answers added successfully!")
            return redirect('add_question')  

    else:
        question_form = AssessmentQuestionForm()
        answer_forms = [AnswerChoiceForm(prefix=str(i)) for i in range(4)]  

    return render(request, 'users/add_question.html', {
        'question_form': question_form,
        'answer_forms': answer_forms
    })





def add_tutor_assessment(request):
    if request.method == "POST":
        question_form = TutorAssessmentQuestionForm(request.POST)
        answer_forms = [TutorAnswerChoiceForm(request.POST, prefix=str(i)) for i in range(4)]

        print("POST Data:", request.POST)  # Debugging

        if question_form.is_valid() and all(form.is_valid() for form in answer_forms):
            question = question_form.save()

            for form in answer_forms:
                answer = form.save(commit=False)
                answer.question = question
                print("Saving Answer Choice:", answer.text) 
                answer.save()

            messages.success(request, "Question and answers added successfully!")
            return redirect("add_tutor_assessment")
        else:
            print("Form Errors:", question_form.errors, [form.errors for form in answer_forms]) 

    else:
        question_form = TutorAssessmentQuestionForm()
        answer_forms = [TutorAnswerChoiceForm(prefix=str(i)) for i in range(4)]

    return render(request, "users/add_tutor_assessment.html", {
        "question_form": question_form,
        "answer_forms": answer_forms,
    })



def dashboard_view(request):
    tutor_count = TutorProfile.objects.filter(is_approved=True).count()
    
    # Get parent count excluding admin/superusers
    parent_count = UserProfile.objects.filter(
        role='parent',
        is_superuser=False,
        is_staff=False
    ).count()
    
    student_count = StudentProfile.objects.count()
    
    session_stats = {
        'total_sessions': TutorSession.objects.count(),
        'today_sessions': TutorSession.objects.filter(date=timezone.now().date()).count(),
        'completed_sessions': TutorSession.objects.filter(status='completed').count(),
        'pending_sessions': TutorSession.objects.filter(status='pending').count(),
        'upcoming_sessions': TutorSession.objects.filter(
            date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).count(),
    }

    schedule_stats = {
        'total_schedules': TutorSchedule.objects.count(),
        'active_schedules': TutorSchedule.objects.filter(
            status='confirmed',
            end_date__gte=timezone.now().date()
        ).count(),
        'pending_approval': TutorSchedule.objects.filter(status='pending').count(),
    }

    top_tutors = TutorProfile.objects.filter(is_approved=True).annotate(
        total_schedules=Count('tutor_schedules', distinct=True),
        confirmed_schedules=Count(
            'tutor_schedules',
            filter=Q(tutor_schedules__status='confirmed'),
            distinct=True
        ),
        total_sessions=Count(
            'tutor_schedules__sessions',
            distinct=True
        ),
        completed_sessions=Count(
            'tutor_schedules__sessions',
            filter=Q(tutor_schedules__sessions__status='completed'),
            distinct=True
        ),
        review_count=Count('reviews', distinct=True),
        avg_rating=Avg('reviews__rating')
    ).order_by('-total_schedules')[:3]

    top_performing_tutor = TutorProfile.objects.filter(is_approved=True).annotate(
        completed_sessions=Count(
            'tutor_schedules__sessions',
            filter=Q(tutor_schedules__sessions__status='completed'),
            distinct=True
        ),
        review_count=Count('reviews', distinct=True),
        avg_rating=Avg('reviews__rating')
    ).order_by('-completed_sessions').first()

    context = {
        'tutor_count': tutor_count,
        'parent_count': parent_count,
        'student_count': student_count,
        **session_stats,
        **schedule_stats,
        'top_tutors': top_tutors,
        'top_performing_tutor': top_performing_tutor,
    }

    return render(request, 'admin/dashboard.html', context)


def tutor_list_view(request):
    tutors = TutorProfile.objects.filter(is_approved=True).annotate(
        average_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews')
    )


    search_query = request.GET.get('search', '')
    if search_query:
        tutors = tutors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )


    subject_filter = request.GET.get('subject')
    if subject_filter:
        tutors = tutors.filter(subjects__id=subject_filter)


    sort_by = request.GET.get('sort', '-average_rating')
    valid_sort_fields = ['-average_rating', '-reviews_count', '-user__date_joined']
    if sort_by in valid_sort_fields:
        tutors = tutors.order_by(sort_by)

    all_subjects = Subject.objects.all().order_by('name')
    

    stats = tutors.aggregate(
        total_reviews=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    )
    
    featured_tutor = tutors.filter(reviews_count__gte=1).order_by('-average_rating').first()


    SHOW_PAGINATION_THRESHOLD = 5
    paginator = Paginator(tutors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    

    show_pagination = paginator.count > SHOW_PAGINATION_THRESHOLD

    context = {
        'tutors': page_obj,
        'total_reviews': stats['total_reviews'],
        'avg_rating': stats['avg_rating'] or 0,
        'featured_tutor': featured_tutor,
        'all_subjects': all_subjects,
        'show_pagination': show_pagination,  
    }
    return render(request, 'admin/reviews.html', context)


from django.core.paginator import Paginator

def tutor_reviews_detail(request, tutor_id):
    tutor = get_object_or_404(TutorProfile, id=tutor_id)
    reviews = tutor.reviews.all()
    
    # Apply filters
    if request.GET.get('sort'):
        reviews = reviews.order_by(request.GET['sort'])
    if request.GET.get('rating'):
        reviews = reviews.filter(rating=request.GET['rating'])
    if request.GET.get('search'):
        reviews = reviews.filter(comment__icontains=request.GET['search'])
    
    paginator = Paginator(reviews, 10)  # 10 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tutor': tutor,
        'page_obj': page_obj,
    }
    return render(request, 'admin/review_comments.html', context)


def link_assessment_questions(request):
    if request.method == "POST":
        student_question_id = request.POST.get("student_question")
        tutor_question_id = request.POST.get("tutor_question")

        if student_question_id and tutor_question_id:
            student_question = AssessmentQuestion.objects.get(id=student_question_id)
            tutor_question = TutorAssessmentQuestion.objects.get(id=tutor_question_id)

         
            tutor_question.linked_student_question = student_question
            tutor_question.save()

          
            student_choices = AnswerChoice.objects.filter(question=student_question)
            tutor_choices = TutorAnswerChoice.objects.filter(question=tutor_question)

            for s_choice, t_choice in zip(student_choices, tutor_choices):
                t_choice.linked_student_answer = s_choice
                t_choice.save()

    student_questions = AssessmentQuestion.objects.all()
    tutor_questions = TutorAssessmentQuestion.objects.all()

    return render(request, 'users/link_assessment.html', {
        'student_questions': student_questions,
        'tutor_questions': tutor_questions,
    })

from django.views.decorators.http import require_GET

@require_GET
def check_existing_schedule(request):
    student_id = request.GET.get('student_id')
    tutor_id = request.GET.get('tutor_id')
    subject_id = request.GET.get('subject_id')
    
    if not all([student_id, tutor_id, subject_id]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        existing = TutorSchedule.objects.filter(
            tutor_id=tutor_id,
            parent_id=request.user.id,
            student_id=student_id,
            status__in=["pending", "confirmed"],
            sessions__subject_id=subject_id
        ).exists()
        
        if existing:
            from django.apps import apps
            Subject = apps.get_model('your_app_name', 'Subject')
            subject_name = Subject.objects.get(id=subject_id).name
            return JsonResponse({
                'exists': True,
                'subject_name': subject_name
            })
        return JsonResponse({'exists': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

def get_student_id(request):
    return JsonResponse({
        'student_id': request.session.get('student_id')
    })


def check_unread_messages(request):
    user = request.user
    

    conversations = Conversation.objects.filter(
        Q(tutor=user) | Q(parent=user)
    )


    unread_count = Message.objects.filter(
        conversation__in=conversations,
        is_read=False,
    ).exclude(sender=user).count()

    print("Unread Messages:", unread_count) 

    return JsonResponse({'unread_count': unread_count})

@require_POST
@user_login_required
def mark_messages_as_read(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        messages = Message.objects.filter(conversation=conversation, is_read=False).exclude(sender=request.user)
        messages.update(is_read=True)
        return JsonResponse({'success': True})
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False}, status=404)
    


@user_login_required

#SWITCH INTO TUTOR ACCOUNT
def switch_to_tutor(request):
   
    request.session.pop('user_role', None)
    request.session.pop('profile_photo', None)


    if not hasattr(request.user, 'tutor_profile'):
        messages.info(request, "Please complete your tutor profile setup")
        return redirect('user_about')  

 
    request.session['user_id'] = request.user.id
    request.session['user_role'] = 'tutor'
    if request.user.tutor_profile.profile_photo:
        request.session['profile_photo'] = request.user.tutor_profile.profile_photo.url

    messages.success(request, "Switched to tutor mode successfully")
    return redirect('tutor_profile')

@user_login_required

#SWITCH INTO PARENT ACCOUNT
def switch_to_parent(request):

    request.session.pop('user_role', None)
    request.session.pop('profile_photo', None)


    request.session['user_role'] = 'parent'
    if hasattr(request.user, 'userprofile') and request.user.userprofile.profile_photo:
        request.session['profile_photo'] = request.user.userprofile.profile_photo.url

    messages.success(request, "Switched to parent mode")
    return redirect('parent_profile')



@require_POST
@csrf_exempt
def check_schedule_conflicts(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        tutor_id = data.get('tutor_id')
        subject_ids = data.get('subject_ids', [])
        
        if not all([student_id, tutor_id, subject_ids]):
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        conflicting_subjects = []
        
   
        existing_schedules = TutorSchedule.objects.filter(
            student_id=student_id,
            tutor_id=tutor_id,
            status__in=["pending", "confirmed"]
        ).prefetch_related('sessions__subject')
        
   
        for schedule in existing_schedules:
            for session in schedule.sessions.all():
                if str(session.subject.id) in subject_ids and session.subject.id not in conflicting_subjects:
                    conflicting_subjects.append(session.subject.id)
        
        if conflicting_subjects:
            subject_names = Subject.objects.filter(id__in=conflicting_subjects).values_list('name', flat=True)
            return JsonResponse({
                'hasConflict': True,
                'conflicting_subjects': conflicting_subjects,
                'message': f"Student already has active sessions for: {', '.join(subject_names)}"
            })
            
        return JsonResponse({'hasConflict': False})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@require_POST
@user_login_required
def assign_substitute(request):
    booking_id = request.POST.get('booking_id')
    substitute_name = request.POST.get('substitute_name', '').strip()
    substitute_contact = request.POST.get('substitute_contact', '').strip()
    substitute_street = request.POST.get('substitute_street', '').strip()
    substitute_barangay = request.POST.get('substitute_barangay', '').strip()
    
    try:
        session = TutorSession.objects.get(id=booking_id)
        
        # Verify the requesting user has permission
        if not (request.user == session.tutor_schedule.tutor.user or request.user.is_staff):
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        session.substitute_name = substitute_name
        session.substitute_contact = substitute_contact
        session.substitute_street = substitute_street
        session.substitute_barangay = substitute_barangay
        session.is_substitute = True
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': f"Substitute tutor {substitute_name} assigned successfully"
        })
        
    except TutorSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    

from datetime import date

def calculate_age(birthdate):
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def student_list_view(request):

    students = StudentProfile.objects.select_related('parent').all()
    

    for student in students:
        student.get_age = calculate_age(student.birthday)
    

    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(parent__first_name__icontains=search_query) |
            Q(parent__last_name__icontains=search_query) |
            Q(parent__username__icontains=search_query)
        )
    
    
    students = students.order_by('last_name')
    

    paginator = Paginator(students, 10)  
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    
    context = {
        'students': students,
        'search_query': search_query,
    }
    
    return render(request, 'admin/students.html', context)




def parent_profile_view(request, parent_id):
    parent = get_object_or_404(UserProfile, id=parent_id, role='parent')
    students = StudentProfile.objects.filter(parent=parent).select_related('parent')
    
    for student in students:
        student.age = student.get_age()
    
    context = {
        'parent': parent,
        'students': students,
        'opts': UserProfile._meta,
        'has_view_permission': True,
        'original': parent,
        'is_popup': False,
        'title': f"Parent Profile: {parent.get_full_name()}",
    }
    return render(request, 'admin/student_parent.html', context)



@login_required
def tutor_admin_profile(request, tutor_id):
    tutor = get_object_or_404(TutorProfile, id=tutor_id)
    reviews = Review.objects.filter(tutor=tutor).order_by('-created_at')
    
    context = {
        'tutor': tutor,
        'reviews': reviews,
    }
    return render(request, 'admin/tutor_reviews_profile.html', context)