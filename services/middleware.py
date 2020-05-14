from django.urls import reverse


class CustomHeaders:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(reverse('admin:index')):
            return response
        response['Content-type'] = "text/xml"
        response['Connection'] = "close"
        response['Expires'] = "-1"
        return response
