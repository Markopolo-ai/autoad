#-*- coding: utf-8 -*-
"""
@author: MD.Nazmuddoha Ansary,Omer Sayem
"""
# ---------------------------------------------------------
from fbads import create_facebook_ad
import json
# ---------------------------------------------------------
'''
    This is the connector script for facebook and google                    
'''
# ---------------------------------------------------------
def split_budget(budget):
    '''
        splits budget as per channels
        **ONLY AVAILABLE FOR FACEBOOK NOW**
    '''
    # convert budget into facebook format
    facebook_budget =   budget
    google_budget   =   0
    return facebook_budget,google_budget
# ---------------------------------------------------------
def process_data(data,status="PAUSED"):
    '''
        TODO: Add error handling
        this receives the data from backend for further processing
        args:
            data    :      The passed json data from backend
        
        data format:{
                        budget      :   the amount of budget specified by user (UI)     <int>,
                        start_date  :   the start date of the campaign by user (UI)     <STRING>[d-m-Y,H:M],
                        end_date    :   the end date of the campaign by user   (UI)     <STRING>[d-m-Y,H:M],
                        objective   :   the objective of the campaign given    (UI)     <STRING>,
                        channels    :   the channels to divide the budget into (UI)     <LIST OF DICTIONARY>
                    }
        DATA EXPANSION
        date and time : Time is in 24 Hour format Example: "3-12-2020,23:35"--> indicates 11:35 PM of 3rd December,2020     
        facebook:   Either set to "None" if not selected 
                    or must be a dictionary of the following variables
                    {
                        business_id :   ad account of user      <STRING>,
                        page_id     :   page id of  user        <STRING>,
                        access_token:   facebook app token      <STRING>,
                        creative_id :   id ofad creative created<STRING>,
                        geo_location:   specified geolocation   <DICTIONARY>
                    }
        
                    geo_location: must contain atleast the 'countries' list
                        format:
                                {
                                    'countries':['XX','XX',.....],                  # XX        ->   Two letter country codes as per fb-sdk
                                    'regions':[{'key':'XXXX'},{'key':'XXXX'}],      # XXXX      ->   Region Codes as per fb-sdk
                                    'cities':[{'key':'XXXXXXX',                     # XXXXXXX   ->   city codes as per fb-sdk            
                                                'radius':I,                         # I         ->   int value of radius                       
                                                'distance_unit':'<UNIT>'},          # UNIT      ->   valid units as per fb-sdk
                                              {'key':'XXXXXXX',
                                                'radius':I,
                                                'distance_unit':'<UNIT>'},
                                                ]
                                } 
        
        google  : to be implemented,set as None for now
               
    '''
    
    # base data
    budget      =   data['budget']
    start_date  =   data['start_date']
    end_date    =   data['end_date']
    objective   =   data['objective']
    channels    =   data['channels'][0]
    facebook    =   channels['facebook']
    # budget 
    facebook_budget,google_budget=split_budget(budget)
    # facebook variables
    business_id = facebook['business_id'] 
    page_id     = facebook['page_id']                          # this is a future need (Targeting level)
    access_token= facebook['access_token']
    creative_id = facebook['creative_id']
    geo_location= facebook['geo_location']
    # create facebook ad
    create_facebook_ad(access_token=access_token, 
                       business_id=business_id,
                       start_date=start_date,
                       end_date=end_date,
                       campaign_budget=facebook_budget,
                       campaign_objective=objective,
                       geo_locations=geo_location,
                       creative_id=creative_id,
                       status=status) 



def autoad(event, context):


    '''
        an example data
    
    {"budget": 20,
    "start_date"  : "27-1-2021,1:30",
    "end_date"    : "28-1-2021,23:30",
    "objective"   : "Reach",  
    "channels"    :[{"facebook":{
                                    "business_id" :   "760249887886995",
                                    "page_id"     :   "Markopoloai",
                                    "access_token":   "",
                                    "creative_id" :   "23846237956520529",
                                    "geo_location": {
                                                    "countries":["BD"]
                                                    }
                                }
                    }
                    ]        
    }
    '''
    data = event['body']
    # testing    
    process_data(data=data)


    body = {
        "message": "ad created!",
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
