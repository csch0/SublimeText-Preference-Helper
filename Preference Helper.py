import sublime, sublime_plugin

import json, os.path, re

try:
	from .preference_helper.tools import *
except ValueError:
	from preference_helper.tools import *

class PreferenceHelperListener(sublime_plugin.EventListener):

	def is_read_only(self, view):
		if is_sublime_settings(view):
			settings = sublime.load_settings("Preference Helper.sublime-settings")
			package_name = find_package_name(view)
			if package_name != "Default" and settings.get("protect_default_settings", True) and not is_user_sublime_setting(view) and not view.settings().get("pref_exclude_package"):
				exclude_packages = settings.get("exclude_packages", [])
				return package_name not in exclude_packages
		return False

	def on_activated(self, view):
		if view.size():
			view.set_read_only(self.is_read_only(view))		

	def on_query_completions(self, view, prefix, locations):

		if not is_sublime_settings(view) or view.score_selector(locations[0], "source.json string.quoted.double.json") != 2064:
			return []
		src_json = default_sublime_setting(view)
		# print(src_json)
		dst_json = user_sublime_setting(view)
		# print(dst_json)
		keys = [(key, key) for key in src_json.keys() if "\"%s\"" % key not in dst_json]
		# print(keys)
		return keys, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS


class PrefFillSettingFileCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		point = self.view.sel()[0].a if self.view.sel()[0].a < self.view.sel()[0].b else self.view.sel()[0].b
		line = self.view.substr(sublime.Region(self.view.line(point).a, point))[::-1]

		expr = re.search(r"\"(?P<key>[^\"]+)\"", line)
		if expr:
			key = expr.group("key")[::-1]
			src_json = default_sublime_setting(self.view)
			if key in src_json:
				s = json.dumps({key:src_json[key]}, indent=2).strip("{}").strip("\t\n ")
				s = s.replace("\"%s\"" % key, "")
				s = "%s" % re.sub(r"\n\s{%d}" % 2, "\n%s" % indention(line[::-1]), s)
				# Insert default value
				self.view.insert(edit, point, s)
				self.view.sel().clear()
				self.view.sel().add(point + len(s))
				self.view.show(point + len(s))


class PrefOpenSettingFileCommand(sublime_plugin.WindowCommand):

	def run(self):

		resources = [resource[9:] for resource in find_resources("*.sublime-settings")]
		def on_done(i):
			if i >= 0:
				self.window.run_command("open_file", { "file": "${packages}/%s" % resources[i]})

		self.window.show_quick_panel(resources, on_done)


class PrefToggleSettingFileCommand(sublime_plugin.TextCommand):

	def is_enabled(self):
		return is_sublime_settings(self.view)

	def run(self, edit):

		file_dir, file_name = os.path.split(self.view.file_name())

		if is_user_sublime_setting(self.view):
			package_name = find_package_name(self.view)
			def on_done(i):
				if i >= 0:
					self.view.window().run_command("open_file", { "file": "${packages}/%s/%s" % (package_name[i], file_name) })
			# Show a list if more than one possible source
			if isinstance(package_name, list):
				self.view.window().show_quick_panel(["%s/%s" % (item, file_name) for item in package_name], on_done)
			else:
				self.view.window().run_command("open_file", { "file": "${packages}/%s/%s" % (package_name, file_name) })
		else:
			self.view.window().run_command("open_file", { "file": "${packages}/User/%s" % file_name })


class PrefExcludePackageCommand(sublime_plugin.TextCommand):

	def is_enabled(self):
		return is_sublime_settings(self.view) and not is_user_sublime_setting(self.view)

	def run(self, edit, save_to_settings = True):

		# Get package name
		package_name = find_package_name(self.view)

		if save_to_settings:
			# Load settings if save_to_settings
			s = sublime.load_settings("Preference Helper.sublime-settings")
			exclude_packages = s.get("exclude_packages", [])
			if package_name not in exclude_packages:
				exclude_packages += [package_name]
			s.set("exclude_packages", exclude_packages)
			sublime.save_settings("Preference Helper.sublime-settings")
		else:
			self.view.settings().set("pref_exclude_package", True)

		# set_read_only
		self.view.set_read_only(False)

