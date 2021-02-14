#-*- coding: utf-8 -*-
"""
@author: MD.Nazmuddoha Ansary
"""
# ---------------------------------------------------------
# -------------------imports------------------------------
# ---------------------------------------------------------
from datetime import datetime
import pandas as pd
import requests
import sys
from uuid import uuid4

from google.ads.google_ads.client import GoogleAdsClient
from google.ads.google_ads.errors import GoogleAdsException

# ---------------------------------------------------------
'''
    This is the script for google adsets                         
'''
# ---------------------------------------------------------
#-----------Globals---------------------------------------
# ---------------------------------------------------------
_DATE_FORMAT = "%Y%m%d"
# ---------------------------------------------------------
#-----------helpers---------------------------------------
# ---------------------------------------------------------
def get_google_country_codes(country_list,mapper_csv_path):
    '''
        maps location codes to google ids
        args:
            country_list    =   list of countries to map    <LIST>
            mapper_csv_path =   csv file of code and maps   <STRING>
        returns:
            location_ids    =   list of location ids        <LIST>
    '''
    # read mappers
    df=pd.read_csv(mapper_csv_path)
    return [df['id'].loc[df['code']==country].tolist()[0] for country in country_list]

# ---------------------------------------------------------
def upload_image_asset( client, 
                        customer_id, 
                        image_url, 
                        image_width, 
                        image_height):
    '''
        uploads image to google
        args:
            client          =   client created from yaml        <CLIENT OBJECT>
            customer_id     =   customer id to create ad        <STRING>
            image_url       =   url of the image to create ad   <STRING>
            image_width     =   width of the image              <INT>
            image_height    =   height of the image             <INT>
        return:
            asset_id        =   id of the created asset         
    '''                    
    # Download image from URL
    image_content = requests.get(image_url).content
    # service
    asset_operation = client.get_type("AssetOperation", version="v6")
    # mode
    asset = asset_operation.create
    # service
    asset_type_enum = client.get_type("AssetTypeEnum", version="v6")
    # type
    asset.type = asset_type_enum.IMAGE
    # asset
    image_asset = asset.image_asset
    # data
    image_asset.data = image_content
    # size
    image_asset.file_size = len(image_content)
    # mome
    image_asset.mime_type = client.get_type("MimeTypeEnum").IMAGE_JPEG
    # width
    image_asset.full_size.width_pixels = image_width
    # width
    image_asset.full_size.height_pixels = image_height
    # url
    image_asset.full_size.url = image_url
    # service
    asset_service = client.get_service("AssetService", version="v6")
    # content
    content_type_enum = client.get_type("ResponseContentTypeEnum", version="v6")

    try:
        mutate_asset_response = asset_service.mutate_assets(customer_id,[asset_operation],response_content_type=content_type_enum.MUTABLE_RESOURCE,)
        return mutate_asset_response.results[0].asset.id
    except GoogleAdsException as ex:
        _handle_google_ads_exception(ex)
       
# ---------------------------------------------------------
def _handle_google_ads_exception(exception):
    """
        Prints the details of a GoogleAdsException object.
        Args:
            exception: an instance of GoogleAdsException.
    """
    print(
        f'Request with ID "{exception.request_id}" failed with status '
        f'"{exception.error.code().name}" and includes the following errors:'
    )
    for error in exception.failure.errors:
        print(f'\tError with message "{error.message}".')
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"\t\tOn field: {field_path_element.field_name}")
    sys.exit(1)

# ---------------------------------------------------------
#-----------ad functions---------------------------------------
# ---------------------------------------------------------
# budget resource
def create_budget(client, customer_id,budget,campaign_objective):
    '''
        creates budget resource
        args:
            client              =   client created from yaml        <CLIENT OBJECT>
            customer_id         =   customer id to create ad        <STRING>
            budget              =   budget for the campaign         <INT> (USD)
            campaign_objective  =   objective of the campaign       <STRING>
            
        returns:
            budget_resource_name
        
    '''
    # service
    campaign_budget_operation = client.get_type("CampaignBudgetOperation", version="v6")
    # mode
    campaign_budget = campaign_budget_operation.create
    # name of campaign
    campaign_budget.name = f'{campaign_objective}#{uuid4()}'
    # method of delivery
    campaign_budget.delivery_method = client.get_type("BudgetDeliveryMethodEnum").STANDARD
    # set budget
    campaign_budget.amount_micros = int(budget*1000000) # fix as micros
    # service
    campaign_budget_service = client.get_service("CampaignBudgetService", version="v6")
    # resource name
    try:
        campaign_budget_response = campaign_budget_service.mutate_campaign_budgets(customer_id, [campaign_budget_operation])
        return campaign_budget_response.results[0].resource_name
    except GoogleAdsException as ex:
        _handle_google_ads_exception(ex)

