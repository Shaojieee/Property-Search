import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import sys
sys.path.append('../../')
from onemap_client import OneMapClient
from dotenv import load_dotenv
load_dotenv()
import json
import re

email = os.environ['ONE_MAP_API_EMAIL']
password = os.environ['ONE_MAP_API_PASSWORD']


def get_preschool(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0]

    search_results = client.retrieve_theme(query_name='preschools_location')['SrchResults']
    # search results starts from index
    pre_school_locations = {'results':[]}
    lat_longs = set()

    for pre_school in search_results[1:]:
        coord_list = pre_school['LatLng'].split(',')
        lat_long = tuple([float(coord_list[0]), float(coord_list[1])])
        if lat_long not in lat_longs:
            lat_longs.add(lat_long)
            pre_school_locations['results'].append({'name':pre_school['NAME'],'lat':float(coord_list[0]),'long':float(coord_list[1])})


    with open(f'{output_dir}/preschool_coords.json','w')as f:
        json.dump(pre_school_locations,f)

def get_kindergarten(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0] 

    search_results = client.retrieve_theme(query_name='kindergartens')['SrchResults']
    # search results starts from index
    kind_loc = {'results':[]}
    lat_longs = set()
    for kind in search_results[1:]:
        coord_list = kind['LatLng'].split(',')
        lat_long = tuple([float(coord_list[0]), float(coord_list[1])])
        if lat_long not in lat_longs:
            lat_longs.add(lat_long)
            kind_loc['results'].append({'name':kind['NAME'],'lat':float(coord_list[0]),'long':float(coord_list[1])})

        with open(f'{output_dir}/kindergarten_coords.json','w')as f:
            json.dump(kind_loc,f)




def filter_school_search(cur_sch_name,existing_sch_list):
    # conditions to check if search result returned a specific block/building within a school or if school has been stored in existing_schools already
    if '@' in cur_sch_name:
        return True
    if '(U/C)' in cur_sch_name:
        return True
    if 'BUILDING' in cur_sch_name:
        return True
    for existing_sch in existing_sch_list:
        if cur_sch_name == existing_sch['name']:
            return True
    pattern = r"(\(|\[)*.(PRIMARY|HIGH|SECONDARY) SCHOOL(\]|\))"
    if re.search(pattern, cur_sch_name):
        return True
    return False


def get_primary_school(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0] 

    tot_page_num = client.search(search_val='Primary School')['totalNumPages']
    primary_sch = {'results':[]}
    lat_longs = set()

    try:
        for i in range(tot_page_num):
            for sch in client.search(search_val='Primary School',page_num=i+1)['results']:
                # Do not add coordinate if building is a specific block within a school
                if filter_school_search(sch['BUILDING'],primary_sch['results']):
                    continue
                else:
                    lat_long = tuple([float(sch['LATITUDE']), float(sch['LONGITUDE'])])
                    if lat_long not in lat_longs:
                        lat_longs.add(lat_long)
                        primary_sch['results'].append({'name':sch['BUILDING'],'lat':float(sch['LATITUDE']),'long':float(sch['LONGITUDE'])})
    except:
        print('No Results!')

    with open(f'{output_dir}/primary_school_coords.json','w')as f:
        json.dump(primary_sch,f)

def get_secondary_school(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0] 

    tot_page_num = client.search(search_val='Secondary School')['totalNumPages']
    sec_sch = {'results':[]}
    lat_longs = set()

    try:
        for i in range(tot_page_num):
            for sch in client.search(search_val='Secondary School',page_num=i+1)['results']:
                # Do not add coordinate if building is a specific block within a school
                if filter_school_search(sch['BUILDING'],sec_sch['results']):
                    print(sch['BUILDING'])
                    continue
                else:
                    lat_long = tuple([float(sch['LATITUDE']), float(sch['LONGITUDE'])])
                    if lat_long not in lat_longs:
                        lat_longs.add(lat_long)
                        sec_sch['results'].append({'name':sch['BUILDING'],'lat':float(sch['LATITUDE']),'long':float(sch['LONGITUDE'])})
    except:
        print('No Results!')

    tot_page_num = client.search(search_val='High School')['totalNumPages']

    try:
        for i in range(tot_page_num):
            for sch in client.search(search_val='High School',page_num=i+1)['results']:
                # Do not add coordinate if building is a specific block within a school
                if filter_school_search(sch['BUILDING'],sec_sch['results']):
                    print(sch['BUILDING'])
                    continue
                else:
                    lat_long = tuple([float(sch['LATITUDE']), float(sch['LONGITUDE'])])
                    if lat_long not in lat_longs:
                        lat_longs.add(lat_long)
                        sec_sch['results'].append({'name':sch['BUILDING'],'lat':float(sch['LATITUDE']),'long':float(sch['LONGITUDE'])})
    except:
        print('No Results!')


    with open(f'{output_dir}/secondary_school_coords.json','w')as f:
        json.dump(sec_sch,f)


