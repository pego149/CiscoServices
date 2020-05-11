import json
from ast import parse
import html
import re
import feedparser
import requests
import unicodedata
from django.shortcuts import render
from .models import MenuItem, RSSItem

openWatherApiKey = "373a1e70fd8a428e309f164c0274b176"

mesta = {
    "BA": "Bratislava",
    "BB": "Banska+Bystrica",
    "BJ": "Bardejov",
    "BN": "Banovce+nad+bebravou",
    "BR": "Brezno",
    "BS": "Banska+Stiavnica",
    "BY": "Bytca",
    "CA": "Cadca",
    "DK": "Dolny+Kubín",
    "DS": "Dunajska+Streda",
    "DT": "Detva",
    "GA": "Galanta",
    "GL": "Gelnica",
    "HC": "Hlohovec",
    "HE": "Humenne",
    "IL": "Ilava",
    "KA": "Krupina",
    "KE": "Kosice",
    "KK": "Kezmarok",
    "KM": "Kysucke+Nove+Mesto",
    "KN": "Komarno",
    "KS": "Kosice+okolie",
    "LC": "Lucenec",
    "LE": "Levoca",
    "LM": "Liptovsky+Mikulas",
    "LV": "Levice",
    "MA": "Malacky",
    "MI": "Michalovce",
    "ML": "Medzilaborce",
    "MT": "Martin",
    "MY": "Myjava",
    "NM": "Nove+Mesto+nad+Vahom",
    "NO": "Namestovo",
    "NR": "Nitra",
    "NZ": "Nove+Zámky",
    "PB": "Povazska+Bystrica",
    "PD": "Prievidza",
    "PE": "Partizanske",
    "PK": "Pezinok",
    "PN": "Piestany",
    "PO": "Presov",
    "PP": "Poprad",
    "PT": "Poltar",
    "RA": "Revuca",
    "RK": "Ruzomberok",
    "RS": "Rimavska+Sobota",
    "RV": "Roznava",
    "SA": "Šaľa",
    "SB": "Sabinov",
    "SC": "Senec",
    "SE": "Senica",
    "SI": "Skalica",
    "SK": "Svidnik",
    "SL": "Stara+Lubovna",
    "SN": "Spisska+Nova+Ves",
    "SO": "Sobrance",
    "SP": "Stropkov",
    "SV": "Snina",
    "TN": "Trencín",
    "TO": "Topolcany",
    "TR": "Turcianske+Teplice",
    "TS": "Tvrdosin",
    "TT": "Trnava",
    "TV": "Trebisov",
    "VK": "Veľký+Krtíš",
    "VT": "Vranov+nad+Toplou",
    "ZA": "Zilina",
    "ZC": "Zarnovica",
    "ZH": "Ziae+nad+Hronom",
    "ZM": "Zlate+Moravce",
    "ZV": "Zvolen",
}

TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    return TAG_RE.sub('', text)


