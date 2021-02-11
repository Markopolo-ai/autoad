# AutoAd
automated ad creation api

```python
Version: 0.0.1     
Authors: Md. Nazmuddoha Ansary 
```
**LOCAL ENVIRONMENT**  
```python
OS          : Ubuntu 18.04.3 LTS (64-bit) Bionic Beaver        
Memory      : 7.7 GiB  
Processor   : Intel® Core™ i5-8250U CPU @ 1.60GHz × 8    
Graphics    : Intel® UHD Graphics 620 (Kabylake GT2)  
Gnome       : 3.28.2  
```
# Setup
* ```pip3 install requirements.txt```

# PoC (Sprint:Exodus)
```python
    EXAMPLE DATA:
    
    data={'budget'      : 400, # usd
          'start_date'  : '26-1-2021,1:30',
          'end_date'    : '27-1-2021,23:30',
          'objective'   : 'Reach',  
          'channels'    : ['facebook'],
          'google'      : None,
          'facebook'    :{
                            'business_id' :   "760249887886995",
                            'page_id'     :   "Markopoloai",
                            'access_token':   "access_token_this_is_the_only_thing_that_needs_hiding"
                            'creative_id' :   "23846237956520529",
                            'geo_location': {
                                                'countries':['BD'], 
                                            }
                         }  
        }
    

```
* The **process_data** under **main.py** is the entry point for backend data processing (_only facebook for now_)

# google-ads

**Location**
* Location IDs are listed [here](https://developers.google.com/adwords/api/docs/appendix/geotargeting) 
* They can also be retrieved using the GeoTargetConstantService as shown [here](https://developers.google.com/google-ads/api/docs/targeting/location-targeting/)


**Language**
* A language criterion ID. For example, specify 1000 for English. 
* For more information on determining this value, see the below [link](https://developers.google.com/adwords/api/docs/appendix/codes-formats#languages)




# NOTES
* **BUDGET**:Must meet a required minimum budget to work (FB POLICY)
* **TODO:** 
    *   Add error handling--> This needs frontend intervention (minor)
    *   launch and test with a creative i.e- change status

# Serverless
[**Source**](https://www.serverless.com/blog/serverless-python-packaging)


