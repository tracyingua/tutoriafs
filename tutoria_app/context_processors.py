def user_profile(request):
    if request.user.is_authenticated:
        profile_photo = (
            request.user.tutor_profile.profile_photo.url
            if hasattr(request.user, 'tutor_profile') and request.user.tutor_profile.profile_photo
            else None
        )
    else:
        profile_photo = None

    return {'profile_photo': profile_photo}
