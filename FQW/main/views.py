from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login
from itertools import chain
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .forms import *
from .models import *
from django.db.models import Min
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.utils.timezone import now, timedelta
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory

import os


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль художника после регистрации
            profile = Profile.objects.create(
                user=user,
                # specialization=form.cleaned_data.get('specialization'),
                # description=form.cleaned_data.get('description')
            )
            # # Добавляем навыки (если нужно)
            # skills = form.cleaned_data.get('skills', [])
            # for skill_name in skills:
            #     skill, _ = Skills.objects.get_or_create(name=skill_name)
            #     profile.skills.add(skill)
            login(request, user)
            print("Формы валидны")
            return redirect('home')  # Перенаправляем на главную страницу
    else:
        form = RegisterForm()
        print("Ошибки в форме:", form.errors)
    return render(request, 'register.html', {'form': form})


@login_required
def create_commission(request):
    if request.method == 'POST':
        commission_form = CommissionForm(request.POST, request.FILES)
        option_forms = [OptionForm(request.POST, prefix=f"option-{i}") for i in range(3)]
        bonus_option_formset = modelformset_factory(
            BonusOption, form=BonusOptionForm, extra=0, can_delete=True
        )(request.POST, prefix="bonus", queryset=BonusOption.objects.none())
        portfolio_forms = [PortfolioForm(request.POST, request.FILES, prefix=f"portfolio-{i}") for i in range(5)]

        is_three_packages = request.POST.get('package-switch') == 'on'

        # Валидация форм
        are_forms_valid = (
            commission_form.is_valid() and
            all(form.is_valid() for i, form in enumerate(option_forms) if
                is_three_packages or i == 1) and  # Проверяем только стандартный пакет, если свитч выключен
            bonus_option_formset.is_valid() and
            all(pf.is_valid() for pf in portfolio_forms if pf['image'].value())
        )

        if are_forms_valid:
            # Сохранение комишкии
            commission = commission_form.save(commit=False)
            commission.user = request.user
            commission.save()

            # Сохранение опций
            if is_three_packages:
                # Сохраняем все три пакета
                for pkg, form in zip(['BASIC', 'STANDARD', 'PREMIUM'], option_forms):
                    option = form.save(commit=False)
                    option.commission = commission
                    option.package_type = pkg
                    option.save()
            else:
                # Сохраняем только стандартный пакет
                standard_form = option_forms[1]  # Второй элемент соответствует "STANDARD"
                option = standard_form.save(commit=False)
                option.commission = commission
                option.package_type = 'STANDARD'
                option.save()

            # Сохранение бонусных опций
            for form in bonus_option_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    bonus = form.save(commit=False)
                    bonus.commission = commission
                    bonus.save()

            # Сохранение портфолио
            for i, form in enumerate(portfolio_forms):
                if form.is_valid() and form.cleaned_data.get('image'):
                    portfolio = form.save(commit=False)
                    portfolio.user = request.user
                    portfolio.commission = commission
                    portfolio.description = form.cleaned_data.get(
                        'description') or f"Коммишка «{commission.title}» - работа {i + 1}"
                    portfolio.save()

            return redirect('commission_detail', commission.id)

    else:
        commission_form = CommissionForm()
        option_forms = [
            OptionForm(prefix=f"option-{i}", initial={'package_type': pkg})
            for i, pkg in enumerate(['BASIC', 'STANDARD', 'PREMIUM'])
        ]
        bonus_option_formset = modelformset_factory(
            BonusOption, form=BonusOptionForm, extra=1, can_delete=True
        )(queryset=BonusOption.objects.none(), prefix="bonus")
        portfolio_forms = [PortfolioForm(prefix=f"portfolio-{i}") for i in range(5)]

    return render(request, 'create_commission.html', {
        'commission_form': commission_form,
        'option_forms': option_forms,
        'bonus_option_formset': bonus_option_formset,
        'portfolio_forms': portfolio_forms,
    })




