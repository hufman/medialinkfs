class MediaLinkFSError(BaseException):
	pass

class SetError(MediaLinkFSError):
	pass

class MissingParser(SetError):
	pass

class MissingSourceDir(SetError):
	pass

class MissingDestDir(SetError):
	pass
