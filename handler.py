#-*- coding: utf-8 -*-
"""
@author: MD.Nazmuddoha Ansary,Omer Sayem
"""
# ---------------------------------------------------------
from fbads import create_facebook_ad
from gads import get_google_country_codes,create_google_ad

import json
import pandas as pd
import os
# ---------------------------------------------------------
'''
    This is the connector script for facebook and google                    
'''
# path of location mapper
MAP_CSV     =   os.path.join(os.getcwd(),'resources','map.csv')
# path for google yaml
GOOGLE_YAML =  os.path.join(os.getcwd(),'resources','google-ads.yaml')

# ---------------------------------------------------------
def split_budget(budget):
    '''
        splits budget as per channels
        **ONLY AVAILABLE FOR FACEBOOK NOW**
    '''
    # convert budget into facebook format
    facebook_budget =   budget/2
    google_budget   =   budget/2
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
                        geo_location:   specified geolocation                  (UI)     <DICTIONARY>
                    }
        DATA EXPANSION

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


        date and time : Time is in 24 Hour format Example: "3-12-2020,23:35"--> indicates 11:35 PM of 3rd December,2020     
        
        
        facebook:   Either set to "None" if not selected 
                    or must be a dictionary of the following variables
                    {
                        business_id :   ad account of user      <STRING>,
                        page_id     :   page id of  user        <STRING>,
                        access_token:   facebook app token      <STRING>,
                        creative_id :   id ofad creative created<STRING>,
                    }
        
                    
        
        google  :   Either set to "None" if not selected 
                    or must be a dictionary of the following variables
                    {
                        customer_id     :   customer id to create ad        <STRING>,
                        customer_data   :   customer basic data             <DICTIONARY>
                        ad_data         :   needed  ad data                 <DICTIONARY>
                    }
            customer_data:
            {
                business_image_url      :   business image url              <STRING>
                business_image_dim      :   dimension for business image    <INT>
                website                 :   the website to redirect         <STRING> 
                business_name           :   name of the business            <STRING>
                
            }
            ad_data:
            {
                ad_image_url                    :   ad image url                    <STRING>
                ad_img_height                   :   height of ad image              <INT>
                ad_img_width                    :   width of ad image               <INT>
                headline_text                   :   text for the headline           <STRING>       
                long_headline_text              :   secondary headline              <STRING>
                description_text                :   description text                <STRING>
                
            }

               
    '''
    
    # base data
    budget      =   data['budget']
    start_date  =   data['start_date']
    end_date    =   data['end_date']
    objective   =   data['objective']
    channels    =   data['channels'][0]
    geo_location=   data['geo_location']
    # channels
    facebook    =   channels['facebook']
    google_data =   channels['google']
    # budget 
    facebook_budget,google_budget=split_budget(budget)
    
    # facebook variables
    business_id = facebook['business_id'] 
    page_id     = facebook['page_id']                          # this is a future need (Targeting level)
    access_token= facebook['access_token']
    creative_id = facebook['creative_id']
    # google variables
    location_ids        =   get_google_country_codes(geo_location["countries"],MAP_CSV)
    customer_id         =   google_data['customer_id']
    customer_data       =   google_data['customer_data']
    ad_data             =   google_data['ad_data']
    # customer
    website             =   customer_data['website']
    business_image_url  =   customer_data['business_image_url']
    business_image_dim  =   customer_data['business_image_dim']
    business_name       =   customer_data['business_name']
    # ad 
    ad_image_url        =   ad_data['ad_image_url']
    ad_img_height       =   ad_data['ad_img_height']
    ad_img_width        =   ad_data['ad_img_width']
    headline_text       =   ad_data['headline_text']
    long_headline_text  =   ad_data['long_headline_text']
    description_text    =   ad_data['description_text']
    
    
    # create facebook ad
    facebook_ad=create_facebook_ad(access_token=access_token, 
                       business_id=business_id,
                       start_date=start_date,
                       end_date=end_date,
                       campaign_budget=facebook_budget,
                       campaign_objective=objective,
                       geo_locations=geo_location,
                       creative_id=creative_id,
                       status=status) 
    # create google ad 
    google_ad=create_google_ad(customer_id,
                    GOOGLE_YAML,
                    google_budget,
                    objective,
                    start_date,
                    end_date,
                    location_ids,
                    ad_image_url,
                    ad_img_height,
                    ad_img_width,
                    business_image_url,
                    business_image_dim,
                    website,
                    headline_text,
                    long_headline_text,
                    description_text,
                    business_name)
    body={"facebook":facebook_ad,"google":google_ad}
    return body

def autoad(event, context):



    data = event['body']
    # testing    
    body=process_data(data=data)


    
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

if __name__=='__main__':
    data={  "budget"     : 100,
            "start_date"  : "27-3-2021,1:30",
            "end_date"    : "31-3-2021,23:30",
            "objective"   : "Reach",  
            "geo_location": {
                                "countries":["BD","US"]
                            },

            "channels"    :[{"facebook":{
                                            "business_id" :   "760249887886995",
                                            "page_id"     :   "Markopoloai",
                                            "access_token":   "",
                                            "creative_id" :   "23846237956520529",
                                            
                                        },
                             "google"  :{
                                            "customer_id"       :"2420782878",
                                            "customer_data"     :{
                                                                    
                                                                    "business_image_url"      :   "https://goo.gl/mtt54n",
                                                                    "business_image_dim"      :   512,
                                                                    "website"                 :   "https://www.markopolo.ai/", 
                                                                    "business_name"           :   "Markopoloai"
                                                                    
            
                                                                },   

                                            "ad_data"           :{
                                                                        "ad_image_url"                    :   "https://goo.gl/3b9Wfh",
                                                                        "ad_img_height"                   :   315,
                                                                        "ad_img_width"                    :   600,
                                                                        "headline_text"                   :   "headline",                 
                                                                        "long_headline_text"              :   "secondary headline",              
                                                                        "description_text"                :   "description text"                
                                                                }

                                    }          
                            }]        
    }
    _=process_data(data=data)