# smart display campaign
def create_smart_display_campaign(client, 
                                  customer_id, 
                                  budget_resource_name,
                                  campaign_objective,
                                  start_date,
                                  end_date):
    '''
        creates smart display campaign
        args:
            client              =   client created from yaml        <CLIENT OBJECT>
            customer_id         =   customer id to create ad        <STRING>
            budget_resource_name=   budget resource name            <STRING>
            campaign_objective  =   objective of the campaign       <STRING>
            start_date          =   start date of the campaign      <STRING> [d-m-y,H:M]
            end_date            =   end date of the campaign        <STRING> [d-m-y,H:M]
            
            
        returns:
            campaign_resource_name
    '''
    # service    
    campaign_operation = client.get_type("CampaignOperation", version="v6")
    # mode
    campaign = campaign_operation.create
    # name
    campaign.name = f'{campaign_objective}#{uuid4()}'
    # channels to advertise to
    advertising_channel_type_enum = client.get_type("AdvertisingChannelTypeEnum", version="v6")
    # set type to display
    campaign.advertising_channel_type = advertising_channel_type_enum.DISPLAY
    # set sub-type
    advertising_channel_sub_type_enum = client.get_type("AdvertisingChannelSubTypeEnum", version="v6")
    # Smart Display campaign requires the advertising_channel_sub_type as
    # "DISPLAY_SMART_CAMPAIGN".
    campaign.advertising_channel_sub_type = (advertising_channel_sub_type_enum.DISPLAY_SMART_CAMPAIGN)
    campaign_status_enum = client.get_type("CampaignStatusEnum", version="v6")
    # create paused
    campaign.status = campaign_status_enum.PAUSED # paused campaign
    # Smart Display campaign requires the TargetCpa bidding strategy.
    campaign.target_cpa.target_cpa_micros = 5000000 # 5 dollars (average CPA)
    campaign.campaign_budget = budget_resource_name
    
    # Optional: Set the start and end date.
    campaign.start_date = datetime.strptime(start_date,'%d-%m-%Y,%H:%M').strftime(_DATE_FORMAT)
    campaign.end_date   = datetime.strptime(end_date,'%d-%m-%Y,%H:%M').strftime(_DATE_FORMAT)
    # service
    campaign_service = client.get_service("CampaignService", version="v6")

    try:
        campaign_response = campaign_service.mutate_campaigns(customer_id, [campaign_operation])
        return campaign_response.results[0].resource_name

    except GoogleAdsException as ex:
        _handle_google_ads_exception(ex)
# smart display campaign

def set_campaign_targeting_criteria(client, 
                                    customer_id, 
                                    campaign_resource_name,
                                    location_ids):

    """
        Sets campaign targeting criteria for a given campaign.
        args:
            client                  =   client created from yaml        <CLIENT OBJECT>
            customer_id             =   customer id to create ad        <STRING>
            campaign_resource_name  =   budget resource name            <STRING>
            location_ids            =   geo location codes              <LIST>

    """
    # services
    campaign_criterion_service = client.get_service("CampaignCriterionService", version="v6")

    geo_target_constant_service = client.get_service("GeoTargetConstantService", version="v6")
    
    language_constant_service = client.get_service("LanguageConstantService", version="v6")

    location_type = client.get_type("CriterionTypeEnum", version="v6").LOCATION
    
    language_type = client.get_type("CriterionTypeEnum", version="v6").LANGUAGE

    campaign_criterion_operations = []
    # Creates the location campaign criteria.
    # Besides using location_id, you can also search by location names from
    # GeoTargetConstantService.suggest_geo_target_constants() and directly
    # apply GeoTargetConstant.resource_name here. An example can be found
    # in targeting/get_geo_target_constant_by_names.py.
    
    for location_id in location_ids:  
        campaign_criterion_operation = client.get_type("CampaignCriterionOperation", version="v6")
        campaign_criterion = campaign_criterion_operation.create
        campaign_criterion.campaign = campaign_resource_name
        campaign_criterion.type = location_type
        campaign_criterion.location.geo_target_constant = geo_target_constant_service.geo_target_constant_path(location_id)
        campaign_criterion_operations.append(campaign_criterion_operation)

    # Creates the language campaign criteria.
    for language_id in ["1000"]:  # English  
        campaign_criterion_operation = client.get_type("CampaignCriterionOperation", version="v6")
        campaign_criterion = campaign_criterion_operation.create
        campaign_criterion.campaign = campaign_resource_name
        campaign_criterion.type = language_type
        campaign_criterion.language.language_constant = language_constant_service.language_constant_path(language_id)
        campaign_criterion_operations.append(campaign_criterion_operation)

    # Submits the criteria operations.
    for row in campaign_criterion_service.mutate_campaign_criteria(customer_id, campaign_criterion_operations).results:
        print(f"Created Campaign Criteria with resource name:{row.resource_name}")