def get_college(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0] 

    tot_page_num = client.search(search_val='Junior College')['totalNumPages']
    jc = {'results':[]}
    lat_longs = set()
    try:
        for i in range(tot_page_num):
            for sch in client.search(search_val='Junior College',page_num=i+1)['results']:
                # Do not add coordinate if building is a specific block within a school
                if filter_school_search(sch['BUILDING'],jc['results']):
                    print(sch['BUILDING'])
                    continue
                else:
                    lat_long = tuple([float(sch['LATITUDE']), float(sch['LONGITUDE'])])
                    if lat_long not in lat_longs:
                        lat_longs.add(lat_long)
                        jc['results'].append({'name':sch['BUILDING'],'lat':float(sch['LATITUDE']),'long':float(sch['LONGITUDE'])})
    except:
        print('No Results!')


    with open(f'{output_dir}/college_coords.json','w')as f:
        json.dump(jc,f)


def get_nparks(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0] 

    search_results = client.retrieve_theme(query_name='nationalparks')['SrchResults']
    # search results starts from index
    nparks_loc = {'results':[]}
    lat_longs = set()
    for npark in search_results[1:]:
        coord_list = npark['LatLng'].split(',')
        lat_long = tuple([float(coord_list[0]), float(coord_list[1])])
        if lat_long not in lat_longs:
            lat_longs.add(lat_long)
            nparks_loc['results'].append({'name':npark['NAME'],'lat':float(coord_list[0]),'long':float(coord_list[1])})


    with open(f'{output_dir}/npark_coords.json','w')as f:
        json.dump(nparks_loc,f)


def get_sports_facility(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0] 

    search_results = client.retrieve_theme(query_name='ssc_sports_facilities')['SrchResults']
    # search results starts from index
    sports_loc = {'results':[]}
    lat_longs = set()
    for sport in search_results[1:]:
        coord_list = sport['LatLng'].split(',')
        lat_long = tuple([float(coord_list[0]), float(coord_list[1])])
        if lat_long not in lat_longs:
            lat_longs.add(lat_long)
            sports_loc['results'].append({'name':sport['NAME'],'lat':float(coord_list[0]),'long':float(coord_list[1])})

    with open(f'{output_dir}/sport_facility_coords.json','w')as f:
        json.dump(sports_loc,f)


def get_childcare(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0] 

    search_results = client.retrieve_theme(query_name='childcare')['SrchResults']
    # search results starts from index
    childcare_loc = {'results':[]}
    lat_longs = set()
    for childcare in search_results[1:]:
        coord_list = childcare['LatLng'].split(',')
        lat_long = tuple([float(coord_list[0]), float(coord_list[1])])
        if lat_long not in lat_longs:
            lat_longs.add(lat_long)
            childcare_loc['results'].append({'name':childcare['NAME'],'lat':float(coord_list[0]),'long':float(coord_list[1])})
    
    with open(f'{output_dir}/childcare_coords.json','w')as f:
        json.dump(childcare_loc,f)

def get_cycling_path(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0] 

    search_results = client.retrieve_theme(query_name='cyclingpath')['SrchResults']
    # search results starts from index
    cycling_path = {'results':[]}

    for path in search_results[1:]:
        for coord in path['LatLng']:
            if coord[0]>90:
                lat = coord[1]
                long = coord[0]
            else:
                lat = coord[0]
                long = coord[1]
            cycling_path['results'].append({'name':path['NAME'],'lat':lat, 'long': long})

    with open(f'{output_dir}/cycling_path_coords.json','w')as f:
        json.dump(cycling_path,f)


