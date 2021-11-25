from elasticsearch import Elasticsearch
import pandas as pd
import json,re,time
from sinling import SinhalaTokenizer, SinhalaStemmer,word_splitter
from nltk.stem import PorterStemmer
from filter import Filter

tokenizer = SinhalaTokenizer()
stemmer = SinhalaStemmer()
porter_stemmer = PorterStemmer()

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

INDEX = 'player-index'

NAME_FIELD = 'full_name'
BIO_FIELD = 'bio'
TEAMS_FIELD = 'teams'
BIRTH_CITY_FIELD = 'born_city'
BIRTH_YEAR_FILED = 'birthyear'
# BAT_AVG_FIELD = 'batting_Ave'
MATCHES_FIELD = 'bat_Mat'
HIGHEST_SCORE_FIELD = 'bat_HS'
WICKETS_FIELD = 'bowl_Wkts'
SCORED_RUNS_FIELD = 'bat_Runs'
PLAYING_ROLE_FIELD = 'playing_role'
BATTING_STYLE_FIELD = 'batting_style'
BOWLING_STYLE_FIELD = 'bowling_style'

BIRTH_INDICATORS = ['ඉපද', u'ඉපදුන',u'බිහි',u'උත්පත්',u'උද්භ',u'උපත',u'උප්පැ',u'උපන්',u'උ පන්',u'ජන්',u'ජම්',u'මූලාරම්භ',u'වංශ',u'ප්‍රසූ',u'ජාතක',u'ප්‍රභ ව',u'මූලාරම්භ']
BIRTH_YEAR_INDICATORS = [u'වසර', u'වර්ෂය', u'අවුරුද්ද']
LOCATION_INDICATORS = [u'ස්ථාන',u' තැන ',u'නගර',u'ගම',u'ග්‍රාම']
BOWLING_INDICATORS = [u'වේග',u'දඟ',u'දග',u'ස්පින්',u'ෆාස්ට්']
BATTING_INDICATORS = [u'පිති',u'පහර']
ROLE_INDICATORS = [u'පිතිකර',u'පිති කර' ,u'පන්දු',u'බැට්',u'තුන්',u'ඉරියව්',u'ඕල්']
TEAM_INDICATORS = [u'කන්ඩාය', u'සමාජ', u'සංගම', u'වෙනුවෙන්']
COMMON_TERMS = ['ක්‍රීඩකයින්', 'ක්‍රීඩක']
STAT_INDICATORS = {
    'highest_score' : ['hs'],
    'wickets' : [u'කඩුල'],
    'runs' : [u'ලකුන'],
    'matches': [u'තරග', 'match'],
    'average' : [u'මධ්‍යහ්න'],   
}

STAT_FIELD_MAP = {
    'wickets' : WICKETS_FIELD,
    'runs' : SCORED_RUNS_FIELD,
    'matches':  MATCHES_FIELD,
    'highest_score': HIGHEST_SCORE_FIELD
} 

SYNONYMS = {
    u'කඩුලු': [u'විකට්', u'දවා ගැනීම්', u'දැවීම්', u'අවුට්', u'wicket'],
    u'වසර ': [u'අවුරුද්ද', u'වර්ෂ'],
    # 'ක්‍රීඩා': ['සෙල්ලම්', 'තරග', 'සම්බන්ධ'],
    u'වැඩි ම': [u'ඉහල ම'],
    u'ලකුන': [u'run', u'ලකුනු'],
    u'මධ්‍යහ්න':  [u'මධ්‍යක', u'සාමාන්‍ ය', u'සාමාන්‍ය',u'මධ්‍යන්‍',u'මධ්‍යහ්න', u'average'],
    # '': ['වරක්' , 'වතාවක්', 'සැරයක්', 'දී', 'දි' , 'ක්', 'වර්ෂය', 'අවුරුද්ද']
}