# ---------------------------------------------------------        
# create ad group
def create_ad_group(client, 
                    customer_id, 
                    campaign_resource_name,
                    campaign_objective):
    '''
        creates ad group
        args:
            client                  =   client created from yaml        <CLIENT OBJECT>
            customer_id             =   customer id to create ad        <STRING>
            campaign_resource_name  =   budget resource name            <STRING>
            campaign_objective      =   objective of the campaign       <STRING>
            
        returns:
            campaign_resource_name
    '''
    # service
    ad_group_operation = client.get_type("AdGroupOperation", version="v6")
    # mode
    ad_group = ad_group_operation.create
    # name
    ad_group.name = f'{campaign_objective}#{uuid4()}'
    # service
    ad_group_status_enum = client.get_type("AdGroupStatusEnum", version="v6")
    # status
    ad_group.status = ad_group_status_enum.PAUSED
    # campaign
    ad_group.campaign = campaign_resource_name
    # service
    ad_group_service = client.get_service("AdGroupService", version="v6")

    try:
        ad_group_response = ad_group_service.mutate_ad_groups(customer_id, [ad_group_operation])
        return ad_group_response.results[0].resource_name
    except GoogleAdsException as ex:
        _handle_google_ads_exception(ex)
# ---------------------------------------------------------        
# create ad 
def create_ad(client,
             customer_id,
             ad_group_resource_name,
             website,
             headline_text,
             long_headline_text,
             description_text,
             business_name,
             marketing_image_asset_id,
             square_marketing_image_asset_id):
    '''
        creates ad 
        args:
            client                          =   client created from yaml        <CLIENT OBJECT>
            customer_id                     =   customer id to create ad        <STRING>
            ad_group_resource_name          =   budget resource name            <STRING>
            website                         =   the website to redirect         <STRING> 
            headline_text                   =   text for the headline           <STRING>       
            long_headline_text              =   secondary headline              <STRING>
            description_text                =   description text                <STRING>
            business_name                   =   name of the business           <STRING>
            marketing_image_asset_id        =   ad image asset id               <STRING>
            square_marketing_image_asset_id =   business image asset id         <STRING>
            
        returns:
            ad resource id        
    '''
    # service
    ad_group_ad_operation = client.get_type("AdGroupAdOperation", version="v6")
    # mode
    ad_group_ad = ad_group_ad_operation.create
    # resource
    ad_group_ad.ad_group = ad_group_resource_name
    # status
    ad_group_ad.status = client.get_type("AdGroupAdStatusEnum", version="v6").PAUSED
    # ad
    ad = ad_group_ad.ad
    # website
    ad.final_urls.append(website)
    # make responsive
    responsive_display_ad = ad.responsive_display_ad
    # headline
    headline = responsive_display_ad.headlines.add()
    headline.text = headline_text
    # long headline
    responsive_display_ad.long_headline.text = long_headline_text
    # description
    description = responsive_display_ad.descriptions.add()
    description.text = description_text
    responsive_display_ad.business_name = business_name
    # service
    asset_service = client.get_service("AssetService", version="v6")
    # ad image
    marketing_image = responsive_display_ad.marketing_images.add()
    marketing_image.asset = asset_service.asset_path(customer_id, marketing_image_asset_id)
    # business image
    square_marketing_image = responsive_display_ad.square_marketing_images.add()
    square_marketing_image.asset = asset_service.asset_path(customer_id, square_marketing_image_asset_id)
    # service
    ad_group_ad_service = client.get_service("AdGroupAdService", version="v6")

    try:
        ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(customer_id, [ad_group_ad_operation])
        return ad_group_ad_response.results[0].resource_name
    except GoogleAdsException as ex:
        _handle_google_ads_exception(ex)
        

