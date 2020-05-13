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
    """
    Funkcia, ktorá vymaže html tagy z textu.
    :param text: vstupný text
    :return: výstupný text
    """
    return TAG_RE.sub('', text)


def UTFToASCII(text):
    """
    Funkcia, ktorá vymaže chybné znaky pre telefón z textu.
    :param text: vstupný text
    :return: výstupný text
    """
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode("ascii").replace('"', '').replace("'",
                                                                                                                  '')


def services_list(request):
    """
    V pohľade services_list sa nám vygeneruje pohľad pre telefón obsahujúci základné
    menu. V základnom menu sa zobrazia všetky služby, ktoré sú podporované našim systémom.
    MenuItem je model, v ktorom sú uchovávané všetky služby. Z neho sa jednotlivo vyberajú
    objekty a zaradom sa generujú podľa XML šablóny.
    :param request: webová požiadavka
    :return: webová odpoveď
    """
    items = MenuItem.objects.all()
    services = []
    for service in items:
        services.append({'name': service.name, 'url': service.name.lower().replace(" ", "_")})
    return render(request, 'services/services_list.xml', {'services': services})


def rss_list(request):
    """
    V pohľade rss_list sa generuje pohľad, ktorý obsahuje menu poskytovateľov RSS
    zdrojov. Každá položka v menu reprezentuje jedného poskytovateľa RSS. RSSItem je
    model, v ktorom sú uchovávaní všetci poskytovatelia RSS.
    :param request: webová požiadavka
    :return: webová odpoveď
    """
    items = RSSItem.objects.all()
    rsses = []
    for rss in items:
        rsses.append({'name': rss.name, 'url': rss.url, 'url2': rss.name.lower().replace(" ", "%20")})
    return render(request, 'services/rss_list.xml', {'rsses': rsses})


def rss_item(request, service):
    """
    V pohľade rss_item sa vygeneruje pohľad, ktorý obsahuje menu RSS správ. Každá
    položka v menu reprezentuje jednu správu RSS. Správy sa načítavajú dynamicky po zavolaní
    pohľadu, čiže nie sú nikde ukladané. RSS zdroje sú sťahované parsované cez Python modul
    feedparser (Universal Feed Parser). Všetky znaky, ktoré sú použité v správach musia byť
    ASCII. UTF-8 znaky sa na telefóne nemusia správne zobrazovať a preto sú prevádzané do
    znakov ASCII.
    :param request: webová požiadavka
    :param service: sluba RSS
    :return: webová odpoveď
    """
    items = RSSItem.objects.filter(name__icontains=service)
    srv = items[0]
    itms = []
    feed = feedparser.parse(srv.url)
    for entry in feed.entries:
        itms.append({'title': UTFToASCII(remove_tags(html.unescape(entry.title)).strip()[:62]),
                     'description': UTFToASCII(remove_tags(html.unescape(entry.summary)).strip().replace(" ", "%20"))[:254 - len(request.get_host()) - 30]})
    return render(request, 'services/rss_service.xml', {'rss': srv, 'entries': itms[:20]})


def message(request, msg):
    """
    Vytvára zobrazenie textového obsahu na telefóne.
    :param request: webová požiadavka
    :param msg: správa ktorá sa má zobraziť
    :return: webová odpoveď
    """
    return render(request, 'services/message.xml', {'text': msg})


def message_empty(request):
    """
    Vytvára zobrazenie hlášky "Ziadne data".
    :param request: webová požiadavka
    :return: webová odpoveď
    """
    return render(request, 'services/message.xml', {'text': "Ziadne data"})


def weather_prompt(request):
    """
    Pohľad weather_prompt slúži na získanie vstupu od používateľa. Vstup tvorí EČV
    mesta pre ktoré chce používateľ získať aktuálne počasie.
    :param request: webová požiadavka
    :return: webová odpoveď
    """
    return render(request, 'services/weather_prompt.xml', {})


def weather(request):
    """
    Pohľad weather nám generuje samotný výpis počasia pre zvolené mesto. Ako
    poskytovateľa sme si zvolili OpenWeatherApi, ktorý nám bezplatne poskytuje informácie o
    aktuálnom počasí. Vstup získavame GET metódou parametra mesto v ktorom sa nachádza
    EČV zvoleného mesta. EČV mesta priradíme pomocou slovníka k celému názvu mesta.
    OpenWeatherApi nám vráti json data s informáciami o počasí ktoré následne dekódujeme
    do objektu. Objekt následne prevedieme do XML tvaru ktorý bude vytvorený metódou
    render. Ak mesto nebolo nájdené alebo nastala chyba tak na obrazovku vypíšeme hlášku
    o chybe.
    :param request: webová požiadavka
    :return: webová odpoveď
    """
    try:
        url = "http://api.openweathermap.org/data/2.5/weather?q=" + mesta.get(
            request.GET.get('mesto')) + "&appid=" + openWatherApiKey + "&lang=sk&units=metric"
        res = requests.get(url)
        res.encoding = 'win-1250'
        jsonData = json.loads(res.content.decode())
        return render(request, 'services/weather_message.xml',
                      {'w': jsonData, 'weather': UTFToASCII(jsonData['weather'][0]['description']),
                       'city': UTFToASCII(jsonData['name'])}, content_type="application/xml")
    except:
        return render(request, 'services/message.xml', {'text': "Mesto nenajdene"})


