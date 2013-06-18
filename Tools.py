import sublime, sublime_plugin

import fnmatch, os.path, re, json

def FindResources(pattern):
	# print("FindResources %s" % pattern)
	resources = []
	if hasattr(sublime, 'find_resources'):
		resources = sublime.find_resources(pattern)
	else:
		for root, dir_names, file_names in os.walk(sublime.packages_path()):
			for file_name in file_names:
				rel_path = os.path.relpath(os.path.join(root, file_name), sublime.packages_path())
				if fnmatch.fnmatch(rel_path.lower(), "*" + pattern.lower()):
					resources += [os.path.join('Packages', rel_path)]
	return resources

def LoadResource(name):
	# print("LoadResource %s" % name)
	if hasattr(sublime, 'load_resource'):
		return sublime.load_resource(name)
	else:
		with open(os.path.join(sublime.packages_path(), name[9:])) as f:
			return f.read()

def DecodeValue(string):
	# print("DecodeValue")
	if hasattr(sublime, 'decode_value'):
		return sublime.decode_value(string)
	else:
		lines = [line for line in string.split("\n") if not re.search(r'//.*', line)]
		return json.loads("\n".join(lines))

def IsSublimeSetting(view):
	try:
		return view.match_selector(0, "source.json") and view.file_name().endswith(".sublime-settings")
	except:
		return False

def IsUserSublimeSetting(view):
	return os.path.dirname(view.file_name()).endswith("User")

def PackageName(view):
	return FindResources(os.path.basename(view.file_name()))[0].split(os.sep)[1]

def DefaultSublimeSetting(view):
	file_dir, file_name = os.path.split(view.file_name())
	try:
		package_name = PackageName(view)
		content = LoadResource("Packages/%s/%s" % (package_name, file_name))
		return DecodeValue(content)		
	except:
		return {}

def UserSublimeSetting(view):
	file_dir, file_name = os.path.split(view.file_name())
	try:
		return LoadResource("Packages/User/%s" % file_name)
	except:
		return []

def Indention(s):
	rex = re.compile(r"[\t\s]*(?=[^\t\s])")
	expr = rex.search(s)
	return expr.group() if expr else ""
