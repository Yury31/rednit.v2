from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView
from django.contrib.auth.decorators import login_required

from social.forms import RegisterForm, ProfileForm, MessageForm
from social.models import Profile, Chat


class UserListView(ListView):
    queryset = Profile.objects.all()
    context_object_name = 'users'
    paginate_by = 6
    template_name = 'users_list.html'


@login_required
def user_details(request, pk):
    user = get_object_or_404(Profile, pk=pk)
    is_liked = False
    if user.likes.filter(id=request.user.id).exists():
        is_liked = True
    if user.birth_date is None:
        return render(request, 'registration/profile.html', context={
            'user': user,
            'is_liked': is_liked,
            'total_likes': user.total_likes(),
            'get_online_info': user.get_online_info(),
            'is_online': user.is_online()})
    return render(request, 'registration/profile.html', context={
        'user': user, 'is_liked': is_liked,
        'total_likes': user.total_likes(),
        'age': user.age(),
        'get_online_info': user.get_online_info(),
        'is_online': user.is_online()
    })


def like_profile(request):
    user = get_object_or_404(Profile, id=request.POST.get('profile_id'))
    is_liked = False
    if user.likes.filter(id=request.user.id).exists():
        user.likes.remove(request.user)
        is_liked = False
    else:
        user.likes.add(request.user)
        messages.success(request, u"You liked the user !")
        is_liked = True
    return redirect('user_detail', pk=user.pk)


class HomeView(TemplateView):
    template_name = "home.html"


class RegisterView(TemplateView):
    template_name = "registration/register.html"

    def dispatch(self, request, *args, **kwargs):
        form = RegisterForm()
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                self.create_new_user(form)
                messages.success(request, u"Вы успешно зарегистрировались!")
                return redirect(reverse("login"))

        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    def create_new_user(self, form):
        email = None
        if 'email' in form.cleaned_data:
            email = form.cleaned_data['email']
        User.objects.create_user(form.cleaned_data['username'], email, form.cleaned_data['password'],
                                 first_name=form.cleaned_data['first_name'],
                                 last_name=form.cleaned_data['last_name'])


class LogoutView(View):
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect("/")


class ProfileView(TemplateView):
    template_name = "registration/profile.html"

    def dispatch(self, request, *args, **kwargs):
        if not Profile.objects.filter(user=request.user).exists():
            return redirect(reverse("edit_profile"))
        context = {
            'selected_user': request.user
        }
        return render(request, self.template_name, context)


class EditProfileView(TemplateView):
    template_name = "registration/edit_profile.html"

    def dispatch(self, request, *args, **kwargs):
        form = ProfileForm(instance=self.get_profile(request.user))
        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES, instance=self.get_profile(request.user))
            if form.is_valid():
                form.instance.user = request.user
                form.save()
                messages.success(request, u"Профиль успешно обновлен!")
                return redirect(reverse("profile"))
        return render(request, self.template_name, {'form': form})

    def get_profile(self, user):
        try:
            return user.profile
        except:
            return None


class DialogsView(View):
    def get(self, request):
        chats = Chat.objects.filter(members__in=[request.user.id])
        return render(request, 'dialogs.html', {'user_profile': request.user, 'chats': chats})


class MessagesView(View):
    def get(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
            if request.user in chat.members.all():
                chat.message_set.filter(is_readed=False).exclude(author=request.user).update(is_readed=True)
            else:
                chat = None
        except Chat.DoesNotExist:
            chat = None

        return render(
            request,
            'messages.html',
            {
                'user_profile': request.user,
                'chat': chat,
                'form': MessageForm()
            }
        )

    def post(self, request, chat_id):
        form = MessageForm(data=request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat_id = chat_id
            message.author = request.user
            message.save()
        return redirect(reverse('users:messages', kwargs={'chat_id': chat_id}))


class CreateDialogView(View):
    def get(self, request, user_id):
        user = get_object_or_404(Profile, id=user_id)
        chats = Chat.objects.filter(
            members__in=[request.user.profile, user_id],
            type=Chat.DIALOG).annotate(c=Count('members')).filter(c=2)
        if user.likes.filter(id=request.user.id).exists() \
                and request.user.profile.likes.filter(id=user_id).exists() \
                and chats.count() == 0:
            chat = Chat.objects.create()
            chat.members.add(request.user.profile)
            chat.members.add(user_id)
        else:
            chat = Chat.objects.create()
            chat.members.add(request.user.profile)
            chat.members.add(user_id)
        if not user.likes.filter(id=request.user.id).exists() \
                and request.user.profile.likes.filter(id=user_id).exists():
            messages.error(
                request,
                u"Impossible to start chat. This user hasn't liked you yet.")
            return redirect('user_detail', pk=user.pk)
        return redirect(reverse('messages', kwargs={'chat_id': chat.id}))
