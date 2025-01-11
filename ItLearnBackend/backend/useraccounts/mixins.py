from rest_framework.parsers import FormParser, MultiPartParser, JSONParser

class ParserMixinAPI:
    """
    Mixin to add common parsers for handling form data and file uploads.
    """
    parser_classes = [JSONParser, FormParser, MultiPartParser]