def rate_key(group, request, *_, **__):
    if request.user.is_authenticated:
        return f"user:{request.user.id}"

    ua = request.META.get("HTTP_USER_AGENT")
    ip = request.META.get("HTTP_X_REAL_IP")
    return f"anon:{ip}:{ua}"
