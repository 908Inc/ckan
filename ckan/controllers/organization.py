# encoding: utf-8

import logging
import re

import ckan.controllers.group as group
import ckan.plugins as plugins
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
import ckan.model as model
import ckan.authz as authz
from ckan.common import c, request, _

log = logging.getLogger(__name__)

render = base.render
abort = base.abort

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params



class OrganizationController(group.GroupController):
    ''' The organization controller is for Organizations, which are implemented
    as Groups with is_organization=True and group_type='organization'. It works
    the same as the group controller apart from:
    * templates and logic action/auth functions are sometimes customized
      (switched using _replace_group_org)
    * 'bulk_process' action only works for organizations

    Nearly all the code for both is in the GroupController (for historical
    reasons).
    '''

    group_types = ['organization']

    def _guess_group_type(self, expecting_name=False):
        return 'organization'

    def _replace_group_org(self, string):
        ''' substitute organization for group if this is an org'''
        return re.sub('^group', 'organization', string)

    def _update_facet_titles(self, facets, group_type):
        for plugin in plugins.PluginImplementations(plugins.IFacets):
            facets = plugin.organization_facets(
                facets, group_type, None)

    def member_new(self, id):
        group_type = self._ensure_controller_matches_group_type(id)

        context = {'model': model, 'session': model.Session,
                   'user': c.user}
        try:
            self._check_access('group_member_create', context, {'id': id})
        except NotAuthorized:
            abort(403, _('Unauthorized to create group %s members') % '')

        try:
            data_dict = {'id': id}
            data_dict['include_datasets'] = False
            c.group_dict = self._action('group_show')(context, data_dict)
            c.roles = self._action('member_roles_list')(
                context, {'group_type': group_type}
            )

            if request.method == 'POST':
                data_dict = clean_dict(dict_fns.unflatten(
                    tuplize_dict(parse_params(request.params))))
                data_dict['id'] = id
                prob_email = data_dict.get('email')
                user_by_email = model.User.by_email(prob_email)
                if not user_by_email:
                    user_data_dict = {
                        'email': prob_email,
                        'group_id': data_dict['id'],
                        'role': data_dict['role']
                    }
                    user_dict = self._action('user_invite')(
                        context, user_data_dict)
                    data_dict['username'] = user_dict['name']
                else:
                    # Old logic suggests that email isn't unique
                    data_dict['username'] = user_by_email[0].name
                if 'email' in data_dict:
                    del data_dict['email']
                c.group_dict = self._action('group_member_create')(
                    context, data_dict)

                self._redirect_to_this_controller(action='members', id=id)
            else:
                user = request.params.get('user')
                if user:
                    c.user_dict = \
                        get_action('user_show')(context, {'id': user})
                    c.user_role = \
                        authz.users_role_for_group_or_org(id, user) or 'member'
                else:
                    c.user_role = 'member'
        except NotAuthorized:
            abort(403, _('Unauthorized to add member to group %s') % '')
        except NotFound:
            abort(404, _('Group not found'))
        except ValidationError, e:
            h.flash_error(e.error_summary)
        return self._render_template('group/member_new.html', group_type)
