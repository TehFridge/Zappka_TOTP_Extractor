# This script has no error handlers or anything like that. Purely for testing purposes.
# Overall this script is a mess.
import zappka

# Get token needed for phone authorization
idToken = zappka.auth.get_idToken()

# Get info from user
phone_number = input("Enter phone number (ex. 123456789): ")
country_code = input("Enter country code (ex. 48): ")

print("Sending SMS authentication request.")

# Send phone authorization request. Sends a message to given phone number.
zappka.auth.send_verification_code(idToken, country_code, phone_number)

print("You should receive a message with a verification code.")

# Get code from user
sms_code = input("Enter received SMS code: ")

customToken = zappka.auth.phone_auth(idToken, country_code, phone_number, sms_code)

identityProviderToken = zappka.auth.verify_custom_token(customToken)

# Required so the API won't cry about not starting a session or something.
zappka.auth.get_account_info(identityProviderToken)

snrsToken = identityProviderToken

zappka.qr.get_qr_secret(identityProviderToken)
