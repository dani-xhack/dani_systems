import os, json, urllib.request

def send_max_lead(name, phone):
    token = os.environ.get('MAX_BOT_TOKEN')
    uid = os.environ.get('MAX_ADMIN_ID')
    if not token or not uid:
        return
    u = 'https://' + 'platform-api.max.ru' + f'/messages?user_id={uid}'
    payload = json.dumps({"text": f"\U0001f525 Новая заявка с сайта Dani Systems!\n\n\U0001f464 Имя: {name}\n\U0001f4de Контакт: {phone}"}).encode('utf-8')
    req = urllib.request.Request(u, data=payload, headers={'Authorization': token, 'Content-Type': 'application/json'}, method='POST')
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass
