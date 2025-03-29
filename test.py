
from ProjectManager.models import Project,CheckList
from django.db.models import Avg, Count, Sum
from django.utils import timezone

def calculate_user_performance(project_id):
    """
    Calculate the average performance percentage (1-100) for each user
    based on their completed checklists.
    """
    # Get all users with their completed checklists
    project_obj =Project.objects.get(id=project_id)
    users_with_performance = (
        CheckList.objects
        .filter(status=True,task__project=project_obj)  # Only completed checklists
        .values('responsible_for_doing')  # Group by user
        .annotate(
            total_tasks=Count('id'),  # Total completed tasks
            average_difficulty=Avg('difficulty'),  # Average difficulty
            total_time=Sum(
                (timezone.now() - timezone.now())  # Placeholder for time calculation
            )  # Placeholder for total time
        )
    )

    # Calculate performance percentage for each user
    performance_data = []
    for user_data in users_with_performance:
        user_id = user_data['responsible_for_doing']
        total_tasks = user_data['total_tasks']
        average_difficulty = user_data['average_difficulty']

        # Calculate performance percentage (N * E, scaled to 1-100)
        performance_percentage = min(max((total_tasks * average_difficulty) / 5 * 20, 1), 100)

        performance_data.append({
            'user_id': user_id,
            'total_tasks': total_tasks,
            'average_difficulty': round(average_difficulty, 2),
            'performance_percentage': round(performance_percentage, 2)
        })

    return performance_data
print(calculate_user_performance(project_id=19))