from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import json

from .models import Task


@csrf_exempt
@require_http_methods(["POST"])
def create_task(request):
    try:
        data = json.loads(request.body)
        text = data.get("text", "").strip()

        if not text:
            return JsonResponse({"error": "Task text is required"}, status=400)

        if Task.objects.filter(text=text).exists():
            return JsonResponse(
                {"error": "Task with this text already exists"}, status=400
            )

        task = Task.objects.create(text=text)
        return JsonResponse(
            {"id": task.id, "text": task.text, "is_done": task.is_done}, status=201
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def list_tasks(request):
    tasks = Task.objects.all()
    tasks_data = [
        {"id": task.id, "text": task.text, "is_done": task.is_done} for task in tasks
    ]

    return JsonResponse(tasks_data, safe=False)


@require_http_methods(["GET"])
def retrieve_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return JsonResponse({"id": task.id, "text": task.text, "is_done": task.is_done})


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    try:
        data = json.loads(request.body)

        # Update text if provided
        if "text" in data:
            text = data["text"].strip()
            if not text:
                return JsonResponse({"error": "Task text cannot be empty"}, status=400)

            # Check if another task with this text exists
            existing_task = Task.objects.filter(text=text).exclude(id=task_id).first()
            if existing_task:
                return JsonResponse(
                    {"error": "Task with this text already exists"}, status=400
                )

            task.text = text

        if "is_done" in data:
            task.is_done = bool(data["is_done"])

        task.save()

        return JsonResponse({"id": task.id, "text": task.text, "is_done": task.is_done})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task_data = {"id": task.id, "text": task.text, "is_done": task.is_done}
    task.delete()

    return JsonResponse(
        {"message": "Task deleted successfully", "deleted_task": task_data}
    )
