SERVICE_NAME = 'great-cms'

VIDEO_DURATION_DATA_ATTR_NAME = 'data-v-duration'

BACKLINK_QUERYSTRING_NAME = 'return-link'

# Define a strict subset of rich-text features only includes linebreaks
RICHTEXT_FEATURES__MINIMAL = ()

AWS_S3_MAIN_HOSTNAME_OPTIONS = [
    # https://docs.aws.amazon.com/general/latest/gr/s3.html
    's3.amazonaws.com',  # most likely
    's3.eu-west-2.amazonaws.com',  # London
    's3.dualstack.eu-west-2.amazonaws.com',  # London IPv4 + IPv6
    # 'account-id.s3-control.eu-west-2.amazonaws.com',  # inviable for us
    # 'account-id.s3-control.dualstack.eu-west-2.amazonaws.com',   # inviable for us
    's3-accesspoint.eu-west-2.amazonaws.com',
    's3-accesspoint.dualstack.eu-west-2.amazonaws.com',
]

ARTICLE_TYPES = [
    ('Blog', 'Blog'),
    ('Advice', 'Advice'),
    ('Case study', 'Case study'),
    ('Campaign', 'Campaign'),
]

VIDEO_TRANSCRIPT_HELP_TEXT = 'If the video is present, a transcript must be provided.'
