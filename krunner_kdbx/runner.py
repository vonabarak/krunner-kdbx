import os.path
import sys
from typing import Optional
from pykeepass import PyKeePass
from pykeepass.entry import Entry
from uuid import UUID

import signal
import json
import logging
from gi.repository import GLib
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from setproctitle import setproctitle, setthreadtitle

from .clipboard import Clipboard
from .helper import get_password_gui

config_file = os.path.expanduser("~/.config/krunner-kdbx/config.json")
bus_name = "org.kde.krunner_kdbx"
objpath = "/runner" # Default value for X-Plasma-DBusRunner-Path metadata property
iface = "org.kde.krunner1"

class Runner(dbus.service.Object):
	app_name = "krunner-kdbx"
	cp: Clipboard
	kdbx: Optional[PyKeePass]
	_error: Optional[Exception]

	def __init__(self):
		self.logger = logging.getLogger(self.app_name)
		self.logger.addHandler(logging.StreamHandler(sys.stdout))
		self.logger.setLevel(logging.DEBUG)
		self.logger.info("Initializing")

		mainloop = DBusGMainLoop(set_as_default=True)

		sessionbus = dbus.SessionBus()
		sessionbus.request_name(bus_name, dbus.bus.NAME_FLAG_REPLACE_EXISTING)
		bus_name_obj = dbus.service.BusName(bus_name, dbus.SessionBus())
		self.logger.debug(f"Registering D-Bus session bus: {bus_name}")
		dbus.service.Object.__init__(self, bus_name_obj, objpath)

		self._error = None
		self._kdbx = None

		self.cp = Clipboard()
		self.config = {
			"filename": os.path.expanduser("~/Dropbox/Passwords.kdbx"),
			"keyfile": os.path.expanduser("~/.password-store/keepassxc.keyx"),
			"password": None,
		}
		self.read_config()

	@property
	def kdbx(self):
		if self._kdbx is not None:
			self._error = None
			return self._kdbx

		try:
			self._kdbx = PyKeePass(**self.config)
		except Exception as e:
			self.logger.error(f"Failed to create PyKeePass object: {e}")
			self._error = e

	def read_config(self):
		try:
			with open(config_file, "r") as fh:
				config = json.load(fh)
				if "filename" in config:
					self.config = os.path.expanduser(config["filename"])
				if "keyfile" in config:
					self.config = os.path.expanduser(config["keyfile"])
		except Exception as e:
			self.logger.error(f"Failed to read config: {e}")
			self._error = e


	def start(self):
		self.logger.debug("Starting service")
		setproctitle(self.app_name)
		setthreadtitle(self.app_name)

		loop = GLib.MainLoop()

		def sigint_handler(sig, frame):
			if sig == signal.SIGINT:
				print(f' Quitting {self.app_name}')
				loop.quit()
			else:
				raise ValueError("Undefined handler for '{}'".format(sig))

		signal.signal(signal.SIGINT, sigint_handler)

		loop.run()


	def copy_to_clipboard(self, string: str):
		if string:
			try:
				self.cp.copy(string)
			except Exception as e:
				self._error = e
				self.logger.error(str(self._error))

	@dbus.service.method(iface, out_signature='a(sss)')
	def Actions(self):
		if self.kdbx is None:
			return []

		return [
			('totp', 'copy TOTP', 'accept_time_event'),
			('user', 'copy username', 'username-copy'),
			('url', 'copy url', 'gnumeric-link-url'),
		]

	@dbus.service.method(iface, in_signature='s', out_signature='a(sssida{sv})')
	def Match(self, query: str) -> list:
		if len(query) < 2:
			return []

		if self.kdbx is None:
			if self._error is None:
				return [("", "Database file is locked", "object-locked", 0, 0, {})]
			else:
				return [("", str(self._error), "object-locked", 0, 0, {})]

		entries: list[Entry] = self.kdbx.find_entries(title=f".*{query}.*", regex=True)
		#("data", "display text", "object-unlocked", 100, 0.1, { "subtext": "some properties" })
		return [(
			str(entry.uuid),
			entry.title,
			"object-unlocked",
			100,
			entry.index,
			{
				"subtext": entry.username if entry.username else "",
				"actions": check_actions(entry),
			}
		) for entry in entries[:5]]

	@dbus.service.method(iface, in_signature='ss')
	def Run(self, matchId: str, actionId: str):
		if self.kdbx is None:
			password = get_password_gui()
			if password:
				self.config["password"] = password
			return

		entry = self.kdbx.find_entries(uuid=UUID(matchId))[0]
		self.logger.debug(f"matchId: {matchId}, actionId: {actionId}, entry: {entry}")
		if actionId == "":
			self.copy_to_clipboard(entry.password)
		elif actionId == "user":
			self.copy_to_clipboard(entry.username)
		elif actionId == "totp":
			self.copy_to_clipboard(entry.otp)
		elif actionId == "url":
			self.copy_to_clipboard(entry.url)

	@dbus.service.method(bus_name, in_signature='s', out_signature='(bs)')
	def Password(self, password: str) -> (bool, str):
		if password:
			self.config["password"] = password


def check_actions(entry: Entry) -> list[str]:
	actions = []
	if entry.username:
		actions.append("user")
	if entry.otp:
		actions.append("totp")
	if entry.url:
		actions.append("url")
	return actions