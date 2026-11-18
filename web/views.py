from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Lead, Ticket, Partner
from .forms import TicketForm

def index(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        if name and phone:
            Lead.objects.create(name=name, phone=phone)
            return redirect('/?success=1')
    return render(request, 'web/index.html')

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
    leads = Lead.objects.filter(is_processed=False).order_by('-created_at')
    return render(request, 'web/manage_tickets.html', {
        'review_tickets': review_tickets,
        'tickets': all_tickets,
        'partners': partners,
        'leads': leads,
    })

def update_ticket_admin(request, ticket_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin/login/?next=/manage/')

    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        partner_id = request.POST.get('partner_id')
        status = request.POST.get('status')

        ticket.partner = get_object_or_404(Partner, id=partner_id) if partner_id else None
        if status in dict(Ticket.STATUS_CHOICES):
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

