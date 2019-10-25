import math
from copy import deepcopy

from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
from django.conf import settings
from cached_property import threaded_cached_property_with_ttl
import logging

from django_auth0_user.settings import AUTH0_RULE_CONFIGS
from django_auth0_user.settings import AUTH0_RULES
from django_auth0_user.settings import AUTH0_DOMAIN
from django_auth0_user.settings import AUTH0_API_URL
from django_auth0_user.settings import AUTH0_MANAGEMENT_API_CLIENT_ID
from django_auth0_user.settings import AUTH0_MANAGEMENT_API_CLIENT_SECRET


# TODO: The logging here should be more consistent.
logger = logging.getLogger(__name__)


AUTH0_MANAGEMENT_API_TOKEN_DEFAULT_EXPIRY = 86400  # 24 hours = 86400 seconds
AUTH0_CACHED_TOKEN_TTL = 3600  # 1 hour = 3600 seconds
# AUTH0_DOMAIN = getattr(settings, 'AUTH0_DOMAIN')

# AUTH0_API_URL = 'https://' + AUTH0_DOMAIN + '/api/v2/'
# domain = AUTH0_DOMAIN


# TODO: handle empty domain, client ID and client secret, in a user friendly fashion.


class TokenCache(object):
    """
    Cache the Auth0 token with a TTL so that we get a new one regularly.

    Needed to prevent invalid token issues in production, since the production server needs to possibly live longer
    the token expiry, and we cannot just hammer the token API for a new token every time it makes a request.
    """

    @threaded_cached_property_with_ttl(ttl=AUTH0_CACHED_TOKEN_TTL)
    def auth0_management_api_token(self):
        # TODO: Convert this to a proper logging statement.
        logger.info('No cached Auth0 management API token was found...')
        get_token = GetToken(AUTH0_DOMAIN)
        token = get_token.client_credentials(
            AUTH0_MANAGEMENT_API_CLIENT_ID,
            AUTH0_MANAGEMENT_API_CLIENT_SECRET,
            AUTH0_API_URL
        )
        management_api_token = token['access_token']
        # TODO: Convert this to a proper logging statement.
        logger.info('Successfully generated a new Auth0 Management API Token, this will be cached.')
        return management_api_token


AUTH0_TOKEN_CACHE = TokenCache()


# TODO: Is this the best name for this function?
def get_auth0():
    return Auth0(AUTH0_DOMAIN, AUTH0_TOKEN_CACHE.auth0_management_api_token)


def get_all_auth0_users():
    """
    Update all the user objects...

    :return:
    """
    auth0 = get_auth0()

    auth0_users = []

    first_query = auth0.users.list()
    query_length = first_query['length']
    query_limit = first_query['limit']
    query_start = first_query['start']
    query_total = first_query['total']

    for auth0_user in first_query['users']:
        auth0_users.append(auth0_user)
    if query_length + query_start <= query_total:
        page_number = 0
        while query_length + query_start <= query_total:
            page_number += 1

            page_query = auth0.users.list(page=page_number)

            for auth0_user in page_query['users']:
                auth0_users.append(auth0_user)

            query_length = page_query['length']
            query_limit = page_query['limit']
            query_start = page_query['start']
            query_total = page_query['total']

    return auth0_users


def get_auth0_user(user_id, auth0=None):
    if auth0 is None:
        auth0 = get_auth0()
    # TODO: This does not appear to retrieve all user related data. So it may need to be improved.
    return auth0.users.get(user_id)


def get_users_from_auth0(auth0_conn: Auth0):
    """
    Get all users from Auth0

    :param auth0_conn: Authenticated Auth0 API client
    :param regex: Regex to filter users (re.match(user.email))
    """

    users_list = auth0_conn.users.list()

    total_users = users_list['total']
    page_size = users_list['length']

    # don't waste the first request
    for u in users_list['users']:
        yield u

    del users_list

    # iterate through subsequent pages
    if page_size > 0 and total_users > 0:
        for page in range(1, int(math.ceil(total_users / page_size))):
            for u in auth0_conn.users.list(page=page)['users']:
                yield u