@login_required
def commission_detail(request, pk):
    commission = get_object_or_404(Commission, id=pk)

    # Получаем пакеты
    basic_option = None
    standard_option = None
    premium_option = None

    try:
        basic_option = commission.options.get(package_type='BASIC')
    except Option.DoesNotExist:
        pass

    try:
        standard_option = commission.options.get(package_type='STANDARD')
    except Option.DoesNotExist:
        pass

    try:
        premium_option = commission.options.get(package_type='PREMIUM')
    except Option.DoesNotExist:
        pass

    # Получаем первые 5 изображений из портфолио
    portfolios = commission.portfolio_works.all()[:5]

    context = {
        'commission': commission,
        'basic_option': basic_option,
        'standard_option': standard_option,
        'premium_option': premium_option,
        'portfolios': portfolios,
    }
    return render(request, 'commission_detail.html', context)

# @login_required
# def upload_portfolio_image(request):
#     if request.method == 'POST' and request.FILES.get('file'):
#         portfolio = Portfolio(user=request.user)
#         portfolio.image = request.FILES['file']
#         portfolio.save()
#         return JsonResponse({
#             'success': True,
#             'image_url': portfolio.image.url,
#             'id': portfolio.id,
#         })
#     return JsonResponse({'success': False})

def commission_success(request):
    return render(request, 'commission_success.html')

def home(request):
    commissions = Commission.objects.all()
    return render(request, 'home.html', {'commissions': commissions})

# @login_required
# def commission_detail(request, pk):
#     commission = get_object_or_404(Commission, pk=pk)
#     artist = commission.user
#
#     # Получаем все пакеты
#     basic_option = commission.options.get(package_type='BASIC')
#     standard_option = commission.options.get(package_type='STANDARD')
#     premium_option = commission.options.get(package_type='PREMIUM')
#
#     return render(request, 'commission_detail.html', {
#         'commission': commission,
#         'artist': artist,
#         'basic_option': basic_option,
#         'standard_option': standard_option,
#         'premium_option': premium_option,
#     })

@login_required
def order_form(request, pk):
    commission = get_object_or_404(Commission, pk=pk)
    artist = commission.user

    # Получаем выбранный пакет из GET-параметра
    package_type = request.GET.get('package', 'BASIC')  # По умолчанию "Базовый"
    selected_option = None

    try:
        selected_option = commission.options.get(package_type=package_type.upper())
    except Option.DoesNotExist:
        # Если пакет не найден, используем первый доступный пакет
        available_options = commission.options.all()
        if available_options.exists():
            selected_option = available_options.first()
        else:
            return HttpResponse("Для этой комиссии нет доступных пакетов.", status=404)

    # Дополнительные опции
    additional_options = BonusOption.objects.filter(commission=commission)

    # Суммарная стоимость и срок выполнения
    total_price = selected_option.price
    total_deadline = selected_option.deadline

    if request.method == 'POST':
        form = UserResponseForm(request.POST, request.FILES)
        if form.is_valid():
            user_response = form.save(commit=False)
            user_response.artist = artist
            user_response.customer = request.user
            user_response.commission = commission
            user_response.price = total_price
            user_response.delivery_time = now() + timedelta(days=total_deadline)
            user_response.description = selected_option.description

            # Сохраняем данные о пакете
            user_response.package_type = selected_option.package_type
            user_response.package_description = selected_option.description
            user_response.package_price = selected_option.price
            user_response.package_deadline = selected_option.deadline

            user_response.save()

            # Обработка выбранных дополнительных опций
            selected_bonus_ids = request.POST.getlist('additional_options')
            for bonus_id in selected_bonus_ids:
                try:
                    bonus_option = BonusOption.objects.get(id=bonus_id)
                    user_response.selected_bonus_options.add(bonus_option)
                    total_price += bonus_option.price
                    total_deadline += bonus_option.deadline
                except BonusOption.DoesNotExist:
                    pass

            # Обновляем общую стоимость и срок выполнения
            user_response.price = total_price
            user_response.delivery_time = now() + timedelta(days=total_deadline)
            user_response.save()

            # Обработка файлов
            if 'files' in request.FILES:
                for file in request.FILES.getlist('files'):
                    stored_file = File.objects.create(user=request.user, file=file)
                    user_response.files.add(stored_file)

            return redirect('commission_success')
    else:
        form = UserResponseForm()

    return render(request, 'order_form.html', {
        'form': form,
        'commission': commission,
        'artist': artist,
        'selected_option': selected_option,
        'additional_options': additional_options,
        'total_price': total_price,
        'total_deadline': total_deadline,
    })

