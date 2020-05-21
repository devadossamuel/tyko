import abc
from flask import views, request, jsonify, make_response
from tyko.data_provider import CassetteTypeConnector, \
    CassetteTapeTypeConnector, \
    CassetteTapeThicknessConnector, \
    AbsDataProviderConnector


class AbsEnumView(views.MethodView):
    editable_fields = [
        "name",
    ]

    def __init__(self, provider):
        super().__init__()
        self._provider = provider

    def get(self):
        requested_id = request.args.get("id")
        results = self.connector.get(id=requested_id, serialize=True)
        if results is None:
            return make_response("Unable to find requested cassette types",
                                 404)
        return jsonify(results)

    @property
    @abc.abstractmethod
    def connector(self) -> AbsDataProviderConnector:
        """Returns the proper AbsDataProviderConnector needed to connect to the
        enum tables"""

    def delete(self):
        requested_id = int(request.args["id"])
        success = self.connector.delete(requested_id)
        if success:
            return make_response("", 204)
        return make_response("", 500)

    def put(self):
        requested_id = int(request.args["id"])
        request_data_to_modify = request.get_json()

        invalid_keys = set(request_data_to_modify.keys()).difference(
            self.editable_fields)

        if len(invalid_keys) > 0:
            return make_response(f"Invalid keys {' '.join(invalid_keys)}", 400)

        resp = self.connector.update(requested_id, request_data_to_modify)
        return resp


class CassetteTapeFormatTypesAPI(AbsEnumView):

    @property
    def connector(self):
        return CassetteTypeConnector(self._provider.db_session_maker)

    def post(self):
        args = request.get_json()
        name = args["name"]
        res = self.connector.create(name=name)
        return jsonify(res)


class CassetteTapeTapeTypesAPI(AbsEnumView):

    @property
    def connector(self):
        return CassetteTapeTypeConnector(self._provider.db_session_maker)

    def post(self):
        args = request.get_json()
        name = args["name"]
        res = self.connector.create(name=name)
        return jsonify(res)


class CassetteTapeThicknessAPI(AbsEnumView):
    editable_fields = [
        "value",
        "unit"
    ]

    @property
    def connector(self):
        return CassetteTapeThicknessConnector(self._provider.db_session_maker)

    def post(self):
        args = request.get_json()
        value = args['value']
        unit = args.get('unit')
        res = self.connector.create(value=value, unit=unit)
        return jsonify(res)
