
from rest_framework.permissions import BasePermission
from UserManager.models import GroupMain,PermissionCategory,ViewName,PermissionType
from django.shortcuts import get_object_or_404
from WorkSpaceManager.models import WorkSpace,WorkspaceMember
class IsAccess(BasePermission):
    def has_permission(self, request, view):
        # Determine workspace object based on request method
        workspace_id = request.GET.get("workspace_id") if request.method == "GET" else request.data.get("workspace_id")
        workspace_obj = get_object_or_404(WorkSpace, id=workspace_id)

        request.manager_gp_id = 1
        # Grant full access if the user is the owner of the workspace
        if workspace_obj.owner == request.user:
            return True

        # Initialize permission group IDs
        group_map = {"read": None, "edit": None, "manager": None,"nessery_manager":False}

        # Determine model name
        model_name = getattr(view, 'queryset', None) or view.__class__.__name__.replace("View", "").capitalize()
    
        view_objs = ViewName.objects.filter(name=model_name.lower())
      
        for view_obj in view_objs:
       
            if int(view_obj.perm_category.workspace) == int(workspace_id):             
                
                if not view_obj.nessery_manager:
                    for main_group in view_obj.perm_category.group_obj.all():
                        perm_type = main_group.gp_perm_type.permission_type
                        if perm_type in group_map:
                            group_map[f"{perm_type}"] = main_group.real_group_obj.id
      
        request.manager_gp_id = group_map['manager']
            # Check user group permissions based on HTTP method
        if group_map['nessery_manager'] :
            return request.user.groups.filter(id=group_map["manager"]).exists()
        if request.method == "GET":
            if request.user.groups.filter(id=group_map["read"]).exists() :
                return True
            else:
                return request.user.groups.filter(id__in=[group_map["edit"], group_map["manager"]]).exists()

        return request.user.groups.filter(id__in=[group_map["edit"], group_map["manager"]]).exists()


class IsWorkSpaceMemberAccess(BasePermission):
    def __init__(self):
        self.required_for_permission =[
            "crmdepartmentmanager",
            "groupcrmmanager",
            "categorymanager",
            "customerusermanager",
            "projectmanager",
            "projectdepartmentmanager",
            "taskmanager",
            "categoryprojectmanager",
            "foldermanager",
        ]
    def has_permission(self, request, view):
        model_name = getattr(view, 'queryset', None) or view.__class__.__name__.replace("View", "").capitalize()
        workspace_id = request.user.current_workspace_id
        if workspace_id == 0 or not WorkSpace.objects.filter(id=workspace_id).exists():
            workspace_owner = WorkSpace.objects.filter(owner=request.user).first()
            workspace_member = WorkspaceMember.objects.filter(user_account= request.user).first()
            if workspace_owner:
                request.user.current_workspace_id=workspace_owner.id
                request.user.save()
            elif workspace_member:
                request.user.current_workspace_id = workspace_member.workspace.id
                request.user.save()
            else:
                self.message = "you have to create a workspace first"
                return False


        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        if request.user == workspace_obj.owner:
            return True
        if model_name.lower() not in self.required_for_permission:
            return True

        is_not_exists = True
        permission_dic = {}
        for member in workspace_obj.workspace_member.all():
            if member.user_account == request.user:
                is_not_exists=False
                for permission in member.permissions.all():
                    for view_name in permission.view_names.all():
                
                        if view_name.view_name == model_name.lower():
                            for method in view_name.methods.all():
                                print(method)
                                permission_dic[method.method_name.upper()] = method.is_permission
                            request.user_permission_type = permission.permission_type


        self.message = "شما به این قسمت دسترسی ندارید"
        return permission_dic[request.method]

class IsWorkSpaceUser(BasePermission):
    
    def has_permission(self, request, view):
        if request.method in ['POST',"PUT","DELETE"]:
            try:
                workspace_id = request.data.get("workspace_id")
            except:
                self.message = "workspace_id its a required field"
                return False
        elif request.method == "GET":
            try:
                workspace_id = request.GET.get("workspace_id")
            except:
                self.message = "workspace_id its a required field"
                return False
        else:
            return True
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)

        if request.user == workspace_obj.owner :
            return True
        else:
            perm = False
            for member in workspace_obj.workspace_member.all():
                if request.user == member.user_account:
                    # if member.is_accepted:

                        perm=True
                        break
            self.message = "you dont have any permission to read this workspace detail"
            return perm
        


        


