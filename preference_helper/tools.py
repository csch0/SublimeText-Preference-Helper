import sublime, sublime_plugin

import fnmatch, os, re, json

def find_resources(pattern):
	# print("find_resources %s" % pattern)
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

def load_resource(name):
	# print("load_resource %s" % name)
	if hasattr(sublime, 'load_resource'):
		return sublime.load_resource(name)
	else:
		with open(os.path.join(sublime.packages_path(), name[9:])) as f:
			return f.read()

def decode_value(string):
	# print("decode_value")
	if hasattr(sublime, 'decode_value'):
		return sublime.decode_value(string)
	else:
		lines = [line for line in string.split("\n") if not re.search(r'//.*', line)]
		return json.loads("\n".join(lines))

def is_sublime_settings(view):
	try:
		return view.match_selector(0, "source.json") and os.path.dirname(view.file_name()).startswith(sublime.packages_path()) and view.file_name().endswith(".sublime-settings")
	except:
		return False

def is_user_sublime_setting(view):
	return os.path.dirname(view.file_name())[-5:] == os.sep + "User"

def find_package_name(view):
	file_dir, file_name = os.path.split(view.file_name())
	package_names = [os.path.dirname(item[9:]) for item in find_resources(file_name) if item[9:13] != "User"]
	return package_names[0] if len(package_names) == 1 else package_names

def default_sublime_setting(view):
	file_dir, file_name = os.path.split(view.file_name())
	try:
		package_name = find_package_name(view)
		content = load_resource("Packages/%s/%s" % (package_name, file_name))
		return decode_value(content)
	except:
		return {}

def user_sublime_setting(view):
	file_dir, file_name = os.path.split(view.file_name())
	try:
		return load_resource("Packages/User/%s" % file_name)
	except:
		return []

def indention(s):
	rex = re.compile(r"[\t\s]*(?=[^\t\s])")
	expr = rex.search(s)
	return expr.group() if expr else ""