@login_required
def profile(request):
    # Получаем профиль текущего пользователя
    user_profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'profile.html', {'profile': user_profile})


@login_required
def create_bid(request):
    if request.method == 'POST':
        form = BirzhaForm(request.POST, request.FILES)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.user = request.user
            bid.save()
            return redirect('home')  # Перенаправление после успешного сохранения
    else:
        form = BirzhaForm()

    return render(request, 'create_bid.html', {'form': form})

def commissions_catalog(request):
    print("GET parameters:", request.GET)  # Печатаем параметры запроса

    # Получаем все коммишки с аннотацией минимальной цены
    commissions = Commission.objects.filter(options__isnull=False).annotate(
        min_price=Min('options__price')
    )
    print("Initial commissions count:", commissions.count())
    print("Annotated commissions:", [(c.title, c.min_price) for c in commissions])

    # Фильтрация по типу
    type_filter = request.GET.get('type')
    if type_filter:
        commissions = commissions.filter(type_id=type_filter)
        print(f"Filtered by type ({type_filter}): {commissions.count()}")

    # Фильтрация по минимальной цене
    price_filter = request.GET.get('price')
    if price_filter:
        try:
            price_filter = float(price_filter)
            commissions = commissions.filter(min_price__gte=price_filter)
            print(f"Filtered by price (>= {price_filter}): {commissions.count()}")
        except ValueError:
            pass

    # Фильтрация по сроку выполнения
    deadline_filter = request.GET.get('deadline')
    if deadline_filter:
        try:
            deadline_filter = int(deadline_filter)
            commissions = commissions.filter(options__deadline__lte=deadline_filter)
            print(f"Filtered by deadline (<= {deadline_filter}): {commissions.count()}")
        except ValueError:
            pass

    # Сортировка
    sort_by = request.GET.get('sort', 'popularity')
    if sort_by == 'price_asc':
        commissions = commissions.order_by('min_price')
    elif sort_by == 'price_desc':
        commissions = commissions.order_by('-min_price')
    elif sort_by == 'deadline_asc':
        commissions = commissions.order_by('options__deadline')
    elif sort_by == 'deadline_desc':
        commissions = commissions.order_by('-options__deadline')

    # Пагинация
    paginator = Paginator(commissions, 9)  # 9 коммишек на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Получаем список всех типов для фильтрации
    types = Type.objects.all()

    return render(request, 'commissions_catalog.html', {
        'commissions': page_obj,
        'types': types,
    })

def bazaar_catalog(request):
    # Получаем все заказы из модели Birzha
    bids = Birzha.objects.all()

    # Фильтрация по типу
    type_filter = request.GET.get('type')
    if type_filter:
        bids = bids.filter(type_id=type_filter)

    # Фильтрация по максимальной цене
    price_filter = request.GET.get('price')
    if price_filter:
        try:
            price_filter = float(price_filter)
            bids = bids.filter(price__lte=price_filter)  # Меньше или равно указанной цене
        except ValueError:
            pass

    # Сортировка
    sort_by = request.GET.get('sort', 'created_at_desc')
    if sort_by == 'price_asc':
        bids = bids.order_by('price')
    elif sort_by == 'price_desc':
        bids = bids.order_by('-price')


    # Пагинация
    paginator = Paginator(bids, 9)  # 9 заказов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Получаем список всех типов для фильтрации
    types = Type.objects.all()

    return render(request, 'bazaar_catalog.html', {
        'bids': page_obj,
        'types': types,
    })

@login_required
def offer_service(request, bid_id):
    bid = get_object_or_404(Birzha, id=bid_id)  # Получаем объект Birzha

    if request.method == 'POST':
        form = UserResponseForm(request.POST)
        if form.is_valid():
            user_response = form.save(commit=False)
            user_response.artist = request.user  # Художник, который откликается
            user_response.customer = bid.user  # Заказчик, создавший биржу
            user_response.birzha = bid  # Связываем отклик с биржей
            user_response.save()

            return redirect('bazaar_catalog')  # Перенаправление после успешного сохранения
    else:
        form = UserResponseForm()

    return render(request, 'offer_service.html', {
        'bid': bid,
        'form': form,
    })

