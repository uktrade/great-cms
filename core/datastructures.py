from collections import namedtuple

NotifySettings = namedtuple('NotifySettings', ['user_template', 'agent_template', 'agent_email'], defaults=[None, None])
