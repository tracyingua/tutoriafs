"""
URL configuration for tutoria project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from tutoria_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index,name ="index"),
    path('signup', views.signup,name ="signup"),
    path('forgot', views.forgot,name ="forgot"),
    path('code/<int:user_id>/', views.code, name='code'),  
    path('reset/<int:user_id>/', views.reset_password, name='reset_password'),
    path('signin', views.signin,name ="signin"),
    path('logout', views.logout_function,name ="logout"),
    path("find_tutor/", views.find_tutor, name="find_tutor"),  

    path('tutoria', views.tutoria,name ="tutoria"),
    path('user_chat/', views.user_chat, name='user_chat'),
    path('chat/<int:conversation_id>/', views.user_chat, name='chat_detail'),
    path('chat/send-message/', views.send_message, name='send_message'),
    path("chat/start/<int:user_id>/", views.start_conversation, name="start_conversation"),
    path("get-new-messages/", views.get_new_messages, name="get_new_messages"),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    

    path('subjects', views.subjects,name ="subjects"),
    path('subjects_2/<str:subject_name>/', views.subjects_2, name='subjects_2'),
    path('user_about', views.user_about,name ="user_about"),
    path('create_schedule/', views.create_schedule, name='create_schedule'),
    path('subject_price', views.subject_price,name ="subject_price"),
    path("tutor_assessment/", views.tutor_assessment, name="tutor_assessment"),
    path('user_about_2', views.user_about_2,name ="user_about_2"),
    path('congrats', views.congrats,name ="congrats"),
   
    path('congrats_reset', views.congrats_reset,name ="congrats_reset"),
    path('teacher_profile/<int:id>/', views.teacher_profile, name='teacher_profile'),
    path('teacher_profile_2/<int:id>/', views.teacher_profile_2, name='teacher_profile_2'),


    path('teacher_profile/<int:id>/create-schedule/', views.create_schedule, name='create_schedule_teacher_profile'),
    path('teacher_profile_2/<int:id>/create-schedule/', views.create_schedule, name='create_schedule_teacher_profile_2'),

    path("submit_feedback/<int:tutor_id>/", views.submit_feedback, name="submit_feedback"),
    path('parent_profile', views.parent_profile ,name ="parent_profile"),
    path('edit_parent_profile', views.edit_parent_profile ,name ="edit_parent_profile"),
    path('register_student', views.register_student,name ="register_student"),
    path("edit_student<int:student_id>/", views.edit_student, name="edit_student"),
    path('student_profile<int:student_id>/', views.student_profile, name='student_profile'),
    path('student/<int:student_id>/sessions/<int:subject_id>/', views.student_sessions, name='student_sessions'),
    path('student_assessment/<int:student_id>/', views.student_assessment, name='student_assessment'),
    path('booking/<int:student_id>/<str:action>/', views.update_booking_status, name='update_booking_status'),
    path('student_schedules/', views.view_all_student_schedules, name='student_schedules'),
    path('accept-booking/', views.accept_booking, name='accept_booking'),
    path('decline-booking/', views.decline_booking, name='decline_booking'),
    path('complete-booking/', views.complete_booking, name='complete_booking'),
    path('cancel-booking/', views.cancel_booking, name='cancel_booking'),
    path('cancel-session/', views.cancel_session, name='cancel_session'),
    path('withdraw-schedule/', views.withdraw_schedule, name='withdraw_schedule'),
    path('student_list', views.student_list_view, name='student_list'),
    path('parent_profile/<int:parent_id>/', views.parent_profile_view, name='parent_profile'),
     path('tutor_admin_profile/<int:tutor_id>/', views.tutor_admin_profile, name='tutor_admin_profile'),

    path('get-tutor-availability/<int:tutor_id>/', views.get_tutor_availability, name='get_tutor_availability'),
    path('tutor_profile', views.tutor_profile ,name ="tutor_profile"),
    path('tutor_bookings', views.tutor_bookings ,name ="tutor_bookings"),
    path('tutor/bookings/<int:student_id>/details/', views.tutor_booking_details, name='tutor_booking_details'),

    path('update-booking-status/', views.update_booking_status, name='update_booking_status'),
    path('api/check-schedule/', views.check_existing_schedule, name='check_schedule'),
    path('api/check-unread-messages/', views.check_unread_messages, name='check-unread-messages'),
    path('mark-messages-as-read/<int:conversation_id>/', views.mark_messages_as_read, name='mark_messages_as_read'),
    path('switch-to-tutor/', views.switch_to_tutor, name='switch_to_tutor'),
    path('switch-to-parent/', views.switch_to_parent, name='switch_to_parent'),
    path('check-schedule-conflicts/', views.check_schedule_conflicts, name='check-schedule-conflicts'),
    path('assign-substitute/', views.assign_substitute, name='assign_substitute'),
    path('reviews/', views.tutor_list_view, name='reviews'),
    path('tutors/<int:tutor_id>/reviews/', views.tutor_reviews_detail, name='tutor_reviews_detail'),
    

    path('cirruculum_management', views.curriculum_management, name='curriculum_management'),
    path('delete-subject/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('delete-topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    path('delete-subtopic/<int:subtopic_id>/', views.delete_subtopic, name='delete_subtopic'),
    
    # Edit URLs
    path('edit-subject/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path('edit-topic/<int:topic_id>/', views.edit_topic, name='edit_topic'),
    path('edit-subtopic/<int:subtopic_id>/', views.edit_subtopic, name='edit_subtopic'),
    





     path("get_topics_for_subjects/", views.get_topics_for_subjects, name="get_topics_for_subjects"),
     path("update_tutor_profile/", views.update_tutor_profile, name="update_tutor_profile"),
     path("update_tutor_profile_2/", views.update_tutor_profile_2, name="update_tutor_profile_2"),
     path('update_subject_prices/', views.update_subject_prices, name='update_subject_prices'),
     path('adminlogin', views.adminlogin ,name ="adminlogin"),
    

     path('delete/<str:model_name>/<int:item_id>/', views.delete_item, name='delete_item'),

     path('dashboard/', views.dashboard_view, name='dashboard'),
     path('pending', views.pending ,name ="pending"),
     path('approved', views.approved ,name ="approved"),
     path('declined', views.declined ,name ="declined"),
     path('restricted', views.restricted ,name ="restricted"),
     path('admin_logout', views.admin_logout_function,name ="admin_logout"),
     path('approve/<int:tutor_id>/', views.approve_tutor, name='approve_tutor'),
     path('decline/<int:tutor_id>/', views.decline_tutor, name='decline_tutor'),
     path('restrict/<int:tutor_id>/', views.restrict_tutor, name='restrict_tutor'),
     path('add_question/', views.add_assessment_question, name='add_question'),
     path('add_tutor_assessment/', views.add_tutor_assessment, name='add_tutor_assessment'),
     path('link_assessment/', views.link_assessment_questions, name='link_assessment'),



    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)