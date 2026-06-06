from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseNotFound, HttpResponseGone
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import ShortURL, ClickAnalytics
from .forms import ShortURLForm, ShortURLEditForm
import qrcode
import qrcode.image.svg
import io, base64, os
from django.conf import settings


def home(request):
    return render(request, 'shortener/home.html')


def redirect_url(request, short_code):
    try:
        url_obj = ShortURL.objects.get(short_code=short_code)
    except ShortURL.DoesNotExist:
        return HttpResponseNotFound(render(request, 'shortener/404.html'))

    if not url_obj.is_active:
        return render(request, 'shortener/expired.html', {'reason': 'disabled'}, status=410)

    if url_obj.is_expired():
        return render(request, 'shortener/expired.html', {'reason': 'expired'}, status=410)

    # Track analytics
    ClickAnalytics.objects.create(
        short_url=url_obj,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        referrer=request.META.get('HTTP_REFERER', '')[:500],
    )
    url_obj.click_count += 1
    url_obj.save(update_fields=['click_count'])

    return redirect(url_obj.original_url)


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


@login_required
def dashboard(request):
    urls = ShortURL.objects.filter(user=request.user)
    total_clicks = sum(u.click_count for u in urls)
    active_count = urls.filter(is_active=True).count()
    expired_count = sum(1 for u in urls if u.is_expired())

    context = {
        'urls': urls,
        'total_urls': urls.count(),
        'total_clicks': total_clicks,
        'active_count': active_count,
        'expired_count': expired_count,
    }
    return render(request, 'shortener/dashboard.html', context)


@login_required
def create_url(request):
    if request.method == 'POST':
        form = ShortURLForm(request.POST)
        if form.is_valid():
            url_obj = form.save(commit=False)
            url_obj.user = request.user
            form.save()
            messages.success(request, f'Short URL created: {request.build_absolute_uri("/" + url_obj.short_code + "/")}')
            return redirect('dashboard')
    else:
        form = ShortURLForm()
    return render(request, 'shortener/create.html', {'form': form})


@login_required
def edit_url(request, pk):
    url_obj = get_object_or_404(ShortURL, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ShortURLEditForm(request.POST, instance=url_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'URL updated successfully!')
            return redirect('dashboard')
    else:
        form = ShortURLEditForm(instance=url_obj)
    return render(request, 'shortener/edit.html', {'form': form, 'url_obj': url_obj})


@login_required
def delete_url(request, pk):
    url_obj = get_object_or_404(ShortURL, pk=pk, user=request.user)
    if request.method == 'POST':
        url_obj.delete()
        messages.success(request, 'Short URL deleted.')
        return redirect('dashboard')
    return render(request, 'shortener/confirm_delete.html', {'url_obj': url_obj})


@login_required
def url_analytics(request, pk):
    url_obj = get_object_or_404(ShortURL, pk=pk, user=request.user)
    recent_clicks = url_obj.clicks.all()[:50]

    # Clicks per day (last 7 days)
    clicks_by_day = (
        url_obj.clicks
        .annotate(date=TruncDate('clicked_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    context = {
        'url_obj': url_obj,
        'recent_clicks': recent_clicks,
        'clicks_by_day': list(clicks_by_day),
        'short_url': request.build_absolute_uri(f'/{url_obj.short_code}/'),
    }
    return render(request, 'shortener/analytics.html', context)


@login_required
def generate_qr(request, pk):
    url_obj = get_object_or_404(ShortURL, pk=pk, user=request.user)
    short_url = request.build_absolute_uri(f'/{url_obj.short_code}/')

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(short_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'shortener/qr_code.html', {
        'url_obj': url_obj,
        'qr_b64': qr_b64,
        'short_url': short_url,
    })
