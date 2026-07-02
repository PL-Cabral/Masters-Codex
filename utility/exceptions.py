# Criando excessões customizadas
class AttributeValidationError(Exception):
    pass

class EntityCannotActError(Exception):
    pass

class DuplicateSkillError(Exception):
    pass

class UserValidationError(Exception):
    pass

class PermissionDeniedError(Exception):
    pass

class TableValidationError(Exception):
    pass