# TODO: Add a function to get an Auth0 client's details from the Management API


# TODO: Add a function that returns true/false based on if the Auth0 client is configured to be OIDC conformant.
# TODO: Work out the best way to use this without incurring major overhead or security risks.
#  One time deployment check command?
def oidc_conformant(client_id):
    auth0 = get_auth0()
    clients = auth0.clients.all(fields=['name', 'client_id', 'oidc_conformant'])
    for client in clients:
        if client['client_id'] == client_id:
            return client['oidc_conformant']


# TODO: Make this part of the setup / deployment somehow ... >_>
# Set Auth0 Rule Configs:
def set_auth0_rule_config_values():
    """
    Add Auth0 Rule Config Data that we have defined.
    :return:
    """
    auth0 = get_auth0()
    for config_key, config_item in AUTH0_RULE_CONFIGS.items():
        result = auth0.rules_configs.set(config_key, config_item)
        logger.info(f"Auth0 Set Rule Config Key Result: result={result}")


def remove_auth0_rule_config_values():
    """
    Remove any Auth0 Rule Config data that we have setup.

    :return: None
    """
    auth0 = get_auth0()
    for config_key, config_item in AUTH0_RULE_CONFIGS.items():
        auth0.rules_configs.unset(config_key)


# Auth0 Rules:
# TODO: Document and put in some code to help Limit the required permissions when using the management API.
#  This is super important for being able to run a CI suite against this!
#  Even if stored correctly the API keys placed in a CI suite are
#  inherently vulnerable so should be limited as much as possible.

# TODO: If stage doesnt match, the rule will need to be deleted & then added again.
# TODO: It doesnt seem possible to set the stage directly... So Should I ignore it?
def setup_auth0_rules(dry_run=True):
    """
    Setup Auth0 Rules using the management API.

    :param dry_run:
    :return:
    """
    auth0 = get_auth0()

    current_rule_list = auth0.rules.all()
    current_rules = {}
    for rule in current_rule_list:
        rule_name = rule['name']
        _rule = deepcopy(rule)
        del _rule['name']
        current_rules[rule['name']] = {**_rule}
    current_rule_names = set(current_rules.keys())

    settings_rules = AUTH0_RULES
    settings_rule_names = set(settings_rules.keys())

    # If the rule isn't one we have defined, ignore it.
    # rules_to_ignore = current_rule_names - settings_rule_names
    # If the rule is one we defined and it doesnt exist yet, we need to create it.
    rules_to_create = settings_rule_names - current_rule_names
    # If the rule is defined and already exists, we need to check it is configured correctly.
    rules_to_check = current_rule_names & settings_rule_names
    rules_to_update = set()

    for rule_name in rules_to_create:
        if not dry_run:
            auth0.rules.create({
                'name': rule_name,
                **settings_rules[rule_name]
            })

    for rule_name in rules_to_check:
        if settings_rules[rule_name]['enabled'] == current_rules[rule_name]['enabled']:
            if settings_rules[rule_name]['order'] == current_rules[rule_name]['order']:
                if settings_rules[rule_name]['script'] == current_rules[rule_name]['script']:
                    continue
        rules_to_update.add(rule_name)

    # TODO: update rules here.
    for rule_name in rules_to_update:
        if not dry_run:
            auth0.rules.update(rule_name, {
                'name': rule_name,
                **settings_rules[rule_name]
            })


def tear_down_auth0_rules(dry_run=True):
    auth0 = get_auth0()
    # ----------------------------------------
    settings_rules = AUTH0_RULES
    settings_rule_names = set(settings_rules.keys())
    # ----------------------------------------
    current_rule_mapping = {}
    for rule in auth0.rules.all():
        current_rule_mapping[rule['name']] = rule['id']
    for rule_name in settings_rule_names:
        rule_id = current_rule_mapping[rule_name]
        if not dry_run:
            auth0.rules.delete(rule_id)
