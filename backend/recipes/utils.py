import uuid


def upload_to(instance, filename):
    extension = filename.split(".")[-1]
    instance_slug = getattr(instance, "slug", False)
    if not instance_slug:
        instance_slug = str(uuid.uuid4()).replace("-", "")

    app_label = instance._meta.app_label
    model_name = instance._meta.model_name

    return f"uploads/{app_label}/{model_name}/{instance_slug}.{extension}"
