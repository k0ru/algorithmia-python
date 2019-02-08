'Algorithmia Algorithm API Client (python)'

import base64
import re
from Algorithmia.async_response import AsyncResponse
from Algorithmia.algo_response import AlgoResponse
from Algorithmia.errors import ApiError, ApiInternalError
from enum import Enum
from algorithmia_api_client.rest import ApiException
from algorithmia_api_client import CreateRequest, UpdateRequest, VersionRequest, Details, Settings, SettingsMandatory, SettingsPublish, \
    CreateRequestVersionInfo, VersionInfo

OutputType = Enum('OutputType','default raw void')

class Algorithm(object):
    def __init__(self, client, algoRef):
        # Parse algoRef
        algoRegex = re.compile(r"(?:algo://|/|)(\w+/.+)")
        m = algoRegex.match(algoRef)
        if m is not None:
            self.client = client
            self.path = m.group(1)
            self.username = self.path.split("/")[0]
            self.algoname = self.path.split("/")[1]
            if len(self.path.split("/")) > 2:
                self.version = self.path.split("/")[2]
            self.url = '/v1/algo/' + self.path
            self.query_parameters = {}
            self.output_type = OutputType.default
        else:
            raise ValueError('Invalid algorithm URI: ' + algoRef)

    def set_options(self, timeout=300, stdout=False, output=OutputType.default, **query_parameters):
        self.query_parameters = {'timeout':timeout, 'stdout':stdout}
        self.output_type = output
        self.query_parameters.update(query_parameters)
        return self

    # Create a new algorithm
    def create(self, details, settings, version_info):
        detailsObj = Details(**details)
        settingsObj = SettingsMandatory(**settings)
        createRequestVersionInfoObj = CreateRequestVersionInfo(**version_info)
        create_parameters = {"name": self.algoname, "details": detailsObj, "settings": settingsObj, "version_info": createRequestVersionInfoObj}
        create_request = CreateRequest(**create_parameters)
        try:
            # Create Algorithm
            api_response = self.client.manageApi.create_algorithm(self.username, create_request)
            return api_response
        except ApiException as e:
            raise ApiError("Exception when calling DefaultApi->create_algorithm: %s\n" % e)

    # Update the settings in an algorithm
    def update(self, details, settings, version_info):
        detailsObj = Details(**details)
        settingsObj = Settings(**settings)
        createRequestVersionInfoObj = CreateRequestVersionInfo(**version_info)
        update_parameters = {"details": detailsObj, "settings": settingsObj, "version_info": createRequestVersionInfoObj}
        update_request = UpdateRequest(**update_parameters)
        try:
            # Update Algorithm
            api_response = self.client.manageApi.update_algorithm(self.username, self.algoname, update_request)
            return api_response
        except ApiException as e:
            raise ApiError("Exception when calling DefaultApi->update_algorithm: %s\n" % e)

    # Publish an algorithm
    def publish(self, details, settings, version_info):
        detailsObj = Details(**details)
        settingsObj = SettingsPublish(**settings)
        versionRequestObj = VersionInfo(**version_info)
        publish_parameters = {"details": detailsObj, "settings": settingsObj, "version_info": versionRequestObj}
        version_request = VersionRequest(**publish_parameters) # VersionRequest | Publish Version Request
        try:
            # Publish Algorithm
            api_response = self.client.manageApi.publish_algorithm(self.username, self.algoname, version_request)
            return api_response
        except ApiException as e:
            raise ApiError("Exception when calling DefaultApi->publish_algorithm: %s\n" % e)

    # Get info on an algorithm
    def getInfo(self):
        try:
            # Get Algorithm
            api_response = self.client.manageApi.get_algorithm(self.username, self.algoname)
            return api_response
        except ApiException as e:
            raise ApiError("Exception when calling DefaultApi->get_algorithm: %s\n" % e)

    # Pipe an input into this algorithm
    def pipe(self, input1):

        if self.output_type == OutputType.raw:
            return self._postRawOutput(input1)
        elif self.output_type == OutputType.void:
            return self._postVoidOutput(input1)
        else:
            return AlgoResponse.create_algo_response(self.client.postJsonHelper(self.url, input1, **self.query_parameters))

    def _postRawOutput(self, input1):
            # Don't parse response as json
            self.query_parameters['output'] = 'raw'
            response = self.client.postJsonHelper(self.url, input1, parse_response_as_json=False, **self.query_parameters)
            # Check HTTP code and throw error as needed
            if response.status_code == 400:
                # Bad request
                raise ApiError(response.text)
            elif response.status_code == 500:
                raise ApiInternalError(response.text)
            else:
                return response.text

    def _postVoidOutput(self, input1):
            self.query_parameters['output'] = 'void'
            responseJson = self.client.postJsonHelper(self.url, input1, **self.query_parameters)
            if 'error' in responseJson:
                raise ApiError(responseJson['error']['message'])
            else:
                return AsyncResponse(responseJson)
