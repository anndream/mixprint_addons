#
#  Created by Patipol Treerojporn on 30/04/12
#  Copyright (c) 2555 1Moby Co., Ltd. All rights reserved.
#

import sys, os
sys.path.append(os.path.dirname(__file__))

import httplib, urllib

class ThaiBulkSMSAPI:
    def __init__(self):
        self._SERVER = "www.thaibulksms.com"
        self._PORT = "80"
        self._URI = "/sms_api.php"
    
    def sendMessage(self, username, password, msisdn, message, sender, ScheduledDelivery):
        
        """
            Send SMS via ThaiBulkSMS HTTP API
            
            Argruments:
            (string) username --- ThaiBulkSMS username (required)
            (string) password --- ThaiBulkSMS password (required)
            (string) msisdn --- Thai-style destination mobile phone number, to send to multiple numbers at once use , (comma) to split between numbers (required)
            (string) message --- Text message (required)
            (string) [Sender] --- Available Sender Name (optional)
            (string) [ScheduledDelivery] --- Schedule time to deliver in format "yymmddhhmm" (optional), eg. "1204300909"
            
            Return:
            A list contains:
            1. Integer of status code returned by server
            2. XML Data replied from ThaiBulkSMS API
        """
        
        conn = httplib.HTTPConnection(self._SERVER, self._PORT)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        params = urllib.urlencode({'username': username, 'password': password, 'msisdn': msisdn, 'message': message, 'sender': sender, 'ScheduledDelivery': ScheduledDelivery })
        
        conn.request("POST", self._URI, params, headers)
        response = conn.getresponse()
        data = response.read()
        
        conn.close()
        
        if response.status == 200:
            return response.status, data
        else:
            return response.status, response.reason
    
    
    
    def getCreditRemain(self, username, password, tag):
        
        """
            Get credit remain via ThaiBulkSMS HTTP API
            
            Argruments:
            (string) username --- ThaiBulkSMS username (required)
            (string) password --- ThaiBulkSMS password (required)
            (string) tag --- "credit_remain" for standard SMS or "credit_remain_premium" for premium SMS
            
            Return:
            A list contains:
            1. Integer of status code returned by server
            2. String of credit remain or XML Data of detail of failure
        """
        
        conn = httplib.HTTPConnection(self._SERVER, self._PORT)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        params = urllib.urlencode({'username': username, 'password': password, 'tag': tag })
        
        conn.request("POST", self._URI, params, headers)
        response = conn.getresponse()
        data = response.read()
        
        conn.close()
        
        if response.status == 200:
            return response.status, data
        else:
            return response.status, response.reason