def create_google_ad(customer_id,
                    google_yaml,
                    budget,
                    campaign_objective,
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
                    business_name):
    '''
        creates a smart responsive google ad
        args:
                customer_id                     =   customer id to create ad        <STRING>
                google_yaml                     =   yaml file location              <STRING>
                budget                          =   budget for the campaign         <INT> (USD)
                campaign_objective              =   objective of the campaign       <STRING>
                start_date                      =   start date of the campaign      <STRING> [d-m-y,H:M]
                end_date                        =   end date of the campaign        <STRING> [d-m-y,H:M]
                location_ids                    =   geo location codes              <LIST>
                business_image_url              =   business image url             <STRING>
                ad_image_url                    =   ad image url                    <STRING>
                business_image_dim             =   dimension for business image   <INT>
                ad_img_height                   =   height of ad image              <INT>
                ad_img_width                    =   width of ad image               <INT>
                website                         =   the website to redirect         <STRING> 
                headline_text                   =   text for the headline           <STRING>       
                long_headline_text              =   secondary headline              <STRING>
                description_text                =   description text                <STRING>
                business_name                   =   name of the business           <STRING>
                
    '''
    # create client
    client = GoogleAdsClient.load_from_storage(google_yaml)
    # budget resource
    num_days=datetime.strptime(end_date,'%d-%m-%Y,%H:%M')-datetime.strptime(start_date,'%d-%m-%Y,%H:%M')
    budget=budget/num_days.days
    budget_resource_name = create_budget(client=client,
                                         customer_id=customer_id,
                                         budget=budget,
                                         campaign_objective=campaign_objective)
    print(f'Created budget with resource name "{budget_resource_name}".')
    # campign 
    campaign_resource_name = create_smart_display_campaign(client=client,
                                                           customer_id=customer_id,
                                                           budget_resource_name=budget_resource_name,
                                                           campaign_objective=campaign_objective,
                                                           start_date=start_date,
                                                           end_date=end_date)
    print(f"Created smart display campaign with resource name {campaign_resource_name}")
    
    set_campaign_targeting_criteria(client=client, 
                                    customer_id=customer_id, 
                                    campaign_resource_name=campaign_resource_name,
                                    location_ids=location_ids)
    # ad group
    ad_group_resource_name = create_ad_group(client=client,
                                             customer_id=customer_id,
                                             campaign_resource_name=campaign_resource_name,
                                             campaign_objective=campaign_objective)
    print(f'Created ad group with resource name "{ad_group_resource_name}"')
    # ad image
    marketing_image_asset_id = upload_image_asset(client=client,
                                                  customer_id=customer_id,
                                                  image_url=ad_image_url,
                                                  image_height=ad_img_height,
                                                  image_width=ad_img_width)
    print(f"Created marketing image asset with resource name {marketing_image_asset_id}")
    # business image       
    square_marketing_image_asset_id = upload_image_asset(client=client,
                                                         customer_id=customer_id,
                                                         image_url=business_image_url,
                                                         image_height=business_image_dim,
                                                         image_width=business_image_dim)                      
    print(f"Created square marketing image asset with resource name {square_marketing_image_asset_id}")


    # create ad
    responsive_display_ad_resource_name = create_ad(client=client,
                                                    customer_id=customer_id,
                                                    ad_group_resource_name=ad_group_resource_name,
                                                    website=website,
                                                    headline_text=headline_text,
                                                    long_headline_text=long_headline_text,
                                                    description_text=description_text,
                                                    business_name=business_name,
                                                    marketing_image_asset_id=marketing_image_asset_id,
                                                    square_marketing_image_asset_id=square_marketing_image_asset_id)
                                                    
    print(f"Created responsive display ad with resource name {responsive_display_ad_resource_name}")
    
    return {
                "budget":f"{budget} per day",
                "campaign_id":campaign_resource_name,
                "ad_group_id":ad_group_resource_name,
                "ad_id":responsive_display_ad_resource_name,
                "logo_asset":square_marketing_image_asset_id,
                "ad_asset":marketing_image_asset_id
            }






