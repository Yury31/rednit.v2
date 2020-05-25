from django.utils import timezone

from social.models import Profile


class MyBackend:

    def get_user(self, user_id):
        try:
            user = Profile.objects.get(pk=user_id)
            user.last_online = timezone.now()
            user.save(update_fields=['last_online'])
            return user
        except Profile.DoesNotExist:
            return None
