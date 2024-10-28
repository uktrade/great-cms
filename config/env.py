import os
import dj_database_url
from typing import Any, Optional, Union

from dbt_copilot_python.database import database_url_from_env
from dbt_copilot_python.utility import is_copilot
from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic_settings import BaseSettings as PydanticBaseSettings, SettingsConfigDict


class BaseSettings(PydanticBaseSettings):
    """Base class holding all environment variables for Great."""

    model_config = SettingsConfigDict(
        extra='ignore',
        validate_default=False,
    )

    # Start of Environment Variables
    app_environment: str
    secret_key: str

    cache_middleware_seconds: int = 60 * 30  # 30 minutes

    @property
    def database_url(self):
        raise NotImplementedError

    @property
    def redis_url(self):
        raise NotImplementedError


class DBTPlatformEnvironment(BaseSettings):
    """Class holding all listed environment variables on DBT Platform.

    Instance attributes are matched to environment variables by name (ignoring case).
    e.g. DBTPlatformEnvironment.app_environment loads and validates the APP_ENVIRONMENT environment variable.
    """

    build_step: bool = Field(alias='build_step', default=False)
    celery_broker_url: str = Field(alias='celery_broker_url', default='')

    @computed_field(return_type=str)
    @property
    def database_url(self):
        if self.build_step:
            return 'postgres://'

        return dj_database_url.parse(database_url_from_env("DATABASE_CREDENTIALS"))

    @computed_field(return_type=str)
    @property
    def redis_url(self):
        if self.build_step:
            return 'rediss://'

        return self.celery_broker_url


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


if is_copilot():
    if 'BUILD_STEP' in os.environ:
        # When building use the fake settings in circleci env file
        print('--RUNNING DBTPLATFORM AT BUILDTIME--')
        env: Union[DBTPlatformEnvironment, GovPaasEnvironment] = DBTPlatformEnvironment(secret_key='FAKE_SECRET_KEY')
    else:
        # When deployed read values from DBT Platform environment
        print('--RUNNING DBTPLATFORM AT RUNTIME--')
        env = DBTPlatformEnvironment()
else:
    # Gov PaaS environment
    print('--RUNNING GOVPAAS--')    
    env = GovPaasEnvironment()
