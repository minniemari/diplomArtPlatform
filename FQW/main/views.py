from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login
from .forms import *
from .models import *
from django.db.models import Min
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.timezone import now, timedelta
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
import os

# def upload_image(request):
#     if request.method == 'POST' and request.FILES.get('file'):
#         file = request.FILES['file']
#         file_path = default_storage.save(f'portfolio/{file.name}', file)
#         return JsonResponse({'success': True, 'file_url': default_storage.url(file_path)})
#     return JsonResponse({'success': False})
#
# @login_required
# def upload_portfolio_image(request):
#     if request.method == 'POST' and request.FILES.get('file'):
#         portfolio = Portfolio(user=request.user)
#         portfolio.image = request.FILES['file']
#         portfolio.save()
#         return JsonResponse({
#             'success': True,
#             'image_url': portfolio.image.url,
#             'id': portfolio.id
#         })
#     return JsonResponse({'success': False})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль художника после регистрации
            profile = Profile.objects.create(
                user=user,
                specialization=form.cleaned_data.get('specialization'),
                description=form.cleaned_data.get('description')
            )
            # Добавляем навыки (если нужно)
            skills = form.cleaned_data.get('skills', [])
            for skill_name in skills:
                skill, _ = Skills.objects.get_or_create(name=skill_name)
                profile.skills.add(skill)
            login(request, user)
            print("Формы валидны")
            # return redirect('home')  # Перенаправляем на главную страницу
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
            # Если вообще нет пакетов, возвращаем ошибку
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
            user_response.delivery_time = now() + timedelta(days=total_deadline)  # Дата завершения
            user_response.description = selected_option.description  # Заполняем описание из пакета
            user_response.save()
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
def send_message(request, pk):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        content = request.POST.get('content')

        if not content.strip():
            return JsonResponse({'success': False, 'message': 'Текст сообщения не может быть пустым.'})

        recipient = get_object_or_404(User, id=recipient_id)
        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content,
        )

        return JsonResponse({'success': True, 'message': 'Сообщение успешно отправлено.'})
    return JsonResponse({'success': False, 'message': 'Неверный запрос.'})

@login_required
def artist_order_detail(request, pk):
    order = Orders.objects.get(pk=pk)
    messages = Message.objects.filter(chat__order=order).order_by('created_at')
    return render(request, 'artist_order_detail.html', {'order': order, 'messages': messages})

@login_required
def customer_order_detail(request, pk):
    order = Orders.objects.get(pk=pk)
    messages = Message.objects.filter(chat__order=order).order_by('created_at')
    return render(request, 'customer_order_detail.html', {'order': order, 'messages': messages})

@login_required
def my_orders(request):
    orders = Orders.objects.filter(artist=request.user)
    return render(request, 'my_orders.html', {'orders': orders})

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
    bid = Birzha.objects.get(id=bid_id)

    if request.method == 'POST':
        form = UserResponseForm(request.POST)
        if form.is_valid():
            user_response = form.save(commit=False)
            user_response.artist = request.user
            user_response.customer = bid.user
            user_response.birzha = bid
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
            return redirect('profile')  # Перенаправление на страницу профиля
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
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})