COMPARISON_INDICATORS = {
    '>=' : ['>=','=>'],
    '<=' : ['<=', '=<'],
    '<': [u'<', u'අඩු [^ම]', u'අඩු$', u'උපරි', u'වැඩි ම', u' කුඩා\\s*'],
    '>': [u'>', u'වැඩි [^ම]', u'වැඩි$', u'අඩු ම', u'\\s+වත්\\s*', u'අව ම', u'ඉහ ල'],# 'පසු', 'පස්ස', 'පහු', 'මතු','අනතුර'],
    '=': [u'=', u'\\s+සමාන\s*', u'\\s+ක් (?!වත්)\\s*', u'\\s+ක්$']
}

SEARCH_LEFT_NUM_WIDTH = 0
SEARCH_RIGHT_NUM_WIDTH = 4
SEARCH_LEFT_OP_WIDTH = 0
SEARCH_RIGHT_OP_WIDTH = 4

TEXT_FIELDS = [
    NAME_FIELD, 
    TEAMS_FIELD, 
    BIRTH_CITY_FIELD,  
    BIO_FIELD,
    BIRTH_YEAR_FILED,
    PLAYING_ROLE_FIELD,
    BATTING_STYLE_FIELD,
    BOWLING_STYLE_FIELD,
]

SIN_LETTERS = u'අඉඊඋඍඑඔකඛගඝඞචඡජඣඤඥටඨඩඪණතථදධනපඵබභමඹයරලවශෂසහළෆ'
SIN_ACCESSORIES = ''.join([chr(u) for u in [0xdd0, 0xdd1, 0xdd2, 0xdd3, 0xdd4, 0xdd6,
    0xdd8, 0xdd9, 0xdda, 0xddb, 0xddc, 0xddd, 0xdde, 0x0DCA, 0x0DCF,0x0D82, 0x0D83]])

def sin_letter_count(string):
    no_accessories = re.sub(u'['+SIN_ACCESSORIES+']','', string)
    return len(no_accessories)

def is_num(str):
    try: 
        float(str)
    except ValueError: 
        return False
    return True

def get_filter_array(query):

    filters = []
    query = query.replace('වැඩි ම ලකුන', 'hs')
    query_tokens = query.split()
    for t in range(len(query_tokens)):
        token = query_tokens[t]
        for entity, indicators in STAT_INDICATORS.items():
            if token in indicators:
                number_found = False
                comparision_found = False
                comparision = '='
                num_left_bound = max(0,t-SEARCH_LEFT_NUM_WIDTH)
                num_right_bound = min(len(query_tokens), t+SEARCH_RIGHT_NUM_WIDTH+1)
                op_left_bound = max(0,t-SEARCH_LEFT_OP_WIDTH)
                op_right_bound = min(len(query_tokens), t+SEARCH_RIGHT_OP_WIDTH+1)
                for s in range(num_left_bound, num_right_bound):
                    if number_found and comparision_found:
                        break
                    if is_num(query_tokens[s]):
                        number = float(query_tokens[s])
                        number_found = True
                        break
                window = ' '.join(query_tokens[op_left_bound: op_right_bound])
                for key, values in COMPARISON_INDICATORS.items():
                    for value in values:
                        if re.search(value, window):
                            comparision_found = True
                            comparision = key
                            break
                    if comparision_found:
                        break
                if number_found and comparision_found:
                    filters.append(Filter(entity, comparision, number, t))
    return filters

def get_filter_dict(filters):
    dct = {
        "term" : {},
        "range" : {}
    }
    for filter in filters:
        entity = STAT_FIELD_MAP[filter.entity]
        if filter.operator == '=':
            dct['term'][entity] = filter.value
        else:
            if filter.operator == '>=':
                op = 'gte'
            elif filter.operator == '<=':
                op = 'lte'
            elif filter.operator == '>':
                op = 'gt'
            else:
                op = 'lt'
            dct['range'][entity] = {op: filter.value}
    if dct['term'] == {}:
        del dct['term']
    if dct['range'] == {}:
        del dct['range']

    # print(dct)

    return dct
