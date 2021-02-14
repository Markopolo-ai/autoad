#-*- coding: utf-8 -*-
"""
@author: MD.Nazmuddoha Ansary
"""
# ---------------------------------------------------------
# -------------------imports------------------------------
# ---------------------------------------------------------
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet
from facebook_business.api import FacebookAdsApi
import requests
from datetime import datetime
import requests
# ---------------------------------------------------------
'''
    This is the script for facebook adsets                         
'''
# ---------------------------------------------------------
#-----------Globals---------------------------------------
# ---------------------------------------------------------
CURRENCY_API_KEY='1e852e43de592de222e1'
CURRENCY_BASE_URL='https://free.currconv.com/api/v7'

UI_OBJECTIVES =["Sales"          ,"Reach"          ,"Lead Generation","Video Promotion"  ,"App Install"    ,"Store Visit"]
FB_OBJECTIVES =['POST_ENGAGEMENT','POST_ENGAGEMENT','POST_ENGAGEMENT','POST_ENGAGEMENT'  ,'POST_ENGAGEMENT','POST_ENGAGEMENT']
GOALS         =['POST_ENGAGEMENT','POST_ENGAGEMENT','POST_ENGAGEMENT','POST_ENGAGEMENT'  ,'POST_ENGAGEMENT','POST_ENGAGEMENT']
BILLING_EVENTS=['IMPRESSIONS'    ,'IMPRESSIONS'    ,'IMPRESSIONS'    ,'IMPRESSIONS'      ,'IMPRESSIONS'    ,'IMPRESSIONS']

# ---------------------------------------------------------
def init_api(access_token):
    '''
        initiates the facebook api
        args:
            access_token    :   long-lived access token (provided from backend) <STRING>
    '''
    FacebookAdsApi.init(access_token=access_token)
# ---------------------------------------------------------
def create_campaign(business_id,
                    campaign_objective,
                    start_date,
                    end_date,
                    status,
                    campaign_budget,
                    keyword=None):
    '''
        creates a campaign based on objective
        args:
            business_id         :   business account id of client       (provided from backend) <STRING>
            campaign_objective  :   objective of the campaign           (provided from backend) <STRING>
            start_date          :   start date of the campaign          (provided from backend) <STRING> [d-m-y,H:M]
            end_date            :   end date of the campaign            (provided from backend) <STRING> [d-m-y,H:M]
            status              :   for running the campaign            (PASSED FROM CONNECTOR) <STRING> 
            campaign_budget     :   the facebook campaign budget        (provided from backend) <STRING>
            keyword             :   specific keyword for the campaign   (if given)
    '''
    BID         =   'LOWEST_COST_WITHOUT_CAP'
    # get index
    idx=UI_OBJECTIVES.index(campaign_objective)
    # create objective
    fb_objective=FB_OBJECTIVES[idx]
    # request setup
    fields=[]
    params={ 'name': f"CBO_{campaign_objective}|{fb_objective}|{start_date}|{end_date}",
             'objective':fb_objective,
             'lifetime_budget':campaign_budget,
             'bid_strategy':'LOWEST_COST_WITHOUT_CAP',
             'status':status,
             'special_ad_categories':[]}
    # create
    campaign_id=AdAccount(f"act_{business_id}").create_campaign(fields=fields,params=params)["id"]
    return campaign_id

# ---------------------------------------------------------

def create_preset(campaign_objective):
    '''
        creates preset based on objective **ONLY AVAILABLE FOR REACH NOW AT THE MOMENT**
        args:
            campaign_objective  :   objective of the campaign           (provided from backend) <STRING>
    '''
    #campaign_objective
    idx=UI_OBJECTIVES.index(campaign_objective)
    class PRESET:
        BILL_EVENT  =   BILLING_EVENTS[idx]
        GOAL        =   GOALS[idx]
    return PRESET

    
# ---------------------------------------------------------
def create_targeting(geo_locations,
                     ad_type,
                     lowest=13,
                     highest=65,
                     ab_test=True):
    '''
        creates the targeting
        args:
            geo_locations       :   location to serve the ad            (provided from backend) <DICTIONARY>
            ad_type             :   control or treatment                (automl selection)      <STRING>
            lowest              :   lowest age to show add              (Facebook Policy)
            highest             :   highest age to show add             (Facebook Policy)
            ab_test             :   flag to do ab_testing               (provided from backend) <BOOLEAN>
              
    '''
    # determine cutoff
    cutoff=int((highest-lowest)/2)+lowest
    # set targeting
    if ab_test:
        if ad_type=='control':
            return {
                    'age_min':lowest,                                        
                    'age_max':cutoff,
                    'geo_locations':geo_locations,
                    'facebook_positions':['feed']
                    }
        else:
            return {
                    'age_min':cutoff+1,                                        
                    'age_max':highest,
                    'geo_locations':geo_locations,
                    'facebook_positions':['feed']
                    }
    else:
        return {
                'geo_locations':geo_locations,
                'facebook_positions':['feed']
                }




