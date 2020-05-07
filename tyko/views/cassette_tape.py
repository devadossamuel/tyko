from flask import views, request, jsonify, make_response
from tyko.data_provider import CassetteTypeConnector, \
    CassetteTapeTypeConnector, \
    CassetteTapeThicknessConnector


class AbsEnumView(views.MethodView):
    def get(self):
        requested_id = request.args.get("id")
        results = self._connector.get(id=requested_id, serialize=True)
        if results is None:
            return make_response("Unable to find requested cassette types",
                                 404)
        return jsonify(results)


class CassetteTapeFormatTypesAPI(AbsEnumView):
    def __init__(self, provider):
        self._provider = provider
        self._connector = CassetteTypeConnector(provider.db_session_maker)

    def post(self):
        args = request.get_json()
        name = args["name"]
        res = self._connector.create(name=name)
        return jsonify(res)


class CassetteTapeTapeTypesAPI(AbsEnumView):
    def __init__(self, provider):
        self._provider = provider
        self._connector = CassetteTapeTypeConnector(provider.db_session_maker)


class CassetteTapeThicknessAPI(AbsEnumView):
    def __init__(self, provider):
        self._provider = provider
        self._connector = \
            CassetteTapeThicknessConnector(provider.db_session_maker)
