from base64 import b64decode

import requests
from bs4 import BeautifulSoup
from pushbullet import Pushbullet


# configuration
USERNAME = 'xxx@students.zhaw.ch'
PASSWORD = ''
PUSHBULLET_ACCESS_TOKEN = ''


LOGIN_URL = 'https://eventoweb.zhaw.ch/cst_pages/login.aspx'
GRADE_URL = 'https://eventoweb.zhaw.ch/CST_Pages/Cst_StudentNoten.aspx?node=c9e803e5-92f3-4a53-acfc-8b5e1cba719d'
GRADE_TABLE_ID = 'ctl00_WebPartManager1_gwpCst_StudentNoten1_Cst_StudentNoten1_gridview'

client = requests.session()
response = client.get(LOGIN_URL)

soup = BeautifulSoup(response.text, 'html.parser')

# get all form fields and copy them to payload
payload = {
    field.get('name'): field.get('value')
    for field in soup.find_all('input')
}

# set login data
payload['ctl00$WebPartManager1$gwpLogin1$Login1$LoginMask$UserName'] = USERNAME
payload['ctl00$WebPartManager1$gwpLogin1$Login1$LoginMask$Password'] = PASSWORD

# login
response = client.post(LOGIN_URL,data=payload)

# get grades page
response = client.get(GRADE_URL)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table', {'id': GRADE_TABLE_ID})
rows = list(table.find_all('tr'))

grades = []
all_blocked = True

for row in rows[1:]:
    texts = [field.text for field in row.find_all('td')]
    modname = texts[1].split('.')[3]
    grade = texts[3]

    if grade != 'gesperrt':
        all_blocked = False

    grades.append('{}: {}'.format(modname, grade))

if not all_blocked:
    # send push
    print('sending push')
    pb = Pushbullet(PUSHBULLET_ACCESS_TOKEN)
    pb.push_note('Grades', '\n'.join(grades))
else:
    print('all grades still blocked, not sending notification')
