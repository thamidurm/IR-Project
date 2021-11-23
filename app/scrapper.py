from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import re
import string
import time

cricket_info = pd.DataFrame()

start='https://www.espncricinfo.com'

for letter in string.ascii_lowercase:
    print('Start loading players for letter: {0}'.format(letter))
    url = '{0}/player/team/sri-lanka-8/alpha-{1}'.format(start,letter)
    page = urlopen(url)
    soup = BeautifulSoup(page)
    divs  = soup.findAll('div',  {'class': ['index-data', 'p-3']})
    c = len(divs)
    for div in divs:
        dct = {}
        anchor= div.findAll('a')[0].attrs['href']
        player_page = urlopen('{0}{1}'.format(start,anchor))
        player_page_soup = BeautifulSoup(player_page)
        content = player_page_soup.findAll('div', {'class': 'playerpage-content'})[0]
        # Extract data from overview grid
        for div in content.findAll('div', {'class': 'player_overview-grid'})[0]:
          key = div.p.text.lower().replace(' ', '_')
          value = div.h5.text
          dct[key] = value
        print(dct['full_name'])
        
        # Extract teams played in
        teams = []
        teams_div = content.find('div', {'class': 'overview-teams-grid'})
        if teams_div:
          for div in teams_div:
            team = div.findAll('a')[1].h5.text
            teams.append(team)
        else:
          print('No teams for {0}'.format(dct['full_name']))
        #   team_issues.append(dct)
        dct['teams'] = ','.join(teams)
        
        # Extract biography
        bio = ''
        biography_div = content.find('div', {'class' : 'more-content-gradient-content'})
        if biography_div:
          for p in biography_div:
            if p.b:
              print(p.b)
              bio += re.sub('[^\.][A-Za-z ]+ESPNcricinfo staff','',p.text)
            else:
              bio += p.text
        else:
            print('No biography for {0}'.format(dct['full_name']))
            # bio_issues.append(dct)
          
        dct['bio'] = bio

        if content.find('div', {'class': 'more-content'}) and len(content.findAll('table')) == 3:
          tables = pd.read_html('{0}{1}'.format(start,anchor))
          batting = tables[0][tables[0]['Format'] == 'Test'].iloc[:,1:].add_prefix('batting_')
          bowling = tables[1][tables[1]['Format'] == 'Test'].iloc[:,1:].add_prefix('bowling_')
          if len(batting) == 1:
            dct.update(batting.to_dict(orient='records')[0])
          if len(bowling) == 1:
            dct.update(bowling.to_dict(orient='records')[0])
        else:
            pass
        #   print('Unexpected table layout for {0}'.format(dct['full_name']))
        #   table_issues.append(dct)
        cricket_info = cricket_info.append(dct, ignore_index=True)
    time.sleep(5)

    print('Done loading players for letter: {0}'.format(letter))