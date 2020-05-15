import abc
from flask import views, request, jsonify, make_response
from tyko.data_provider import CassetteTypeConnector, \
    CassetteTapeTypeConnector, \
    CassetteTapeThicknessConnector, \
    AbsDataProviderConnector


class AbsEnumView(views.MethodView):

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

    @property
    def connector(self):
        return CassetteTapeThicknessConnector(self._provider.db_session_maker)

    def post(self):
        args = request.get_json()
        value = args['value']
        unit = args.get('unit')
        res = self.connector.create(value=value, unit=unit)
        return jsonify(res)
