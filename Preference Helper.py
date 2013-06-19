import sublime, sublime_plugin

import json, os.path, re

if int(sublime.version()) < 3000:
	from Tools import *
else:
	from .Tools import *

class PreferenceHelperListener(sublime_plugin.EventListener):

	def on_load(self, view):
		if not view or not IsSublimeSetting(view):
			return []
		settings = sublime.load_settings("Preference Helper.sublime-settings")
		package_name = PackageName(view)
		if package_name != "Default" and settings.get("protect_default_settings", True) and not IsUserSublimeSetting(view):
			exclude_packages = settings.get("exclude_packages", [])
			view.set_read_only(package_name not in exclude_packages)

	def on_query_completions(self, view, prefix, locations):
			
		if not (view.score_selector(locations[0], "source.json")) or view.score_selector(locations[0], "source.json string.quoted.double.json") != 2064 or not IsSublimeSetting(view):
			return []
		src_json = DefaultSublimeSetting(view)
		# print(src_json)
		dst_json = UserSublimeSetting(view)
		# print(dst_json)
		keys = [(key, key) for key in src_json.keys() if "\"%s\"" % key not in dst_json]
		# print(keys)
		return keys, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS

class FillSettingFileCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		point = self.view.sel()[0].a if self.view.sel()[0].a < self.view.sel()[0].b else self.view.sel()[0].b
		line = self.view.substr(sublime.Region(self.view.line(point).a, point))[::-1]

		expr = re.search(r"\"(?P<key>[^\"]+)\"", line)
		if expr:
			key = expr.group("key")[::-1]
			src_json = DefaultSublimeSetting(self.view)
			if key in src_json:
				s = json.dumps({key:src_json[key]}, indent=2).strip("{}").strip("\t\n ")
				s = s.replace("\"%s\"" % key, "")
				s = "%s" % re.sub(r"\n\s{%d}" % 2, "\n%s" % Indention(line[::-1]), s)
				# Insert default value 
				self.view.insert(edit, point, s)
				self.view.sel().clear()
				self.view.sel().add(point + len(s))
				self.view.show(point + len(s))

class OpenSettingFileCommand(sublime_plugin.WindowCommand):

	def run(self):
		resources = [resource[9:] for resource in FindResources("*.sublime-settings")]
		def on_done(i):
			if i >= 0:
				self.window.run_command("open_file", { "file": "${packages}/%s" % resources[i]})

		self.window.show_quick_panel(resources, on_done)

class ToggleSettingFileCommand(sublime_plugin.TextCommand):

	def is_enabled(self):
		return IsSublimeSetting(self.view)
		
	def run(self, edit):
		file_dir, file_name = os.path.split(self.view.file_name())
		package_name = PackageName(self.view)
		
		if IsUserSublimeSetting(self.view):
			self.view.window().run_command("open_file", { "file": "${packages}/%s/%s" % (package_name, file_name) })
		else:
			self.view.window().run_command("open_file", { "file": "${packages}/User/%s" % file_name })
