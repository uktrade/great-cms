def approve_new_user(sender, instance, created, *args, **kwarg):
    if created:
        instance.is_staff = True
        instance.save()
