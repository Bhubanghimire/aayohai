# utils/renderers.py
from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = {
            'data': data,
            'message': 'Success'
        }
        return super().render(response, accepted_media_type, renderer_context)
