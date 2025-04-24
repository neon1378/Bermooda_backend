from WorkSpaceManager.models import *

for workspace in WorkSpace.objects.all():
    if not WorkSpacePermission.objects.filter(permission_type="human_resources",workspace=workspace).exists():

        WorkSpacePermission.objects.create(
            permission_type="human_resources",
            workspace=workspace,

        )

perms = WorkSpacePermission.objects.filter(permission_type="marketing_status")
for item in perms:
    item.hard_delete()