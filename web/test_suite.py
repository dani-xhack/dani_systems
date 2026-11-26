import pytest
from django.contrib.auth.models import User
from web.models import Lead, Partner, Joke, Ticket

@pytest.mark.django_db
def test_security_headers_and_xss_sanitization(client):
    res = client.get('/')
    assert res.status_code == 200
    assert 'Content-Security-Policy' in res.headers
    assert res.headers['X-Content-Type-Options'] == 'nosniff'
    assert res.headers['X-Frame-Options'] == 'DENY'

    client.post('/', {
        'name': '<script>alert("xss")</script>Иван',
        'phone': 'javascript:alert(1)+79990001122',
        'agree_pdn': 'on',
    })
    lead = Lead.objects.latest('id')
    assert '<script>' not in lead.name
    assert 'Иван' in lead.name
    assert 'javascript:' not in lead.phone

@pytest.mark.django_db
def test_client_registration_requires_pdn_consent(client):
    res_fail = client.post('/register/', {
        'username': 'client_no_pdn',
        'phone': '+79001112233',
        'password': 'StrongPassword123!',
    })
    assert res_fail.status_code == 200
    assert not User.objects.filter(username='client_no_pdn').exists()

    res_ok = client.post('/register/', {
        'username': 'client_ok',
        'phone': '+79001112233',
        'password': 'StrongPassword123!',
        'agree_pdn': 'on',
    })
    assert res_ok.status_code == 302
    assert User.objects.filter(username='client_ok').exists()

@pytest.mark.django_db
def test_partner_registration_requires_offer_and_records_timestamp(client):
    res_fail = client.post('/register/partner/', {
        'username': 'partner_no_offer',
        'phone': '+79004445566',
        'password': 'StrongPassword123!',
    })
    assert res_fail.status_code == 200
    assert not Partner.objects.filter(user__username='partner_no_offer').exists()

    res_ok = client.post('/register/partner/', {
        'username': 'partner_ok',
        'phone': '+79004445566',
        'password': 'StrongPassword123!',
        'agree_offer': 'on',
    })
    assert res_ok.status_code == 302
    partner = Partner.objects.get(user__username='partner_ok')
    assert partner.offer_accepted_at is not None

@pytest.mark.django_db
def test_leads_do_not_appear_on_manage_tickets(client):
    admin = User.objects.create_superuser('admin_test', 'a@test.ru', 'AdminPass123!')
    Lead.objects.create(name='Первичный Лид С Сайта', phone='+79998887766')

    client.force_login(admin)
    res = client.get('/manage/')
    assert res.status_code == 200
    assert 'Первичный Лид С Сайта' not in res.content.decode('utf-8')

@pytest.mark.django_db
def test_teleport_jokes_and_hex_jokes(client):
    client.post('/teleport/', {
        'form_type': 'hex',
        'name': 'Космонавт',
        'text': 'd0 9f d1 80 d0 b8 d0 b2 d0 b5 d1 82',
    })
    joke = Joke.objects.latest('id')
    assert joke.text.startswith('[HEX]')
    assert joke.is_published is False

    joke.is_published = True
    joke.save()
    res = client.get('/teleport/')
    assert res.status_code == 200
    assert 'd0 9f d1 80 d0 b8 d0 b2 d0 b5 d1 82' in res.content.decode('utf-8')
