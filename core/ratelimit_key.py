def rate_key(group, request):
    if request.user.is_authenticated:
        return f"user:{request.user.id}"
    
    session = request.session.session_key
    if not session:
        request.session.save
        session = request.session.session_key

    ip = request.META.get("REMOTE_ADDR")

    return f"anon:{ip}:{session}"