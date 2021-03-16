from collections import namedtuple

NotifySettings = namedtuple(
    'NotifySettings',
    ['agent_template', 'agent_email', 'user_template'],
)
