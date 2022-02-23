
class MultipleSerializerMixin:
    """
    Manages the choice of serialization depending on the action
    """

    def get_serializer_class(self):
        if self.action in self.serializers.keys():
            return self.serializers[self.action]
        return self.serializers['default']
