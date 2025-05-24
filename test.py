from WorkSpaceManager.models import WorkSpace,WorkspaceMember
from HumanResourcesManager.models import Folder,FolderCategory

for new_workspace_obj in WorkSpace.objects.all():
    if not WorkspaceMember.objects.filter(workspace=new_workspace_obj,user_account=new_workspace_obj.owner).exists():

        if not Folder.objects.filter(workspace=new_workspace_obj).exists():

            new_folder = Folder.objects.create(
                    title ="پیشفرض",
                    workspace = new_workspace_obj

                )
            new_folder.members.add(new_workspace_obj.owner)
            new_folder.save()
            category_list = [
                {
                    "title": "تایید شده",
                    "color_code": "#35dba8"
                },
                {
                    "title": "تایید نشده",
                    "color_code": "#747a80"
                }

            ]
            for item in category_list:
                new_category = FolderCategory.objects.create(
                    title=item["title"],
                    color_code=item["color_code"],
                    folder=new_folder
                )
        else:
            new_folder = Folder.objects.filter(workspace=new_workspace_obj).first()




        workspace_member = WorkspaceMember.objects.create(
            workspace= new_workspace_obj,
            user_account = new_workspace_obj.owner,
            user_type= "owner",
            folder = new_folder
        )
