#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

# Add commands below to run inside the container after all the other buildpacks have been applied

echo "Running image_build_run.sh"
export BUILD_STEP='true'

# shellcheck disable=SC2046
export $(grep -v '^#' test.env | sed 's/ *#.*//' | xargs)
export APP_ENVIRONMENT='local'
export REDIS_URL='redis://localhost:6379'
export BASE_URL='http://greatcms.trade.great:8020'
export WAGTAILADMIN_BASE_URL='http://greatcms.trade.great:8020'
export STAFF_SSO_AUTHBROKER_URL='https://www.example.com'
export AUTHBROKER_CLIENT_ID='debug'
export AUTHBROKER_CLIENT_SECRET='debug'
export SSO_PROXY_LOGIN_URL='http://sso.proxy.trade.great:8004/sso/accounts/login/'
export SSO_PROXY_LOGOUT_URL='http://sso.proxy.trade.great:8004/sso/accounts/logout/?next=http://greatcms.trade.great:8020/thing/'
export SSO_PROXY_SIGNUP_URL='http://sso.proxy.trade.great:8004/sso/accounts/signup/?next=http://greatcms.trade.great:8020/thing/'
export SSO_PROXY_PASSWORD_RESET_URL='http://sso.proxy.trade.great:8004/sso/accounts/password/reset/'
export SSO_PROXY_REDIRECT_FIELD_NAME='next'
export SSO_SESSION_COOKIE='debug_sso_session_cookie'
export SSO_OAUTH2_LINKEDIN_URL='http://sso.proxy.trade.great:8004/sso/accounts/login/via-linkedin/'
export SSO_OAUTH2_GOOGLE_URL='debug'
export GOOGLE_TAG_MANAGER_ID='GTM-1234567'
export UTM_COOKIE_DOMAIN='.trade.great'
export RECAPTCHA_PUBLIC_KEY='test_key'
export RECAPTCHA_DOMAIN='www.google.com'
export RECAPTCHA_PRIVATE_KEY='test_key'
export DIRECTORY_FORMS_API_BASE_URL='http://forms.trade.great:8011'
export DIRECTORY_FORMS_DEFAULT_TIMEOUT='30'
export DIRECTORY_API_CLIENT_BASE_URL='http://api.trade.great:8000'
export DIRECTORY_API_CLIENT_API_KEY='debug'
export DIRECTORY_FORMS_API_API_KEY=''
export DIRECTORY_FORMS_API_SENDER_ID='12345678-1234-1234-1234-123456789012'
export EU_EXIT_ZENDESK_SUBDOMAIN='debug'
export CONTACT_ENQUIRIES_AGENT_EMAIL_ADDRESS='local'
export CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_EMAIL_ADDRESS='local'
export CONTACT_DIT_AGENT_EMAIL_ADDRESS='local'
export CONTACT_EVENTS_AGENT_EMAIL_ADDRESS='local'
export CONTACT_DSO_AGENT_EMAIL_ADDRESS='local'
export CONTACT_INTERNATIONAL_AGENT_EMAIL_ADDRESS='local'
export UKEF_CONTACT_AGENT_EMAIL_ADDRESS='local'
export UKEF_FORM_SUBMIT_TRACKER_URL='http://go.pardot.com/l/590031/2018-08-16/5kj25l'
export MAXMIND_LICENCE_KEY='debug'
export WAGTAILTRANSFER_SECRET_KEY='local-one'
export WAGTAIL_TRANSFER_LOCAL_DEV='False'
export HEALTH_CHECK_TOKEN='debug'
export ELASTIC_APM_SECRET_TOKEN='fake-token'

echo "Running collectstatic"
python manage.py collectstatic --noinput
