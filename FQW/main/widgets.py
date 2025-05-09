from django.forms import FileInput
from django.utils.translation import gettext as _

class MultipleFileInput(FileInput):
    input_type = 'file'
    allows_multiple_selected = True

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['multiple'] = True
        super().__init__(attrs)