def build_query_dict(query):

    normalized_query = normalize_query(query)
    boost_weights = get_boost_weights_for_text_fields(normalized_query)
    filter_arr = get_filter_array(normalized_query)
    filters = get_filter_dict(filter_arr)
    for c in COMMON_TERMS:
        query = query.replace(c, '') 
        normalized_query = normalized_query.replace(c, '')
    query += ' ' + normalized_query
    print(query)
    fields = ['{0}^{1}'.format(field, weight) for field, weight in boost_weights.items()]
    # print(get_filter_array(normalized_query))
    query_dct =   { 
        "bool": { 
        "should": {
            "multi_match" : {
                "query" : query,
                "fields" : fields,

                "type" : "best_fields"
            }
        }
        }
    }
    if filters != {}:
        query_dct['bool']['filter'] = filters
    print(query_dct)
    return query_dct

def get_boost_weights_for_text_fields(query):
    print('norm',query)
    boost_weights = {k : 1 for k in TEXT_FIELDS}
    boost_weights['bio'] = 1
    for i in BIRTH_INDICATORS:
        if i in query:
            boost_weights[BIRTH_CITY_FIELD] += 3
            break
    
    for i in LOCATION_INDICATORS:
        if i in query:
            boost_weights[BIRTH_CITY_FIELD] += 2
            break

    for i in BOWLING_INDICATORS:
        if i in query:
            boost_weights[BOWLING_STYLE_FIELD] += 2
            break

    for i in BATTING_INDICATORS:
        if i in query:
            boost_weights[BATTING_STYLE_FIELD] += 2
            break

    for i in TEAM_INDICATORS:
        if i in query:
            boost_weights[TEAMS_FIELD] += 2
            break
    
    for i in ROLE_INDICATORS:
        if i in query:
            boost_weights[PLAYING_ROLE_FIELD] += 2
            break

    for i in BIRTH_YEAR_INDICATORS:
        if i in query:
            boost_weights[BIRTH_YEAR_FILED] += 2
    for token in query.split():
        if is_num(token):
            num = float(token)
            if  00 < num < 99 or 1940 < num < 2021:
                boost_weights[BIRTH_YEAR_FILED] +=2
                break
    # print(boost_weights)
    return boost_weights

def add_space_after_numbers(query):
    return re.sub(u'(\d)([^0-9,.])', r'\1 \2', query)

def normalize_query(query):
    query = porter_stemmer.stem(query)
    query = add_space_after_numbers(query)
    
    for replacement, matches in SYNONYMS.items():
        for match in matches:
            query = query.replace(match, replacement)
            
    new_query = []
    for token in query.split():
        if sin_letter_count(token) > 2:
            prefix, suffix = stemmer.stem(token)
            prefix_letter_count = sin_letter_count(prefix) 
            suffix_letter_count = sin_letter_count(suffix)
            # print(len(re.sub('['+ SIN_ACCESSORIES+'\\s]', '', suffix)), re.sub('['+ SIN_ACCESSORIES+'\\s]', '', suffix), 'fs')
            if prefix_letter_count > 1 and (suffix_letter_count == 0 or (suffix_letter_count== 1 and re.sub('['+ SIN_ACCESSORIES+'\\s]', '', suffix) in [u'ව',u'ම',u'ට',u'ය'])):
                new_query.append(prefix)
                if sin_letter_count(suffix) >= 1:
                    new_query.append(suffix)
            else:
                new_query.append(token)
        else:
            new_query.append(token)

    stemmed = ' '.join(new_query)
    stemmed = stemmed.replace('ඡ','ච').replace('ණ','න').replace('ළ', 'ල') 

    for replacement, matches in SYNONYMS.items():
        for match in matches:
            stemmed = stemmed.replace(match, replacement)

    normalized = []

    #Splits
    for token in stemmed.split():
        if token in ['දකුනත', 'වමත']:
            normalized.append(token[:token.rindex('ත')])
            normalized.append('අත')
        else:
            normalized.append(token)
    return ' '.join(normalized)

def filtered_search_results(query):

    # query = normalize_query(query)
    query_dct = build_query_dict(query)
    res = es.search(index=INDEX, query=query_dct)
    return json.dumps(res, ensure_ascii=False)

    