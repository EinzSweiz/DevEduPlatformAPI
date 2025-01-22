from rest_framework.parsers import FormParser, MultiPartParser

class ParserMixinAPI:
    """
    Mixin to add common parsers for handling form data and file uploads.
    """
    parser_classes = [FormParser, MultiPartParser]