def contacts_prompt(request):
    """
    Pohľad contact_prompt slúži na získanie vstupu od používateľa. Používateľ zadáva
    meno a/alebo priezvisko zamestnanca, o ktorom chce získať informácie.
    :param request: webová požiadavka
    :return: webová odpoveď
    """
    return render(request, 'services/contacts_prompt.xml', {})


def contacts_engine(request):
    """
    Pohľad contacts_engine je časť z hlavnej logiky fungovania vyhľadávania kontaktov
    v adresári zamestnancov UNIZA, ktorý sa nachádza na adrese
    http://nic.uniza.sk/webservices/getDirectory.php. Jej úlohou je získať všetky kontakty
    vyhovujúce zadanému menu a/alebo priezvisku pomocou dátového formátu JSON metódou
    GET. Následne zo získaných dát vytvoríme pole objektov (kontaktov). Tieto kontakty
    nakoniec pošleme do funkcie render, ktorá nám vygeneruje za pomoci šablóny výstup pre
    telefón Cisco vo formáte XML.
    :param request: webová požiadavka
    :return: webová odpoveď
    """
    url = "http://nic.uniza.sk/webservices/getDirectory.php?q=" + request.GET.get('meno')
    req = requests.get(url)
    req.encoding = 'win-1250'
    jsonData = json.loads(req.content.decode())
    jsonList = jsonData['directory']
    parsedData = []
    for directory in jsonList:
        cardData = {}
        cardData['url'] = directory['oc'].replace(" ", "%20")
        cardData['nameurl'] = UTFToASCII(directory['name']).replace(" ", "%20")
        cardData['name'] = UTFToASCII(directory['name'])
        parsedData.append(cardData)
    return render(request, 'services/contacts_list.xml', {'contacts': parsedData[:20]})


def contact(request):
    """
    V pohľade contact získavame informácie pre konkrétny kontakt podľa mena a oc
    (osobného čísla zamestnanca) pre prípad, že zamestnancov s rovnakým menom je viac.
    Metódou GET opäť získame zoznam zamestnancov podľa mena a priezviska zamestnanca.
    Následne v prípade viacerých rovnakých mien overíme aj oc. Metódou render vygenerujeme
    menu kontaktu s parametrom objekt kontaktu.
    :param request: webová požiadavka
    :return: webová odpoveď
    """
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
        cardData['name'] = UTFToASCII(directory['name'])
        if UTFToASCII(directory['function']) == "":
            cardData['function'] = "zamestnanec"
        else:
            cardData['function'] = UTFToASCII(directory['function']).replace(" ", "%20")
        cardData['tel'] = directory['tel']
        cardData['mobil'] = directory['mobil']
        cardData['mail'] = directory['mail']
        cardData['job'] = UTFToASCII(directory['job'])
        cardData['room'] = UTFToASCII(directory['room'])
        parsedData.append(cardData)
    for c in parsedData:
        if c.get('oc') == oc and c.get('name') == meno:
            if c.get('mobil') != "":
                mobilenumbers = c.get('mobil').split(',')
            else:
                mobilenumbers = []
            if c.get('tel') != "":
                telnumbers = c.get('tel').split(',')
            else:
                telnumbers = []
            return render(request, 'services/contact_number.xml', {'name': c.get('name'), 'mobile': mobilenumbers, 'tel': telnumbers})


def contact_dialer_empty(request):
    """
    Pohľad contact_dialer_empty slúži pre prípad, keď zamestnanec nemá zadané
    telefónne číslo. Vtedy sa zavolá render so šablónou message.xml, ktorú sme si predstavili
    vyššie, do ktorej pošleme text že toto pole kontaktu neobsahuje dáta.
    :param request: webová požiadavka
    :return: webová odpoveď
    """
    return render(request, 'services/message.xml', {'text': "Ziadne data"})


def contacts_prompt_zlatestranky(request):
    """
    Pohľad contacts_prompt_zlatestranky slúži na získanie vstupu od používateľa.
    Používateľ zadáva meno a/alebo priezvisko človeka, o ktorom chce získať informácie.
    :param request: webová požiadavka
    :return: webová odpoveď
    """
    return render(request, 'services/contacts_prompt_zlatestranky.xml', {})


def contacts_engine_zlatestranky(request):
    """
    Pohľad contacts_engine_zlatestranky ukrýva logiku vyhľadávania kontaktov na
    portáli zlatestránky.sk. Jej úlohou je pomocou metódy GET získať všetky kontakty
    vyhovujúce zadanému menu a/alebo priezvisku vo formáte HTML stránky. Následne zo
    získanej stránky vytvoríme pole objektov (kontaktov). Tieto kontakty nakoniec pošleme do
    funkcie render, ktorá nám vygeneruje za pomoci šablóny výstup pre telefón Cisco vo formáte
    XML.
    :param request: webová požiadavka
    :return: webová odpoveď
    """
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
    return render(request, 'services/contacts_list_zlatestranky.xml', {'contacts': parsedData[:20]})


def contact_zlatestranky(request):
    """
    V pohľade contact_zlatestranky získavame informácie pre konkrétny kontakt podľa
    oc (osobného čísla). Metódou GET opäť získame HTML podstránku kontaktu podľa oc.
    Metódou render vygenerujeme menu kontaktu s parametrom objekt kontaktu, v ktorom sa
    nachádza meno kontaktu a telefónne číslo.
    :param request: webová požiadavka
    :return: webová odpoveď
    """
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
        pass
    return render(request, 'services/contact_zlatestranky.xml', {'contact': data})