def UTFToASCII(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode("ascii").replace('"', '').replace("'", '')


def services_list(request):
    items = MenuItem.objects.all()
    services = []
    for service in items:
        services.append({'name': service.name, 'url': service.name.lower().replace(" ","_")})
    return render(request, 'services/services_list.xml', {'services': services}, content_type="application/xml")


def rss_list(request):
    items = RSSItem.objects.all()
    rsses = []
    for rss in items:
        rsses.append({'name': rss.name, 'url': rss.url, 'url2': rss.name.lower().replace(" ","%20")})
    return render(request, 'services/rss_list.xml', {'rsses': rsses}, content_type="application/xml")


def rss_item(request, service):
    items = RSSItem.objects.filter(name__icontains=service)
    srv = items[0]
    itms = []
    feed = feedparser.parse(srv.url)
    for entry in feed.entries:
        itms.append({'title': UTFToASCII(remove_tags(html.unescape(entry.title)).strip()),
                     'description': UTFToASCII(remove_tags(html.unescape(entry.summary)).strip().replace(" ","%20"))})
    return render(request, 'services/rss_service.xml', {'rss': srv, 'entries': itms[:20]}, content_type="application/xml")


def message(request, msg):
    return render(request, 'services/message.xml', {'text': msg}, content_type="application/xml")


def message_empty(request):
    return render(request, 'services/message.xml', {'text': "Ziadne data"}, content_type="application/xml")


def weather_prompt(request):
    return render(request, 'services/weather_prompt.xml', {}, content_type="application/xml")


def weather(request):
    try:
        url = "http://api.openweathermap.org/data/2.5/weather?q=" + mesta.get(request.GET.get('mesto')) + "&appid" \
            "=" + openWatherApiKey + "&lang=sk&units=metric"
        res = requests.get(url)
        res.encoding = 'win-1250'
        jsonData = json.loads(res.content.decode())
        return render(request, 'services/weather_message.xml', {'w': jsonData, 'weather': UTFToASCII(jsonData['weather'][0]['description']), 'city': UTFToASCII(jsonData['name'])}, content_type="application/xml")
    except:
        return render(request, 'services/message.xml', {'text': "Mesto nenajdene"}, content_type="application/xml")


def contacts_prompt(request):
    return render(request, 'services/contacts_prompt.xml', {}, content_type="application/xml")


def contacts_engine(request):
    url = "http://nic.uniza.sk/webservices/getDirectory.php?q=" + request.GET.get('meno')
    req = requests.get(url)
    req.encoding = 'win-1250'
    jsonData = json.loads(req.content.decode())
    jsonList = jsonData['directory']
    parsedData = []
    for directory in jsonList:
        cardData = {}
        cardData['url'] = directory['oc']
        cardData['name'] = UTFToASCII(directory['name'])
        parsedData.append(cardData)
    return render(request, 'services/contacts_list.xml', {'contacts': parsedData[:20]}, content_type="application/xml")


def contact(request):
    oc = request.GET.get('oc')
    meno = request.GET.get('name')
    url = "http://nic.uniza.sk/webservices/getDirectory.php?q=" + meno
    req = requests.get(url)
    req.encoding = 'win-1250'
    jsonData = json.loads(req.content.decode())
    jsonList = jsonData['directory']
    parsedData = []
    for directory in jsonList:
        cardData = {}
        cardData['oc'] = directory['oc']
        cardData['name'] = UTFToASCII(directory['name']).replace(" ","%20")
        if UTFToASCII(directory['function']) == "":
            cardData['function'] = "zamestnanec"
        else:
            cardData['function'] = UTFToASCII(directory['function']).replace(" ","%20")
        cardData['tel'] = directory['tel'].replace(" ","%20")
        cardData['mobil'] = directory['mobil'].replace(" ","%20")
        cardData['mail'] = directory['mail'].replace(" ","%20")
        cardData['job'] = UTFToASCII(directory['job']).replace(" ","%20")
        cardData['room'] = UTFToASCII(directory['room']).replace(" ","%20")
        parsedData.append(cardData)
    for c in parsedData:
        if c.get('oc') == oc and c.get('name') == meno.replace(" ","%20"):
            return render(request, 'services/contact.xml', {'contact': c}, content_type="application/xml")


def contact_dialer(request, numbers):
    out = numbers.split(',')
    return render(request, 'services/contact_number.xml', {'numbers': out}, content_type="application/xml")


def contact_dialer_empty(request):
    return render(request, 'services/message.xml', {'text': "Ziadne data"}, content_type="application/xml")


def contacts_prompt_zlatestranky(request):
    return render(request, 'services/contacts_prompt_zlatestranky.xml', {}, content_type="application/xml")


def contacts_engine_zlatestranky(request):
    url = "https://www.zlatestranky.sk/osoby/hladanie/" + request.GET.get('meno') + "/"
    header = {'Accept-Encoding': 'gzip, deflate, sdch',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
    res = requests.get(url, headers=header)
    res.encoding = 'win-1250'
    strng = res.text
    a = True
    parsedData = []
    while a:
        try:
            data = {}
            index = strng.index('<a class="item__parts" href="')
            strng = strng[index + len('<a class="item__parts" href="'):].strip()
            index = strng.index('">')
            data['url'] = strng[:index].strip()
            index = strng.index('<span itemprop="name">')
            strng = strng[index + len('<span itemprop="name">'):].strip()
            index = strng.index('</span>')
            data['name'] = UTFToASCII(html.unescape(strng[:index]).strip())
            parsedData.append(data)
        except ValueError:
            a = False
    return render(request, 'services/contacts_list_zlatestranky.xml', {'contacts': parsedData[:20]}, content_type="application/xml")


def contact_zlatestranky(request):
    url = "https://www.zlatestranky.sk" + request.GET.get('oc')
    header = {'Accept-Encoding': 'gzip, deflate, sdch',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
    res = requests.get(url, headers=header)
    res.encoding = 'win-1250'
    strng = res.text
    data = {}
    try:
        index = strng.index('<h1 class="bold fl" itemprop="name">')
        strng = strng[index + len('<h1 class="bold fl" itemprop="name">'):].strip()
        index = strng.index('</h1>')
        data['name'] = UTFToASCII(html.unescape(strng[:index]).strip())
        index = strng.index(' <span itemprop="telephone">')
        strng = strng[index + len(' <span itemprop="telephone">'):].strip()
        index = strng.index('</span>')
        data['tel'] = strng[:index].strip()
    except ValueError:
        a = False
    return render(request, 'services/contact_zlatestranky.xml', {'contact': data}, content_type="application/xml")
