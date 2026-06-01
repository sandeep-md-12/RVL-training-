class NotFoundError(Exception):
    def __init__(self, resource: str, identifier=None):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} not found" + (f": {identifier}" if identifier else ""))


class AlreadyExistsError(Exception):
    def __init__(self, resource: str, field: str = None):
        self.resource = resource
        self.field = field
        super().__init__(f"{resource} already exists" + (f" ({field})" if field else ""))


class ForbiddenError(Exception):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message)


class RoomFullError(Exception):
    def __init__(self, max_members: int):
        self.max_members = max_members
        super().__init__(f"Room is full (max {max_members} members)")


class AlreadyMemberError(Exception):
    def __init__(self):
        super().__init__("User is already a member of this room")


class NotMemberError(Exception):
    def __init__(self):
        super().__init__("User is not a member of this room")


class InvalidCredentialsError(Exception):
    def __init__(self):
        super().__init__("Invalid username or password")


class InactiveUserError(Exception):
    def __init__(self):
        super().__init__("User account is inactive")


class MessageDeletedError(Exception):
    def __init__(self):
        super().__init__("Message has already been deleted")
