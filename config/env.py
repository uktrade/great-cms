import os
from typing import Any, Optional

from dbt_copilot_python.database import database_url_from_env
from dbt_copilot_python.utility import is_copilot
from pydantic import BaseModel, ConfigDict, computed_field
from pydantic_settings import BaseSettings as PydanticBaseSettings, SettingsConfigDict

from config.helpers import is_circleci, is_local


class BaseSettings(PydanticBaseSettings):
    """Base class holding all environment variables for Great."""

    model_config = SettingsConfigDict(
        extra='ignore',
        validate_default=False,
    )

    # Start of Environment Variables
    debug: bool = False
    secret_key: str = 'fake_secret_key'
    app_environment: str = 'dev'

    safelist_hosts: str = ''

    wagtaildocs_serve_method: str = 'redirect'
    wagtail_cache: bool = False
    wagtail_cache_timout: int = 4 * 60 * 60  # 4 hours (in seconds)

    api_cache_disabled: bool = False

    cache_expire_seconds: int = 60 * 30  # 30 minutes

    time_zone: str = 'UTC'

    default_file_storage: str = 'storages.backends.s3boto3.S3Boto3Storage'
    staticfiles_storage: str = 'whitenoise.storage.CompressedStaticFilesStorage'

    base_url: str
    wagtailadmin_base_url: str

    sentry_browser_traces_sample_rate: float = 1.0
    sentry_dsn: str = ''
    sentry_environment: str = 'dev'
    sentry_enable_tracing: bool = False
    sentry_traces_sample_rate: float = 1.0

    secure_hsts_seconds: int = 16070400

    secure_ssl_redirect: bool = True

    session_engine: str = 'django.contrib.sessions.backends.cache'

    session_cookie_secure: bool = True
    csrf_cookie_secure: bool = True

    privacy_cookie_domain: str = ''

    aws_s3_region_name: str = ''
    aws_storage_bucket_name: str = ''
    aws_s3_custom_domain: str = ''
    aws_s3_url_protocol: str = 'https:'
    aws_access_key_id: str = ''
    aws_secret_access_key: str = ''
    aws_s3_host: str = 's3-eu-west-2.amazonaws.com'
    aws_s3_signature_version: str = 's3v4'
    aws_querystring_auth: bool = False
    s3_use_sigv4: bool = True

    service_name: str = 'great-cms'
    elastic_apm_secret_token: str
    elastic_apm_url: str = ''
    elastic_apm_server_timeout: str = '20s'

    opensearch_instance_name: str = ''
    opensearch_url: str = 'localhost:9200'

    elasticsearch_case_study_index: str = 'case-studies'

    enforce_staff_sso_enabled: bool = False

    staff_sso_authbroker_url: str
    authbroker_client_id: str
    authbroker_client_secret: str

    sso_proxy_login_url: str

    sso_api_client_base_url: str = ''
    sso_signature_secret: str = ''
    directory_sso_api_client_sender_id: str = 'directory'

    sso_profile_url: str = '/profile/'  # directory-sso-profile is now in great-cms

    sso_proxy_login_url: str
    sso_proxy_logout_url: str
    sso_proxy_signup_url: str
    sso_proxy_password_reset_url: str
    sso_proxy_redirect_field_name: str
    sso_session_cookie: str
    sso_display_logged_in_cookie: str = 'sso_display_logged_in'

    sso_oauth2_linkedin_url: str
    sso_oauth2_google_url: str

    google_tag_manager_id: str
    google_tag_manager_env: str = ''
    utm_cookie_domain: str

    ga4_api_url: str = 'https://www.google-analytics.com/mp/collect'
    ga4_api_secret: str = ''
    ga4_measurement_id: str = ''

    recaptcha_domain: str = 'www.google.com'
    recaptcha_public_key: str
    recaptcha_private_key: str
    recaptcha_required_score: float = 0.5

    directory_forms_api_base_url: str
    directory_forms_api_api_key: str
    directory_forms_api_sender_id: str
    directory_forms_api_default_timeout: int = 30
    directory_forms_api_zendesk_sevice_name: str = 'directory'

    eu_exit_zendesk_subdomain: str

    invest_contact_url: str = 'https://invest.great.gov.uk/contact/'

    capital_invest_contact_url: str = '/international/content/capital-invest/contact/'

    find_a_supplier_contact_url: str = '/international/trade/contact/'

    contact_exporting_to_uk_hmrc_url: str = 'https://www.tax.service.gov.uk/shortforms/form/CITEX_CGEF'
    confirm_verification_code_template_id: str = 'a1eb4b0c-9bab-44d3-ac2f-7585bf7da24c'
    enrolment_welcome_template_id: str = '0a4ae7a9-7f67-4f5d-a536-54df2dee42df'  # /PS-IGNORE
    eyb_enrolment_welcome_template_id: str = '651ea9b4-af61-4cd6-a969-6e305ffa133a'  # /PS-IGNORE
    enquries_contactus_template_id: str = '3af1de7c-e5c2-4691-b2ce-3856fad97ad0'  # /PS-IGNORE
    contactus_enquries_confirmation_template_id: str = '68030d40-4574-4aa1-b3ff-941320929964'
    contact_domestic_zendesk_subject: str = 'Great.gov.uk contact form'
    contact_enquiries_agent_notify_template_id: str = '7a343ec9-7670-4813-9ed4-ae83d3e1f5f7'  # /PS-IGNORE
    contact_enquiries_agent_email_address: str
    contact_enquiries_user_notify_template_id: str = '61c82be6-b140-46fc-aeb2-472df8a94d35'  # /PS-IGNORE
    contact_ecommerce_export_support_agent_email_address: str
    contact_ecommerce_export_support_agent_notify_template_id: str = 'a56114d3-515e-4ee7-bb1a-9a0ceab04378'
    contact_ecommerce_export_support_notify_template_id: str = '18d807d2-f4cf-4b93-96c1-0d3169bd0906'
    contact_office_agent_notify_template_id: str = '0492eb2b-7daf-4b37-99cd-be3abbb9eb32'
    contact_office_user_notify_template_id: str = '03c031e1-1ee5-43f9-8b24-f6e4cfd56cf1'  # /PS-IGNORE
    contact_dit_agent_email_address: str
    contact_events_user_notify_template_id: str = '2d5d556a-e0fa-4a9b-81a0-6ed3fcb2e3da'  # /PS-IGNORE
    contact_events_agent_notify_template_id: str = '7a343ec9-7670-4813-9ed4-ae83d3e1f5f7'  # /PS-IGNORE
    contact_events_agent_email_address: str
    contact_dso_agent_notify_template_id: str = '7a343ec9-7670-4813-9ed4-ae83d3e1f5f7'  # /PS-IGNORE
    contact_dso_user_notify_template_id: str = 'a6a3db79-944f-4c59-8eeb-2f756019976c'  # /PS-IGNORE
    contact_dso_agent_email_address: str
    contact_exporting_user_notify_template_id: str = '5abd7372-a92d-4351-bccb-b9a38d353e75'
    contact_exporting_agent_subject: str = 'A form was submitted on great.gov.uk'
    contact_exporting_user_reply_to_email_id: str = 'ac1b973d-5b49-4d0d-a197-865fd25b4a97'
    contact_international_agent_notify_template_id: str = ('8bd422e0-3ec4-4b05-9de8-9cf039d258a9',)
    contact_international_agent_email_address: str
    contact_international_user_notify_template_id: str = 'c07d1fb2-dc0c-40ba-a3e0-3113638e69a3'
    contact_industry_agent_email_address: str = None
    contact_industry_agent_template_id: str = 'a9318bce-7d65-41b2-8d4c-b4a76ba285a2'  # /PS-IGNORE
    contact_industry_user_template_id: str = '6a97f783-d246-42ca-be53-26faf3b08e32'
    contact_industry_user_reply_to_id: str = None
    contact_fas_company_notify_template_id: str = 'bb88aa79-595a-44fc-9ed3-cf8a6cbd6306'  # /PS-IGNORE

    subscribe_to_fta_updates_notify_template_id: str = 'cfa3b4b3-c232-4603-a3ce-e476ee8bab92'  # /PS-IGNORE
    gov_notify_welcome_template_id: str = '0a4ae7a9-7f67-4f5d-a536-54df2dee42df'  # /PS-IGNORE
    gov_notify_already_registered_template_id: str = '5c8cc5aa-a4f5-48ae-89e6-df5572c317ec'  # /PS-IGNORE
    gov_notify_new_member_registered_template_id: str = '439a8415-52d8-4975-b230-15cd34305bb5'
    gov_notify_collaboration_request_resent: str = '60c14d97-8e58-4e5f-96e9-e0ca49bc3b96'  # /PS-IGNORE

    campaign_user_notify_template_id: str = '1e00a6d9-8505-44e0-b314-6c01c46bc1b7'  # /PS-IGNORE

    ukef_contact_user_notify_template_id: str = '09677460-1796-4a60-a37c-c1a59068219e'
    ukef_contact_agent_notify_template_id: str = 'e24ba486-6337-46ce-aba3-45d1d3a2aa66'  # /PS-IGNORE
    ukef_contact_agent_email_address: str
    ukef_form_submit_tracker_url: str

    export_academy_notify_registration_template_id: str = '3b68c119-fdc5-4517-90dc-043e88853b0f'

    export_academy_notify_booking_template_id: str = '109d5d9e-4c5f-4be5-bc35-5769ef51a8df'
    export_academy_notify_cancellation_template_id: str = 'a073bd50-bd01-4cea-98c9-f2a54a0a1b56'  # /PS-IGNORE
    export_academy_notify_event_reminder_template_id: str = 'b446f2be-8c92-40af-a5c8-e21b8d9e8077'
    export_academy_notify_follow_up_template_id: str = 'ff45b258-ae9e-4939-a049-089d959ddfee'  # /PS-IGNORE
    export_academy_event_allow_join_before_start_mins: int = 30
    export_academy_automated_notify_time_delay_minutes: int = 30
    export_academy_remove_event_media_after_days: int = 14
    export_academy_automated_event_complete_time_delay_minutes: int = 15

    international_investment_notify_agent_template_id: str = 'ca1a4f1b-7c0b-4eb7-bfb2-fdff898b09f3'
    international_investment_notify_user_template_id: str = '37b5fa22-0850-49f5-af1f-5c2984ca0309'
    international_investment_agent_email: str = ''

    dnb_api_username: str = ''
    dnb_api_password: str = ''
    dnb_api_renew_access_token_seconds_remaining: int = 20

    maxmind_licence_key: str
    geolocation_maxmind_database_file_url: str = 'https://download.maxmind.com/app/geoip_download'
    geoip_download_day: str = 1
    geoip_download_hour: str = 0
    geoip_download_minute: str = 0

    companies_house_api_key: str = ''
    companies_house_client_id: str = ''
    companies_house_client_secret: str = ''
    companies_house_url: str = 'https://account.companieshouse.gov.uk'
    companies_house_api_url: str = 'https://api.companieshouse.gov.uk'

    directory_api_client_base_url: str
    directory_api_client_api_key: str

    directory_ch_search_client_base_url: str
    directory_ch_search_client_api_key: str
    directory_ch_search_client_sender_id: str = 'directory'
    directory_ch_search_client_default_timeout: str = 5

    directory_forms_api_base_url: str
    directory_forms_api_api_key: str
    directory_forms_api_sender_id: str
    directory_api_forms_default_timeout: int = 5
    directory_forms_api_zendesk_sevice_name: str = 'directory'

    max_compare_places_allowed: int = 10

    get_address_api_key: str

    check_duties_url: str = 'https://www.check-duties-customs-exporting-goods.service.gov.uk/selectdest'

    cia_factbook_url: str = 'https://www.cia.gov/the-world-factbook/'

    world_bank_url: str = 'https://www.worldbank.org/'
    data_world_bank_url: str = 'https://data.worldbank.org/indicator/NY.ADJ.NNTY.PC.CD'
    united_nations_url: str = 'https://www.un.org/en/'

    ccce_base_url: str = 'https://info.stage.3ceonline.com'
    ccce_commodity_search_token: str = ''

    directory_constants_url_single_sign_on: str = ''
    directory_constants_url_find_a_buyer: str = ''
    directory_constants_url_great_domestic: str = ''

    validator_max_logo_size_bytes: int = 2 * 1024 * 1024
    validator_max_case_study_image_size_bytes: int = 2 * 1024 * 1024
    validator_max_case_study_video_size_bytes: int = 20 * 1024 * 1024

    environment_css_theme_file: str = ''

    wagtail_transfer_local_dev: bool = False
    wagtailtransfer_secret_key: str
    wagtailtransfer_base_url_dev: str = None
    wagtailtransfer_secret_key_dev: str = None
    wagtailtransfer_base_url_uat: str = None
    wagtailtransfer_secret_key_uat: str = None
    wagtailtransfer_base_url_staging: str = None
    wagtailtransfer_secret_key_staging: str = None
    wagtailtransfer_base_url_production: str = None
    wagtailtransfer_secret_key_production: str = None
    wagtailtransfer_chooser_api_proxy_timeout: int = 10

    feature_export_plan_sections_disabled_list: list = []
    feature_compare_markets_tabs: str = '{ }'
    feature_opensearch: bool = False
    feature_search_preview: bool = False
    feature_show_report_barrier_content: bool = False
    feature_show_brand_banner: bool = False
    feature_show_international_footer_link: bool = False
    feature_show_case_study_rankings: bool = False
    feature_microsite_enable_template_translation: bool = False
    feature_digital_point_of_entry: bool = False
    feature_product_experiment_header: bool = False
    feature_product_experiment_links: bool = False
    feature_design_system: bool = False
    feature_courses_landing_page: bool = False
    feature_dea_v2: bool = False
    feature_show_old_contact_form: bool = False
    feature_homepage_redesign_v1: bool = False
    feature_share_component: bool = False
    feature_product_market_hero: bool = False
    feature_product_market_search_enabled: bool = False
    feature_show_usa_cta: bool = False
    feature_show_eu_cta: bool = False
    feature_show_market_guide_sector_spotlight_china: bool = False
    feature_show_market_guide_sector_spotlight_germany: bool = False
    feature_show_market_guide_sector_spotlight_usa: bool = False
    feature_ukea_sector_filter: bool = False
    feature_ukea_region_filter: bool = False
    feature_ukea_market_filter: bool = False
    feature_ukea_trading_bloc_filter: bool = False
    feature_market_guides_sector_links: bool = False
    feature_design_system: bool = False
    feature_great_error: bool = False
    feature_guided_journey: bool = False
    feature_unguided_journey: bool = False
    feature_test_search_api_pages_enabled: bool = False
    feature_maintenance_mode_enabled: bool = False
    feature_admin_requests_enabled: bool = False
    feature_redis_use_ssl: bool = False
    feature_great_cms_openapi_enabled: bool = False
    feature_guided_journey_extras: bool = False
    feature_guided_journey_enhanced_search: bool = False
    feature_activity_stream: bool = False
    feature_domestic_growth: bool = False

    ax_compare_places_allowed: int = 10

    beta_token: str = ''
    beta_whitelisted_endpoints: str = None
    beta_blacklisted_users: str = None
    beta_token_expiration_days: int = 30

    great_support_email: str = 'great.support@trade.gov.uk'  # /PS-IGNORE
    dit_on_govuk: str = 'www.gov.uk/government/organisations/department-for-business-and-trade'
    travel_advice_covid19: str = 'https://www.gov.uk/guidance/travel-advice-novel-coronavirus'
    travel_advice_foreign: str = 'https://www.gov.uk/foreign-travel-advice'

    breadcrumbs_root_url: str = 'https://great.gov.uk/'

    aws_access_key_id_data_science: str = ''
    aws_secret_access_key_data_science: str = ''
    aws_storage_bucket_name_data_science: str = ''
    aws_s3_region_name_data_science: str = ''

    elastic_apm_enabled: bool = False
    service_name: str = 'great-cms'
    elastic_apm_secret_token: str
    elastic_apm_url: str
    elastic_apm_server_timeout: str = '20s'

    market_access_zendesk_subject: str = 'market access'
    market_access_forms_api_zendesk_service_name: str = 'market_access'

    health_check_token: str

    activity_stream_access_key_id: str
    activity_stream_secret_key: str
    activity_stream_url: str
    activity_stream_ip_allowlist: str

    exporting_opportunities_api_basic_auth_username: str = ''
    exporting_opportunities_api_basic_auth_password: str = ''
    exporting_opportunities_api_base_url: str
    exporting_opportunities_api_secret: str
    exporting_opportunities_search_url: str

    url_prefix_domain: str = ''

    hashids_salt: str

    clam_av_enabled: bool = False
    clam_av_host: str = ''
    clam_av_username: str = ''
    clam_av_password: str = ''

    celery_task_always_eager: bool = True

    moderation_email_dist_list: str = ''
    campaign_moderators_email_template_id: str = '75c6fde4-f27c-4f75-b7ed-2b526912a041'
    campaign_moderation_requestor_email_template_id: str = '321db5bd-362c-45de-b8ce-6e9b0f36198e'
    campaign_moderation_reply_to_id: str = '654df5da-c214-4297-bb55-27690ce1813d'
    campaign_site_review_reminder_minute: str = 0
    campaign_site_review_reminder_hour: str = 0
    campaign_site_review_reminder_template_id: str = '9647397a-8d59-4b45-aa25-9d129eac8be8'  # /PS-IGNORE

    is_circleci_env: bool = False

    # countries iso code update config, default = once on the first of the month
    countries_iso_code_update_day: str = 1
    countries_iso_code_update_hour: str = 0
    countries_iso_code_update_minute: str = 0

    csp_upgrade_insecure_requests: bool = True

    headless: bool = True

    is_docker: bool = False

    feature_great_migration_banner: bool = False