# ---------------------------------------------------------
def create_adset(business_id,
                 campaign_id,
                 adset_name,
                 PRESET,
                 targeting,
                 status,
                 start_date,
                 end_date):
                 
    '''
        creates an addset 
        args:
            business_id         :   business account id of client       (provided from backend) <STRING>
            campaign_id         :   campaign id the desired campaihn    (provided from backend) <STRING>
            start_date          :   start date of the campaign          (provided from backend) <STRING> [d-m-y,H:M]
            end_date            :   end date of the campaign            (provided from backend) <STRING> [d-m-y,H:M]
            adset_name          :   name of the adset                   (automl selection)      <STRING>
            PRESET              :   class for preset values             (automl selection)      <CLASS>
            targeting           :   targeting dictionary                (automl selection)      <DICTIONARY>
            status              :   for running the campaign            (PASSED FROM CONNECTOR) <STRING>
    '''

    fields = []
    params = {
                'name'              :   f"{adset_name}_{start_date}_{end_date}",
                'start_time'        :   datetime.strptime(start_date,'%d-%m-%Y,%H:%M').strftime("%Y-%m-%dT%H:%M:%S-0000") ,
                'end_time'          :   datetime.strptime(end_date,'%d-%m-%Y,%H:%M').strftime("%Y-%m-%dT%H:%M:%S-0000"),
                'campaign_id'       :   campaign_id,
                'billing_event'     :   PRESET.BILL_EVENT,
                'optimization_goal' :   PRESET.GOAL,
                'targeting'         :   targeting,
                'status'            :   status
            }
    
    return AdAccount(f"act_{business_id}").create_ad_set(fields=fields,params=params)['id']
# ---------------------------------------------------------
def create_ad(business_id,
              creative_id,
              ad_type,
              adset_id,
              status):
    '''
        creates ad based on creative id
        args:
            business_id         :   business account id of client       (provided from backend) <STRING>
            creative_id         :   ad creative id selected by client   (provided from backend) <STRING>
            ad_type             :   type of ad                          (automl selection)      <STRING>
            adset_id            :   adset_id                            (automl selection)      <STRING>
            status              :   for running the campaign            (PASSED FROM CONNECTOR) <STRING> 
        
    '''
    fields = []
    params = {
    'name'    : f'{ad_type}',
    'adset_id': adset_id,
    'creative': {'creative_id':creative_id},
    'status': status
    }
    return AdAccount(f"act_{business_id}").create_ad(fields=fields,params=params)
# ---------------------------------------------------------

def create_facebook_ad( access_token,
                        business_id,
                        start_date,
                        end_date,
                        campaign_budget,
                        campaign_objective,
                        geo_locations,
                        creative_id,
                        status):
    '''
        creates an a/b testing study
    
        args:
            access_token        :   long-lived access token             (provided from backend) <STRING>
            business_id         :   business account id of client       (provided from backend) <STRING>
            start_date          :   start date of the campaign          (provided from backend) <STRING> [d-m-y,H:M]
            end_date            :   end date of the campaign            (provided from backend) <STRING> [d-m-y,H:M]
            campaign_budget     :   the facebook campaign budget        (provided from backend) <STRING>
            campaign_objective  :   the objective chosen at UI          (provided from backend) <STRING>
            geo_locations       :   location to serve the ad            (provided from backend) <DICTIONARY>
            creative_id         :   ad creative id                      (provided from backend) <STRING>
            status              :   for running the campaign            (PASSED FROM CONNECTOR) <STRING>     
    '''
    # api init
    init_api(access_token)
    
    # budget
    #campaign_budget=campaign_budget*100
    account = AdAccount(f'act_{business_id}')
    currency=account.api_get(fields=["currency"])["currency"]
    print("Currency:",currency)
    Q_WORD=f"USD_{currency}"
    URL=f"{CURRENCY_BASE_URL}/convert?q={Q_WORD}&compact=ultra&apiKey={CURRENCY_API_KEY}"
    rate=float(requests.get(URL).json()[Q_WORD])
    campaign_budget=int(rate*campaign_budget)*100
    print("Budget:",campaign_budget/100,currency)
    
    

    # create campaign
    campaign_id=create_campaign(business_id=business_id,
                                campaign_objective=campaign_objective,
                                start_date=start_date,
                                end_date=end_date,
                                status=status,
                                campaign_budget=campaign_budget)

    print("LOG:Campaign Created:",campaign_id)
    # PRESET
    PRESET=create_preset(campaign_objective)
    
    # adset
    adset_name="creative"    
    # get targeting
    targeting=create_targeting(geo_locations=geo_locations,
                               ad_type=adset_name,
                               ab_test=False)     
    # create adset
    adset_id=create_adset(business_id=business_id,
                        campaign_id=campaign_id,
                        adset_name=adset_name,
                        PRESET=PRESET,
                        targeting=targeting,
                        status=status,
                        start_date=start_date,
                        end_date=end_date)

    print("LOG:Adset Created:",adset_id)
    
    # create ad
    ad_id=create_ad(business_id=business_id,
                    creative_id=creative_id,
                    ad_type=adset_name,
                    adset_id=adset_id,
                    status=status)           
    
    print("LOG:Ad Created:",ad_id['id'])
    
    return  {
                    "budget":f"{campaign_budget/100} {currency}",
                    "campaign_id":campaign_id,
                    "adset_id":adset_id,
                    "ad_id":ad_id,
                    "creative_id":creative_id
            }