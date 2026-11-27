from django.utils import timezone
from .max_notify import send_max_lead
from .models import Lead, Ticket, Partner, Review, Post
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Lead, Ticket, Partner, Review
from .forms import TicketForm

def index(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'review':
            name = request.POST.get('name', '').strip()
            text = request.POST.get('text', '').strip()
            try:
                rating = min(5, max(1, int(request.POST.get('rating', 5))))
            except ValueError:
                rating = 5
            if name and text:
                Review.objects.create(name=name, text=text, rating=rating, is_published=False)
                return redirect('/?review_sent=1#reviews')
        else:
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            if name and phone:
                Lead.objects.create(name=name, phone=phone); send_max_lead(name, phone)
                return redirect('/?success=1')

    reviews = Review.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'web/index.html', {'reviews': reviews})

def register_user(request, role='client'):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')

        if not username or not phone or not password:
            error = 'Заполните все поля.'
        elif role != 'partner' and request.POST.get('agree_pdn') != 'on':
            error = 'Необходимо дать согласие на обработку персональных данных (152-ФЗ).'
        elif role == 'partner' and request.POST.get('agree_offer') != 'on':
            error = 'Необходимо принять условия партнёрской оферты.'
        elif User.objects.filter(username=username).exists():
            error = 'Этот логин уже занят.'
        else:
            user = User.objects.create_user(username=username, password=password)
            if role == 'partner':
                Partner.objects.create(user=user, phone=phone, is_active=True, offer_accepted_at=timezone.now())
                login(request, user)
                return redirect('partner_cabinet')
            else:
                user.first_name = phone
                user.save()
                login(request, user)
                return redirect('cabinet')

    return render(request, 'web/register.html', {'role': role, 'error': error})

@login_required
def cabinet(request):
    if hasattr(request.user, 'partner'):
        return redirect('partner_cabinet')
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.client_name = request.user.username
            ticket.phone = request.user.first_name
            ticket.save()
            return redirect('cabinet')
    else:
        form = TicketForm()

    tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'web/cabinet.html', {'tickets': tickets, 'form': form})

@login_required
def partner_cabinet(request):
    try:
        partner = request.user.partner
    except Partner.DoesNotExist:
        return redirect('cabinet')

    tickets = Ticket.objects.filter(partner=partner).order_by('-created_at')
    return render(request, 'web/partner_cabinet.html', {'tickets': tickets})

@login_required
def take_ticket(request, ticket_id):
    if request.method == 'POST':
        try:
            partner = request.user.partner
        except Partner.DoesNotExist:
            return redirect('cabinet')

        ticket = get_object_or_404(Ticket, id=ticket_id, partner=partner, status='new')
        ticket.status = 'in_progress'
        ticket.save()

    return redirect('partner_cabinet')

@login_required
def drop_ticket(request, ticket_id):
    if request.method == 'POST':
        try:
            partner = request.user.partner
        except Partner.DoesNotExist:
            return redirect('cabinet')

        ticket = get_object_or_404(Ticket, id=ticket_id, partner=partner)
        if ticket.status in ['new', 'in_progress']:
            ticket.partner = None
            ticket.status = 'new'
            ticket.save()

    return redirect('partner_cabinet')

@login_required
def complete_ticket(request, ticket_id):
    if request.method == 'POST':
        try:
            partner = request.user.partner
        except Partner.DoesNotExist:
            return redirect('cabinet')

        ticket = get_object_or_404(Ticket, id=ticket_id, partner=partner, status='in_progress')
        result_text = request.POST.get('result', '').strip()
        time_spent = request.POST.get('time_spent', 0)

        if result_text:
            ticket.result = result_text
            try:
                ticket.time_spent = ticket.time_spent + max(0, int(time_spent))
            except ValueError:
                pass
            ticket.revision_comment = ''
            ticket.status = 'on_review'
            ticket.save()

    return redirect('partner_cabinet')

def manage_tickets(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin/login/?next=/manage/')

    review_tickets = Ticket.objects.filter(status='on_review').order_by('-created_at')
    all_tickets = Ticket.objects.all().order_by('-created_at')
    partners = Partner.objects.filter(is_active=True)
    return render(request, 'web/manage_tickets.html', {
        'review_tickets': review_tickets,
        'tickets': all_tickets,
        'partners': partners,
    })

def update_ticket_admin(request, ticket_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin/login/?next=/manage/')

    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        partner_id = request.POST.get('partner_id')
        status = request.POST.get('status')

        old_partner_id = ticket.partner_id
        ticket.partner = get_object_or_404(Partner, id=partner_id) if partner_id else None

        if ticket.partner and ticket.partner_id != old_partner_id and status == 'new':
            ticket.status = 'in_progress'
        elif status in dict(Ticket.STATUS_CHOICES):
            ticket.status = status

        ticket.save()

    return redirect('manage_tickets')

def review_ticket_admin(request, ticket_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin/login/?next=/manage/')

    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id, status='on_review')
        action = request.POST.get('action')

        if action == 'close':
            ticket.status = 'closed'
            ticket.revision_comment = ''
            ticket.save()
        elif action == 'rework':
            comment = request.POST.get('revision_comment', '').strip()
            ticket.revision_comment = comment or 'Требуется доработка.'
            ticket.status = 'in_progress'
            ticket.save()

    return redirect('manage_tickets')
def blog_list(request):
    posts = Post.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'web/blog.html', {'posts': posts})

def blog_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_published=True)
    return render(request, 'web/blog_detail.html', {'post': post})



def privacy_policy(request):
    return render(request, 'web/privacy.html')


def public_offer(request):
    return render(request, 'web/offer.html')
