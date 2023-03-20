# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 16:37:32 2022

@author: Prateek

Functions to fetch propert data from Domain and save it as sql database
"""

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import sqlite3
import string

api_key = "Add API key"

def get_suburbs():
    HTML = requests.get("https://www.matthewproctor.com/full_australian_postcodes_nsw")
    page = bs(HTML.text, "html.parser")
    table = page.find("table")
    rows = table.findAll("tr")
    data = [[cell.text for cell in row("td")] for row in rows]
    data = pd.DataFrame(data)
    data.columns = data.iloc[0]
    data = data[1:]
    df = data[['Postcode', 'Locality', 'State', 'Category', 
               'Longitude', 'Latitude', 'SA4 Name', 'LGA Region', 'LGA Code']]
    df = df[df['Category'] == 'Delivery Area']
    df.reset_index(drop=True, inplace = True)
    df[['Postcode', 'LGA Code','Longitude', 'Latitude']] = df[['Postcode', 'LGA Code',
                                       'Longitude', 'Latitude']].apply(pd.to_numeric)
    df.drop(['Category'], axis=1, inplace = True)
    df['Locality'] = [string.capwords(s) for s in list(df['Locality'])]
    return df

def save_suburbs_name():
    conn = sqlite3.connect('Suburb_names.db')
    df = get_suburbs()
    df.to_sql('SubNames', conn, if_exists='replace', index = False)
    conn.close()
    return print('Suburbs names saved to database')

def performance_data(Sub, Postcode, Quaters, maxBedrooms, Category):
    State = 'NSW'
    all_df = []
    for Bedrooms in range(1,maxBedrooms+1):
        perf_URL = f'https://api.domain.com.au/v2/suburbPerformanceStatistics/{State}/{Sub}/{Postcode}?propertyCategory={Category}&bedrooms={Bedrooms}&periodSize=quarters&startingPeriodRelativeToCurrent=1&totalPeriods={Quaters}'
        header = {'X-API-Key':api_key}
        response = requests.get(url = perf_URL, headers=header)
        try:
            data = response.json()
        except:
            print(f'JSON cannot be loaded for {Bedrooms} Bedroom {Category} in {Sub}')
            continue
        
        df = pd.DataFrame(data['series']['seriesInfo'])
        new_df = []
        for i, row in df.iterrows():
            tempdf = pd.DataFrame(row['values'], index=[f'{i}',])
            tempdf.insert(loc=0, column='year', value=row['year'])
            tempdf.insert(loc=1, column='quater', value=row['month']/3)
            tempdf.insert(loc=2, column='bedrooms', value=Bedrooms)
            tempdf.insert(loc=3, column='type', value=Category)
            new_df.append(list(tempdf.iloc[0]))
            
        all_df.append(new_df)
        
    if len(all_df) == 0:
            print(f'No Data Available for {Sub}')
    else:
        columns = ['year', 'quater', 'bedrooms', 'type', 'medianSoldPrice', 'numberSold',
           'highestSoldPrice', 'lowestSoldPrice', '5thPercentileSoldPrice',
           '25thPercentileSoldPrice', '75thPercentileSoldPrice',
           '95thPercentileSoldPrice', 'medianSaleListingPrice',
           'numberSaleListing', 'highestSaleListingPrice',
           'lowestSaleListingPrice', 'auctionNumberAuctioned', 'auctionNumberSold',
           'auctionNumberWithdrawn', 'daysOnMarket', 'discountPercentage',
           'medianRentListingPrice', 'numberRentListing',
           'highestRentListingPrice', 'lowestRentListingPrice']
        length = len(all_df)
        if length == 1:
            dataframe = pd.DataFrame(all_df[0], columns=columns)
        elif length == 2:
            dataframe = pd.concat([pd.DataFrame(all_df[0], columns=columns), 
                               pd.DataFrame(all_df[1], columns=columns)])
        elif length == 3:
            dataframe = pd.concat([pd.DataFrame(all_df[0], columns=columns), 
                               pd.DataFrame(all_df[1], columns=columns),
                               pd.DataFrame(all_df[2], columns=columns)])
        elif length == 4:
            dataframe = pd.concat([pd.DataFrame(all_df[0], columns=columns), 
                               pd.DataFrame(all_df[1], columns=columns),
                               pd.DataFrame(all_df[2], columns=columns),
                               pd.DataFrame(all_df[3], columns=columns)])
        elif length == 5:
            dataframe = pd.concat([pd.DataFrame(all_df[0], columns=columns), 
                               pd.DataFrame(all_df[1], columns=columns),
                               pd.DataFrame(all_df[2], columns=columns),
                               pd.DataFrame(all_df[3], columns=columns),
                               pd.DataFrame(all_df[4], columns=columns)])
    
        dataframe[['year', 'quater', 'bedrooms', 'medianSoldPrice', 'numberSold',
           'highestSoldPrice', 'lowestSoldPrice', '5thPercentileSoldPrice',
           '25thPercentileSoldPrice', '75thPercentileSoldPrice',
           '95thPercentileSoldPrice', 'medianSaleListingPrice',
           'numberSaleListing', 'highestSaleListingPrice',
           'lowestSaleListingPrice', 'auctionNumberAuctioned', 'auctionNumberSold',
           'auctionNumberWithdrawn', 'daysOnMarket', 'discountPercentage',
           'medianRentListingPrice', 'numberRentListing',
           'highestRentListingPrice', 'lowestRentListingPrice']] = dataframe[['year', 'quater', 'bedrooms', 'medianSoldPrice', 'numberSold',
           'highestSoldPrice', 'lowestSoldPrice', '5thPercentileSoldPrice',
           '25thPercentileSoldPrice', '75thPercentileSoldPrice',
           '95thPercentileSoldPrice', 'medianSaleListingPrice',
           'numberSaleListing', 'highestSaleListingPrice',
           'lowestSaleListingPrice', 'auctionNumberAuctioned', 'auctionNumberSold',
           'auctionNumberWithdrawn', 'daysOnMarket', 'discountPercentage',
           'medianRentListingPrice', 'numberRentListing',
           'highestRentListingPrice', 'lowestRentListingPrice']].apply(pd.to_numeric)
        
        return dataframe

def get_demographics(Sub, Postcode, year=2021):
    State = 'NSW'
    dem_URL = f'https://api.domain.com.au/v2/demographics/{State}/{Sub}/{Postcode}?types=AgeGroupOfPopulation%2CCountryOfBirth%2CNatureOfOccupancy%2COccupation%2CGeographicalPopulation%2CGeographicalPopulation%2CEducationAttendance%2CHousingLoanRepayment%2CMaritalStatus%2CReligion%2CTransportToWork%2CFamilyComposition%2CHouseholdIncome%2CRent%2CLabourForceStatus&year={year}'
    header = {'X-API-Key':api_key}
    response = requests.get(url = dem_URL, headers=header)
    data = response.json()
    try:
        df = pd.DataFrame(data['demographics'])
        return df
    except:
        return []


def save_performance_database(Category,set_num, maxBedrooms, num_subs = 100):
    conn = sqlite3.connect(f'{Category}_data.db')
    start = set_num*num_subs - num_subs
    end = set_num*num_subs
    suburbs = get_suburbs()
    sydney_subs = suburbs[suburbs['SA4 Name'].str.contains('Sydney - ')].reset_index(drop=True)
    subs = sydney_subs.iloc[start:end]
    for i, row in subs.iterrows():
        Sub = row['Locality']
        Postcode = row['Postcode']
        Quaters = 16
        print(f'Fetching data for {Sub} - {Postcode}')
        data = performance_data(Sub, Postcode, Quaters, maxBedrooms, Category)
        if data is None:
            continue
        else:
            data.to_sql(f'{Sub}', conn, if_exists='replace', index = False)
    conn.close()
    return print(f'Set {set_num} of {num_subs} tables saved to the database')



def save_demographic_database(set_num, num_subs = 400):
    conn = sqlite3.connect('Demographic_data.db')
    start = set_num*num_subs - num_subs
    end = set_num*num_subs
    suburbs = get_suburbs()
    sydney_subs = suburbs[suburbs['SA4 Name'].str.contains('Sydney - ')].reset_index(drop=True)
    subs = sydney_subs.iloc[start:end]

    transport_df = pd.DataFrame()
    occupation_df = pd.DataFrame()
    rent_df = pd.DataFrame()
    religion_df = pd.DataFrame()
    income_df = pd.DataFrame()
    age_df =pd.DataFrame()
    marital_df = pd.DataFrame()
    country_df = pd.DataFrame()
    edu_df = pd.DataFrame()
    occupancy_df = pd.DataFrame()
    
    for i, row in subs.iterrows():
        Sub = row['Locality']
        Postcode = row['Postcode']
        print(f'Fetching data for {Sub} - {Postcode}')
        
        data = get_demographics(Sub, Postcode)
        if len(data) == 0:
            print(f'No demographic data recieved for {Sub} - {Postcode}')
            continue
        
        if len(list(pd.DataFrame(data[data['type'] == 'TransportToWork'].
                                       iloc[0]['items'])['label'])) == 30:
              trans_cols = list(pd.DataFrame(data[data['type'] == 'TransportToWork'].
                                             iloc[0]['items'])['label'])
              temp_trans = list(pd.DataFrame(data[data['type'] == 'TransportToWork'].
                                             iloc[0]['items'])['value'])
              temp_trans = pd.DataFrame([temp_trans], columns = trans_cols)
              temp_trans.insert(loc=0, column='suburb', value=Sub)
              transport_df = pd.concat([transport_df, temp_trans], 
                                       sort = False)
        else:
            print(f'Insufficient Transport data recieved for {Sub} - {Postcode}')

        if len(list(pd.DataFrame(data[data['type'] == 'Occupation'].
                                       iloc[0]['items'])['label'])) == 9:
             occup_cols = list(pd.DataFrame(data[data['type'] == 'Occupation'].
                                            iloc[0]['items'])['label'])
             temp_occup = list(pd.DataFrame(data[data['type'] == 'Occupation'].
                                            iloc[0]['items'])['value'])
             temp_occup = pd.DataFrame([temp_occup], columns = occup_cols)
             temp_occup.insert(loc=0, column='suburb', value=Sub)
             occupation_df = pd.concat([occupation_df, temp_occup], 
                                      sort = False)
        else:
            print(f'Insufficient Occupation data recieved for {Sub} - {Postcode}')
             
        if len(list(pd.DataFrame(data[data['type'] == 'Rent'].
                                      iloc[0]['items'])['label']))==15:
             rent_cols = list(pd.DataFrame(data[data['type'] == 'Rent'].
                                           iloc[0]['items'])['label'])
             temp_rent = list(pd.DataFrame(data[data['type'] == 'Rent'].
                                           iloc[0]['items'])['value'])
             temp_rent = pd.DataFrame([temp_rent], columns = rent_cols)
             temp_rent.insert(loc=0, column='suburb', value=Sub)
             rent_df = pd.concat([rent_df, temp_rent], 
                                      sort = False)
        else:
            print(f'Insufficient Rent data recieved for {Sub} - {Postcode}')
             
        if len(list(pd.DataFrame(data[data['type'] == 'Religion'].
                                          iloc[0]['items'])['label']))==30:
            religion_cols = list(pd.DataFrame(data[data['type'] == 'Religion'].
                                              iloc[0]['items'])['label'])
            temp_religion = list(pd.DataFrame(data[data['type'] == 'Religion'].
                                              iloc[0]['items'])['value'])
            temp_religion = pd.DataFrame([temp_religion], columns = religion_cols)
            temp_religion.insert(loc=0, column='suburb', value=Sub)
            religion_df = pd.concat([religion_df, temp_religion], 
                                     sort = False)
        else:
            print(f'Insufficient Religion data recieved for {Sub} - {Postcode}')
            
        if len(list(pd.DataFrame(data[data['type'] == 'HouseholdIncome'].
                                        iloc[0]['items'])['label']))==19:
            income_cols = list(pd.DataFrame(data[data['type'] == 'HouseholdIncome'].
                                            iloc[0]['items'])['label'])
            temp_income = list(pd.DataFrame(data[data['type'] == 'HouseholdIncome'].
                                            iloc[0]['items'])['value'])
            temp_income = pd.DataFrame([temp_income], columns = income_cols)
            temp_income.insert(loc=0, column='suburb', value=Sub)
            income_df =  pd.concat([income_df, temp_income], 
                                     sort = False)
        else:
            print(f'Insufficient Income data recieved for {Sub} - {Postcode}')
            
        if len(list(pd.DataFrame(data[data['type'] == 'AgeGroupOfPopulation'].
                                     iloc[0]['items'])['label']))==5:
            age_cols = list(pd.DataFrame(data[data['type'] == 'AgeGroupOfPopulation'].
                                         iloc[0]['items'])['label'])
            temp_age = list(pd.DataFrame(data[data['type'] == 'AgeGroupOfPopulation'].
                                         iloc[0]['items'])['value'])
            temp_age = pd.DataFrame([temp_age], columns = age_cols)
            temp_age.insert(loc=0, column='suburb', value=Sub)
            age_df =  pd.concat([age_df, temp_age], 
                                     sort = False)
        else:
            print(f'Insufficient Age data recieved for {Sub} - {Postcode}')
            
        if len(list(pd.DataFrame(data[data['type'] == 'MaritalStatus'].
                                       iloc[0]['items'])['label'])) == 5:
              marital_cols = list(pd.DataFrame(data[data['type'] == 'MaritalStatus'].
                                             iloc[0]['items'])['label'])
              temp_marital = list(pd.DataFrame(data[data['type'] == 'MaritalStatus'].
                                             iloc[0]['items'])['value'])
              temp_marital = pd.DataFrame([temp_marital], columns = marital_cols)
              temp_marital.insert(loc=0, column='suburb', value=Sub)
              marital_df = pd.concat([marital_df, temp_marital], 
                                       sort = False)
        else:
            print(f'Insufficient Marital Status data recieved for {Sub} - {Postcode}')
            
        if len(list(pd.DataFrame(data[data['type'] == 'CountryOfBirth'].
                                       iloc[0]['items'])['label'])) == 52:
              country_cols = list(pd.DataFrame(data[data['type'] == 'CountryOfBirth'].
                                             iloc[0]['items'])['label'])
              temp_country = list(pd.DataFrame(data[data['type'] == 'CountryOfBirth'].
                                             iloc[0]['items'])['value'])
              temp_country = pd.DataFrame([temp_country], columns = country_cols)
              temp_country.insert(loc=0, column='suburb', value=Sub)
              country_df = pd.concat([country_df, temp_country], 
                                       sort = False)
        else:
            print(f'Insufficient Country of Birth data recieved for {Sub} - {Postcode}')
            
        if len(list(pd.DataFrame(data[data['type'] == 'EducationAttendance'].
                                       iloc[0]['items'])['label'])) == 7:
              education_cols = list(pd.DataFrame(data[data['type'] == 'EducationAttendance'].
                                             iloc[0]['items'])['label'])
              temp_edu = list(pd.DataFrame(data[data['type'] == 'EducationAttendance'].
                                             iloc[0]['items'])['value'])
              temp_edu = pd.DataFrame([temp_edu], columns = education_cols)
              temp_edu.insert(loc=0, column='suburb', value=Sub)
              edu_df =  pd.concat([edu_df, temp_edu], 
                                       sort = False)
        else:
            print(f'Insufficient Education data recieved for {Sub} - {Postcode}')
            
        if len(list(pd.DataFrame(data[data['type'] == 'NatureOfOccupancy'].
                                       iloc[0]['items'])['label'])) == 5:
              occupancy_cols = list(pd.DataFrame(data[data['type'] == 'NatureOfOccupancy'].
                                             iloc[0]['items'])['label'])
              temp_occupancy = list(pd.DataFrame(data[data['type'] == 'NatureOfOccupancy'].
                                             iloc[0]['items'])['value'])
              temp_occupancy = pd.DataFrame([temp_occupancy], columns = occupancy_cols)
              temp_occupancy.insert(loc=0, column='suburb', value=Sub)
              occupancy_df = pd.concat([occupancy_df, temp_occupancy], 
                                       sort = False)
        else:
            print(f'Insufficient Occupancy data recieved for {Sub} - {Postcode}')
    
    if set_num == 1:
        exist = 'replace'
    else:
        exist = 'append'
    
    transport_df.to_sql('Transport', conn, if_exists=exist, index = False)
    occupation_df.to_sql('Occupation', conn, if_exists=exist, index = False)
    rent_df.to_sql('Rent', conn, if_exists=exist, index = False)
    religion_df.to_sql('Religion', conn, if_exists=exist, index = False)
    income_df.to_sql('Income', conn, if_exists=exist, index = False)
    age_df.to_sql('Age', conn, if_exists=exist, index = False)
    marital_df.to_sql('MaritalStatus', conn, if_exists=exist, index = False)
    country_df.to_sql('CountryOfBirth', conn, if_exists=exist, index = False)
    edu_df.to_sql('Education', conn, if_exists=exist, index = False)
    occupancy_df.to_sql('Occupancy', conn, if_exists=exist, index = False)
    conn.close()
    return print(f'Set {set_num} of {num_subs} suburbs saved to the database')