class CIEnvironment(BaseSettings):
    database_url: str
    redis_url: str
    opensearch: list = []

    @computed_field(return_type=list)
    @property
    def opensearch_service(self):
        return self.opensearch


class DBTPlatformEnvironment(BaseSettings):
    """Class holding all listed environment variables on DBT Platform.

    Instance attributes are matched to environment variables by name (ignoring case).
    e.g. DBTPlatformEnvironment.app_environment loads and validates the APP_ENVIRONMENT environment variable.
    """

    build_step: bool = False
    redis_endpoint: str = ''
    opensearch: list = []

    @computed_field(return_type=str)
    @property
    def database_url(self):
        return database_url_from_env('DATABASE_CREDENTIALS')

    @computed_field(return_type=str)
    @property
    def redis_url(self):
        return self.redis_endpoint

    @computed_field(return_type=list)
    @property
    def opensearch_service(self):
        return self.opensearch


class GovPaasEnvironment(BaseSettings):
    """Class holding all listed environment variables on Gov PaaS.

    Instance attributes are matched to environment variables by name (ignoring case).
    e.g. GovPaasSettings.app_environment loads and validates the APP_ENVIRONMENT environment variable.
    """

    class VCAPServices(BaseModel):
        """Config of services bound to the Gov PaaS application"""

        model_config = ConfigDict(extra='ignore')

        postgres: list[dict[str, Any]]
        redis: list[dict[str, Any]]
        opensearch: list[dict[str, Any]]

    class VCAPApplication(BaseModel):
        """Config of the Gov PaaS application"""

        model_config = ConfigDict(extra='ignore')

        application_id: str
        application_name: str
        application_uris: list[str]
        cf_api: str
        limits: dict[str, Any]
        name: str
        organization_id: str
        organization_name: str
        space_id: str
        uris: list[str]

    model_config = ConfigDict(extra='ignore')

    vcap_services: Optional[VCAPServices] = None
    vcap_application: Optional[VCAPApplication] = None

    @computed_field(return_type=str)
    @property
    def database_url(self):
        if self.vcap_services:
            return self.vcap_services.postgres[0]['credentials']['uri']

        return 'postgres://'

    @computed_field(return_type=str)
    @property
    def redis_url(self):
        if self.vcap_services:
            return self.vcap_services.redis[0]['credentials']['uri']

        return 'rediss://'

    @computed_field(return_type=list)
    @property
    def opensearch_service(self):
        if self.vcap_services:
            return self.vcap_services.opensearch
        return ['opensearch://']


if is_local() or is_circleci():
    # Load environment files in a local or CI environment
    env_files = ['config/env/' + filename for filename in os.getenv('ENV_FILES', '').split(',')]
    env = CIEnvironment(_env_file=env_files, _env_file_encoding='utf-8')
elif is_copilot():
    # When deployed read values from DBT Platform environment
    env = DBTPlatformEnvironment()
else:
    # When deployed read values from Gov PaaS environment
    env = GovPaasEnvironment()
