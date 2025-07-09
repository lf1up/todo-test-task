from django.urls import path

from api.views import (
    create_task,
    list_tasks,
    retrieve_task,
    update_task,
    delete_task,
)

urlpatterns = [
    path("tasks/", list_tasks, name="list_tasks"),  # GET - List all tasks
    path("tasks/create/", create_task, name="create_task"),  # POST - Create a new task
    path(
        "tasks/<int:task_id>/", retrieve_task, name="retrieve_task"
    ),  # GET - Get a specific task
    path(
        "tasks/<int:task_id>/update/", update_task, name="update_task"
    ),  # PUT/PATCH - Update a task
    path(
        "tasks/<int:task_id>/delete/", delete_task, name="delete_task"
    ),  # DELETE - Delete a task
]