@login_required
def toggle_favorite_commission(request, commission_id):
    if request.method == 'POST':
        commission = get_object_or_404(Commission, id=commission_id)

        favorite, created = FavoriteCommission.objects.get_or_create(user=request.user, commission=commission)

        if not created:
            # Если уже есть в избранном, удаляем
            favorite.delete()
            is_favorite = False
        else:
            # Если нет в избранном, добавляем
            is_favorite = True

        return JsonResponse({'success': True, 'is_favorite': is_favorite})
    return JsonResponse({'success': False, 'message': 'Неверный запрос.'})

@login_required
def add_portfolio(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            return redirect('profile',username=request.user.username)  # Перенаправление на страницу профиля
    else:
        form = PortfolioForm()
    return render(request, 'add_portfolio.html', {'form': form})

@login_required
def profile_detail(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile

    context = {
        'profile': profile,
        'commissions': profile.user.commission_set.all(),
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)  # Перенаправляем на страницу профиля
    else:
        form = ProfileForm(instance=profile)

    # Если форма не валидна или это GET-запрос
    context = {
        'profile': profile,
        'form': form
    }
    return render(request, 'profile.html', context)  # Всегда рендерим profile.html

@login_required
def my_orders(request):
    birzha_responses_as_artist = UserResponse.objects.filter(artist=request.user, birzha__isnull=False)
    birzha_responses_as_customer = UserResponse.objects.filter(customer=request.user, birzha__isnull=False)
    commission_responses_as_artist = UserResponse.objects.filter(artist=request.user, commission__isnull=False)
    commission_responses_as_customer = UserResponse.objects.filter(customer=request.user, commission__isnull=False)

    return render(request, 'my_orders.html', {
        'birzha_responses_as_artist': birzha_responses_as_artist,
        'birzha_responses_as_customer': birzha_responses_as_customer,
        'commission_responses_as_artist': commission_responses_as_artist,
        'commission_responses_as_customer': commission_responses_as_customer,
    })


@login_required
def order_detail_view(request, pk):
    # Получаем объект UserResponse по его ID
    response = get_object_or_404(UserResponse, pk=pk)

    # Проверяем, существует ли связанный заказ
    order = Orders.objects.filter(response=response).first()
    messages = Message.objects.filter(chat__order=order).order_by('created_at') if order else Message.objects.none()
    revisions = RevisionRequest.objects.filter(order=order).order_by('created_at') if order else RevisionRequest.objects.none()
    dispute = order.disputechat_set.filter(status='pending').first()
    delivers = order.delivers.all() if order else []

    # Объединяем сообщения и правки в один временной ряд
    timeline = sorted(
        chain(
            messages.annotate(type=models.Value('message', output_field=models.CharField())),
            revisions.annotate(type=models.Value('revision', output_field=models.CharField()))
        ),
        key=lambda x: x.created_at
    )

    # Получаем выбранный пакет из UserResponse
    selected_option = None
    additional_options = []
    if response.commission:
        try:
            # Получаем выбранный пакет через package_type
            selected_option = response.commission.options.get(package_type=response.package_type)
        except Option.DoesNotExist:
            pass

    # Дополнительные опции (если есть)
    if response.commission:
        additional_options = BonusOption.objects.filter(commission=response.commission)

    # Обработка POST-запросов
    if request.method == 'POST':
        if 'accept_order' in request.POST and not order:
            # Проверяем тип отклика и наличие соответствующего объекта
            is_commission_owner = response.commission and request.user == response.commission.user
            is_birzha_owner = response.birzha and request.user == response.birzha.user

            if is_commission_owner or is_birzha_owner:
                order, created = Orders.objects.get_or_create(
                    response=response,
                    defaults={
                        'artist': response.artist,
                        'customer': response.customer,
                        'price': response.price,
                        'description': response.description,
                        'deadline': timezone.now().date() + timezone.timedelta(days=response.delivery_time),
                        'status': 'discussion'
                    }
                )
                    # Проверка успешного создания
                    # if not created:
                    #     order.status = 'discussion'
                    #     order.save()
                return redirect('order_detail', pk=response.pk)
        # Для заказчика: принятие заказа
        elif 'accept_order_customer' in request.POST:
            if order and request.user == order.customer and order.status == 'on_review':
                order.status = 'accepted'
                order.save()
                return redirect('leave_review', pk=order.id)
        elif 'reject_order' in request.POST and not order:
            response.delete()
            return redirect('my_orders')

    return render(request, 'order_detail.html', {
        'response': response,
        'order': order,
        'dispute': dispute,
        'messages': messages,
        'selected_option': selected_option,
        'additional_options': additional_options,
        'delivers': delivers,
    })

@login_required
def send_message(request, order_id):
    order = get_object_or_404(Orders, id=order_id)

    if request.user not in [order.customer, order.artist]:
        return redirect('order_detail', pk=order.response.id)

    chat, created = Chat.objects.get_or_create(order=order)
    if created:
        chat.participants.set([order.customer, order.artist])

    if request.method == 'POST':
        text = request.POST.get('content', '').strip()
        if text:
            Message.objects.create(
                chat=chat,
                sender=request.user,
                text=text
            )
    return redirect('order_detail', pk=order.response.id)

login_required
def order_actions(request, pk):
    order = get_object_or_404(Orders, pk=pk)
    if request.user not in [order.artist, order.customer]:
        return HttpResponseForbidden()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'start_work' and order.status == 'discussion':
            order.status = 'in_work'
            order.save()
        elif action == 'submit_review' and order.status == 'in_work':
            return redirect('submit_delivery', pk=pk)



@login_required
def submit_delivery(request, pk):
    order = get_object_or_404(Orders, pk=pk, artist=request.user)
    chat, created = Chat.objects.get_or_create(order=order)

    if request.method == 'POST':
        images = request.FILES.getlist('images')  # Получаем список изображений
        files = request.FILES.getlist('files')   # Получаем список файлов
        comment = request.POST.get('comment')

        # Создаем запись в Delivers
        deliver = Delivers.objects.create(
            order=order,
            artist=request.user,
            comment=comment
        )

        # Добавляем изображения
        for image_file in images:
            image = ImageStorage.objects.create(image=image_file)
            deliver.images.add(image)

        # Добавляем файлы
        for file in files:
            stored_file = File.objects.create(
                user=request.user,
                file=file,
                file_type='document' if file.name.endswith(('.psd', '.ai', '.zip')) else 'other'
            )
            deliver.files.add(stored_file)

        # Обновляем статус заказа
        order.status = 'on_review'
        order.save()

        return redirect('order_detail', pk=order.response.id)

    return render(request, 'submit_delivery.html', {'order': order})

@login_required
def leave_review(request, pk):
    order = get_object_or_404(Orders, pk=pk, customer=request.user, status='accepted')
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.customer = request.user
            review.image = order.delivers.last().images.first().image
            review.save()
            order.status = 'accepted'
            order.save()
            # Обновление рейтинга художника
            artist_profile = order.artist.profile
            average_rating = (review.communication_rating + review.result_rating + review.recommend_rating) / 3
            artist_profile.ratings = (artist_profile.ratings + average_rating) / 2
            artist_profile.save()
            return redirect('profile_detail', username=order.artist.username)
    else:
        form = ReviewForm()
    return render(request, 'leave_review.html', {'form': form})

@login_required
def dispute_chat(request, pk):
    dispute = get_object_or_404(DisputeChat, pk=pk)
    if request.method == 'POST':
        message = request.POST.get('message')
        DisputeMessage.objects.create(
            dispute_chat=dispute,
            sender=request.user,
            text=message
        )
    messages = DisputeMessage.objects.filter(dispute_chat=dispute)
    return render(request, 'dispute_chat.html', {'messages': messages, 'dispute': dispute})


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Orders, pk=pk, customer=request.user)

    if not order.can_cancel():
        messages.error(request, "Вы уже отправили максимальное количество заявок на отмену.")
        return redirect('order_detail', pk=order.response.id)

    if request.method == 'POST':
        form = CancelOrderForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            other_reason = form.cleaned_data.get('other_reason', '')

            # Создание заявки на отмену
            OrderCancellation.objects.create(
                order=order,
                cancelled_by=request.user,
                reason=reason,
                other_reason=other_reason
            )

            # Уведомление модератора
            moderator = User.objects.filter(is_staff=True).first()
            if moderator:
                Notification.objects.create(
                    user=moderator,
                    message=f"Новая заявка на отмену заказа #{order.id}"
                )

            return redirect('order_detail', pk=order.response.id)
    else:
        form = CancelOrderForm()

    return render(request, 'cancel_order.html', {'form': form, 'order': order})

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications_list.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.notifications.all()

def some_view(request):
    # Пример создания уведомления
    Notification.objects.create(
        user=request.user,
        message="Ваш заказ был обновлен"
    )


@login_required
def request_revisions(request, pk):
    order = get_object_or_404(Orders, pk=pk, customer=request.user, status='on_review')

    if request.method == 'POST':
        comment = request.POST.get('comment')
        # Создаем запрос на правки
        RevisionRequest.objects.create(
            order=order,
            customer=request.user,
            comment=comment
        )

        # Обновляем статус заказа
        order.status = 'in_work'
        order.save()

        # Уведомляем художника
        Notification.objects.create(
            user=order.artist,
            message=f"Заказчик запросил правки к заказу #{order.id}"
        )

        return redirect('order_detail', pk=pk)

    return redirect('order_detail', pk=pk)


@login_required
def start_work(request, pk):
    response = get_object_or_404(UserResponse, pk=pk, artist=request.user)
    # Используйте get_or_create
    order, created = Orders.objects.get_or_create(
        response=response,
        defaults={
            'artist': request.user,
            'customer': response.customer,
            'price': response.price,
            'deadline': timezone.now().date() + timezone.timedelta(days=response.delivery_time),
            'status': 'discussion'
        }
    )
    if not created:
        # Если заказ уже существует, обновите статус
        order.status = 'in_work'
        order.save()
    return redirect('order_detail', pk=response.pk)

@login_required
def edit_response(request, pk):
    response = get_object_or_404(UserResponse, pk=pk, artist=request.user)
    if request.method == 'POST':
        form = UserResponseForm(request.POST, instance=response)
        if form.is_valid():
            form.save()
            return redirect('order_detail', pk=pk)
    else:
        form = UserResponseForm(instance=response)
    return render(request, 'edit_response.html', {'form': form})

@login_required
def edit_order(request, pk):
    response = get_object_or_404(UserResponse, pk=pk, artist=request.user)
    if request.method == 'POST':
        form = UserResponseForm(request.POST, instance=response)
        if form.is_valid():
            form.save()
            return redirect('order_detail', pk=pk)
    else:
        form = UserResponseForm(instance=response)
    return render(request, 'edit_order.html', {'form': form})


@login_required
def handle_revision(request, pk, action):
    revision = get_object_or_404(RevisionRequest, pk=pk)
    order = revision.order

    if request.user != order.artist:
        return HttpResponseForbidden("Вы не можете выполнять это действие")

    if action == 'accept':
        order.status = 'in_work'
        order.save()
        Notification.objects.create(
            user=order.customer,
            message=f"Художник принял правки к заказу #{order.id}"
        )
        return redirect('order_detail', pk=revision.order.response.id)

    elif action == 'dispute':
        # Проверяем, есть ли уже активный спор
        if not order.disputechat_set.filter(status='pending').exists():
            moderator = User.objects.filter(is_superuser=True).first()
            if not moderator:
                messages.error(request, "Нет доступного модератора.")
                return redirect('order_detail', pk=order.response.id)

            # Создание спора
            dispute = DisputeChat.objects.create(
                order=order,
                moderator=moderator,
                reason=f"Спор по правкам к заказу #{order.id}",
                status='pending'
            )
            dispute.participants.set([order.artist, order.customer])

        # Обновление статуса заказа
        order.status = 'discussion'
        order.save()

        return redirect('dispute_chat', pk=dispute.id)


@login_required
def resolve_dispute(request, pk, decision):
    dispute = get_object_or_404(DisputeChat, pk=pk)

    # Проверка, что пользователь — модератор
    if request.user != dispute.moderator:
        return HttpResponseForbidden("Вы не модератор этого спора")

    # Установите решение и статус
    if decision in ['accept', 'reject']:
        dispute.decision = decision
        dispute.status = 'resolved'
        dispute.save()

        # Уведомления участникам
        Notification.objects.create(
            user=dispute.order.artist,
            message=f"Модератор решил спор по заказу #{dispute.order.id}: {decision}"
        )
        Notification.objects.create(
            user=dispute.order.customer,
            message=f"Модератор решил спор по заказу #{dispute.order.id}: {decision}"
        )

    return redirect('dispute_chat', pk=pk)