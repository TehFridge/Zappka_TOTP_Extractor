import requests
import json
import uuid

class auth:

    # Authentication requests from https://github.com/TehFridge/Zappka3DS

    def get_idToken():
        """
        Used for phone authentication.
        """
        url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=AIzaSyDe2Fgxn_8HJ6NrtJtp69YqXwocutAoa9Q"
        
        headers = {
            "content-type": "application/json"
        }

        data = {
            "clientType": "CLIENT_TYPE_ANDROID"
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        try:
            return response.json()['idToken']
        except KeyError:
            raise Exception("No idToken in response. (get temp auth token)")

    def send_verification_code(idToken, country_code, phone_number):
        """
        Start phone number authentication.
        Request sends SMS message to given phone number.
        """
        url = "https://super-account.spapp.zabka.pl/"

        headers = {
            "content-type": "application/json",
            "authorization": "Bearer " + idToken,
        }

        data = {
            "operationName": "SendVerificationCode",
            "query": "mutation SendVerificationCode($input: SendVerificationCodeInput!) { sendVerificationCode(input: $input) { retryAfterSeconds } }",
            "variables": {
                "input": {
                    "phoneNumber": {
                        "countryCode": country_code,
                        "nationalNumber": phone_number,
                    }
                }
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
            
        return response.json()


    def phone_auth(idToken, country_code, phone_number, verify_code):
        """
        Complete phone number authentication.
        Sends the code from SMS message to Żabka.
        Returns customToken.

        Uses token from get_idToken()
        """
        url = "https://super-account.spapp.zabka.pl/"

        headers = {
            "content-type": "application/json",
            "authorization": "Bearer " + idToken,
            "user-agent": "okhttp/4.12.0",
            "x-apollo-operation-id": "a531998ec966db0951239efb91519560346cfecac77459fe3b85c5b786fa41de",
            "x-apollo-operation-name": "SignInWithPhone",
            "accept": "multipart/mixed; deferSpec=20220824, application/json",
            "content-length": "250",
        }

        data = {
            "operationName": "SignInWithPhone",
            "variables": {
                "input": {
                    "phoneNumber": {
                        "countryCode": country_code, 
                        "nationalNumber": phone_number,
                    },
                    "verificationCode": verify_code,
                }
            },
            "query": "mutation SignInWithPhone($input: SignInInput!) { signIn(input: $input) { customToken } }"
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
            
        try:
            return response.json()['data']['signIn']['customToken']
        except KeyError:
            raise Exception("No customToken in response. (phone auth)")
        except TypeError:
            raise Exception("Incorrect SMS code. (phone auth)")
        
    def verify_custom_token(customToken):
        """
        Requires customToken received after phone authentication.
        Returns identityProviderToken. Used for zabka-snrs token and Superlogin requests.
        """
        url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key=AIzaSyDe2Fgxn_8HJ6NrtJtp69YqXwocutAoa9Q"

        headers = {
            "content-type": "application/json",
        }

        data = {
            "token": customToken,
            "returnSecureToken": "True",
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        try:
            return response.json()['idToken']
        except KeyError:
            raise Exception("No idToken in response. (verify custom token)")
        
    def get_account_info(token):
        url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key=AIzaSyDe2Fgxn_8HJ6NrtJtp69YqXwocutAoa9Q"

        headers = {
            "content-type": "application/json"
        }

        data = {
            "idToken": token,
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        return response.json()
        

class snrs:

    def get_snrs_token(identityProviderToken):
        """
        Requires identityProviderToken.
        """
        uid = str(uuid.uuid4())

        url = "https://api.spapp.zabka.pl/"

        headers = {
            "Cache-Control": "no-cache", 
            "user-agent": "Zappka/40038 (Android; MEDIATEK/GS2018; 56c41945-ba88-4543-a525-4e8f7d4a5812) REL/30", 
            "accept": "application/json",
            "content-type": "application/json; charset=UTF-8", 
            "authorization": identityProviderToken,
        }

        data = {
            "operationName": "SignIn",
            "query": """
                mutation SignIn($signInInput: SignInInput!) { 
                    signIn(signInInput: $signInInput) { 
                        profile { 
                            __typename 
                            ...UserProfileParts 
                        } 
                    } 
                }  
                fragment UserProfileParts on UserProfile { 
                    email 
                    gender 
                }
            """,
            "variables": {
                "signInInput": {
                    "sessionId": "65da013a-0d7d-3ad4-82bd-2bc15077d7f5"
                }
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        try:
            return response.json()['token']
        except KeyError:
            raise Exception("No token in response. (snrs)")


class qr:

    def get_qr_secret(snrsToken):
        url = "https://api.spapp.zabka.pl/"

        data = {
            "operationName": "QrCode",
            "query": """
                query QrCode { 
                    qrCode { 
                        loyalSecret 
                        paySecret 
                        ployId 
                    } 
                }
            """,
            "variables": {}
        }

        
        headers = {
            "Cache-Control": "no-cache", 
            "user-agent": "Zappka/40038 (Horizon; nintendo/ctr; 56c41945-ba88-4543-a525-4e8f7d4a5812) REL/28", 
            "accept": "application/json",
            "content-type": "application/json", 
            "Authorization": snrsToken,
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        loyal = response.json()['data']['qrCode']['loyalSecret'] # secret
        # pay = response.json()['secrets']['pay'] # unused but might be useful for later ig
        userId = response.json()['data']['qrCode']['ployId']
        print(f"userId: {userId} SecretTOTP: {loyal}")

        return response.json()
        
