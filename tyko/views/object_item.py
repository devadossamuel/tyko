from flask import views

from tyko import middleware


class ObjectItemNotesAPI(views.MethodView):
    def __init__(self, item: middleware.ItemMiddlwareEntity) -> None:
        self._item = item

    def put(self, project_id, object_id, item_id, note_id):  # noqa: E501 pylint: disable=W0613,C0301
        return self._item.update_note(item_id, note_id)

    def delete(self, project_id, object_id, item_id, note_id):  # noqa: E501  pylint: disable=W0613,C0301
        return self._item.remove_note(item_id, note_id)


class ObjectItemAPI(views.MethodView):
    def __init__(self, parent: middleware.ObjectMiddlwareEntity) -> None:
        self._parent_object = parent

    def delete(self, project_id, object_id, item_id):  # noqa: E501  pylint: disable=W0613,C0301
        return self._parent_object.remove_item(object_id=object_id,
                                               item_id=item_id)


class ItemAPI(views.MethodView):
    def __init__(self, item: middleware.ItemMiddlwareEntity) -> None:
        self._item = item

    def put(self, item_id):
        return self._item.update(id=item_id)

    def get(self, item_id):
        return self._item.get(id=item_id)

    def delete(self, item_id):
        return self._item.delete(id=item_id)