def get_disability_service(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0]

    def remove_extra_spaces(input_string):
        return re.sub('\s+', ' ', input_string).strip() 

    search_results = client.retrieve_theme(query_name='disability')['SrchResults']
    # search results starts from index
    disability_loc = {'results':[]}
    lat_longs = set()
    for disability in search_results[1:]:
        coord_list = disability['LatLng'].split(',')
        lat_long = tuple([float(coord_list[0]), float(coord_list[1])])
        if lat_long not in lat_longs:
            lat_longs.add(lat_long)
            disability_loc['results'].append({'name':remove_extra_spaces(disability['NAME']),'lat':float(coord_list[0]),'long':float(coord_list[1])})
    
    with open(f'{output_dir}/disability_service_coords.json','w')as f:
        json.dump(disability_loc,f)


def get_eldercare(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0] 

    search_results = client.retrieve_theme(query_name='eldercare')['SrchResults']
    # search results starts from index
    eldercare_loc = {'results':[]}
    lat_longs = set()
    for eldercare in search_results[1:]:
        coord_list = eldercare['LatLng'].split(',')
        lat_long = tuple([float(coord_list[0]), float(coord_list[1])])
        if lat_long not in lat_longs:
            lat_longs.add(lat_long)
            eldercare_loc['results'].append({'name':eldercare['NAME'],'lat':float(coord_list[0]),'long':float(coord_list[1])})
    
    with open(f'{output_dir}/eldercare_coords.json','w')as f:
        json.dump(eldercare_loc,f)


# Filter away irrelevant results
def filter_mall_search(cur_mall_name,existing_mall_list):
    # do not add location of bank branches within a mall
    if 'OCBC' in cur_mall_name or 'CITIBANK' in cur_mall_name or 'DBS' in cur_mall_name or 'UOB' in cur_mall_name or 'MAYBANK' in cur_mall_name or 'STANDARD CHARTERED BANK' in cur_mall_name:
        return True

    # if name of search result is NIL do not add 
    if cur_mall_name == 'NIL':
        return True
    
    # if cur name already exists do not add
    for existing_mall in existing_mall_list:
        if cur_mall_name == existing_mall['name']:
            return True
   
    pattern = r"(\(|\[).*MALL.*(\]|\))|.*@.*MALL"
    if re.search(pattern, cur_mall_name):
        return True
    return False


def get_malls(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0]

    tot_page_num = client.search(search_val='Mall')['totalNumPages']
    malls_loc = {'results':[]}
    lat_longs = set()

    try:
        for i in range(tot_page_num):
            for mall in client.search(search_val='Mall',page_num=i+1)['results']:
                # do not add duplicate malls
                if not filter_mall_search(mall['BUILDING'],malls_loc['results']):
                    lat_long = tuple([float(mall['LATITUDE']), float(mall['LONGITUDE'])])
                    if lat_long not in lat_longs:
                        lat_longs.add(lat_long)
                        malls_loc['results'].append({'name':mall['BUILDING'],'lat':float(mall['LATITUDE']),'long':float(mall['LONGITUDE'])})
                else:
                    # print those filtered
                    print(mall['BUILDING'])
    except:
        print('No Results!')
    
    with open(f'{output_dir}/mall_coords.json','w')as f:
        json.dump(malls_loc,f)


def filter_hawker_search(curr_hawker_name,existing_hawker_list):

    # if name of search result is NIL do not add 
    if curr_hawker_name == 'NIL':
        return True
    
    # if cur name already exists do not add
    for existing_hawker in existing_hawker_list:
        if curr_hawker_name == existing_hawker['name']:
            return True
    
    return False


def get_hawker(output_dir):
    client = OneMapClient(email,password)
    access_token = client.get_token(email,password)[0]

    tot_page_num = client.search(search_val='Hawker Centre')['totalNumPages']
    hawker_loc = {'results':[]}
    lat_longs = set()

    try:
        for i in range(tot_page_num):
            for hawker in client.search(search_val='Hawker Centre',page_num=i+1)['results']:
                if not filter_hawker_search(hawker['BUILDING'],hawker_loc['results']):
                    lat_long = tuple([float(hawker['LATITUDE']), float(hawker['LONGITUDE'])])
                    if lat_long not in lat_longs:
                        lat_longs.add(lat_long)
                        hawker_loc['results'].append({'name':hawker['BUILDING'],'lat':float(hawker['LATITUDE']),'long':float(hawker['LONGITUDE'])})
                else:
                    print(hawker['BUILDING'])
    except:
        print('No Results!')

    
    with open(f'{output_dir}/hawker_coords.json','w')as f:
        json.dump(hawker_loc,f)
