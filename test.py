import json
from WorkSpaceManager.models import *

with open('main_perm.json', 'r', errors='ignore', encoding='UTF-8') as file:
    data = json.load(file)
    workspaces = WorkSpace.objects.all()
    for workspace in workspaces:
        members = WorkspaceMember.objects.filter(workspace=workspace)

        for member in members:
            for side_permission in data:
                try:
                    member_permission = MemberPermission.objects.get(member=member,
                                                                     permission_name=side_permission['permission_name'])
                    for item in side_permission['items']:
                        try:
                            view_name = ViewName.objects.get(
                                permission=member_permission,
                                view_name=item['view_name']

                            )
                            for method in side_permission['methods']:
                                try:
                                    method_permission = MethodPermission.objects.get(view=view_name, method_name=method)
                                except:
                                    method_permission = MethodPermission.objects.create(view=view_name,
                                                                                        method_name=method)
                        except:

                            view_name = ViewName.objects.create(
                                permission=member_permission,
                                view_name=item['view_name']

                            )

                            for method in side_permission['methods']:
                                method_permission = MethodPermission.objects.create(view=view_name, method_name=method)
                except:
                    member_permission = MemberPermission.objects.create(member=member, permission_name=side_permission[
                        'permission_name'])
                    for item in side_permission['items']:

                        view_name = ViewName.objects.create(
                            permission=member_permission,
                            view_name=item['view_name']

                        )
                        for method in side_permission['methods']:
                            method_permission = MethodPermission.objects.create(view=view_name, method_name=method)