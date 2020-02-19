from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Gtk

import re
import logging


logger = logging.getLogger('zim.plugin.runnables')

from zim.plugins import PluginClass, InsertedObjectTypeExtension
from zim.signals import SignalEmitter, ConnectorMixin, SIGNAL_RUN_LAST
from zim.utils import WeakSet
from zim.config import String
from zim.formats import ElementTreeModule as ElementTree
from zim.gui.insertedobjects import InsertedObjectWidget
from zim.gui.widgets import Dialog, InputEntry, ScrolledWindow
from zim.gui.pageview import PageViewExtension

class TableEditorPlugin(PluginClass):

	plugin_info = {
		'name': _('Runnables'),  # T: plugin name
		'description': _('''Description'''),  # T: plugin description
		'help': 'Plugins:Runnables',
		'author': 'Mitchell Hansen',
	}

	plugin_preferences = (
		# key, type, label, default
		('show_helper_toolbar', 'bool', _('Show helper toolbar'), True),   # T: preference description

		# option for displaying grid-lines within the table
	#	('grid_lines', 'choice', _('Grid lines'), LINES_BOTH, (LINES_BOTH, LINES_NONE, LINES_HORIZONTAL, LINES_VERTICAL)),
		# T: preference description
	)

#self.emit('link-clicked', {'href': str("foqiwejfoiqwjef")})
#
# class InsertSymbolPageViewExtension(PageViewExtension):
#
# 	def __init__(self, plugin, pageview):
# 		PageViewExtension.__init__(self, plugin, pageview)
# 		self.connectto(pageview.textview, 'end-of-word')
# 		if not plugin.symbols:
# 			plugin.load_file()
#
# 	@action(_('Sy_mbol...'), menuhints='insert')  # T: menu item
# 	def insert_symbol(self):
#
#
# 	def on_end_of_word(self, textview, start, end, word, char, editmode):
# 		textview.stop_emission('end-of-word')



class TableViewObjectType(InsertedObjectTypeExtension):

	name = 'runnable'

	label = _('Runnable')

	object_attr = {
		'program': String('grep'),
		'arguments': String('-r "hello!"')
	}

	def __init__(self, plugin, objmap):

#		InsertSymbolDialog(self.plugi).run()
		self._widgets = WeakSet()
		self.preferences = plugin.preferences
		InsertedObjectTypeExtension.__init__(self, plugin, objmap)
		self.connectto(self.preferences, 'changed', self.on_preferences_changed)


	def data_from_model(self, buffer):
		return buffer.get_object_data()

	def model_from_data(self, notebook, page, attrib, data):
		return TableModel(attrib)

	def model_from_element(self, attrib, element):
		assert ElementTree.iselement(element)
		attrib = self.parse_attrib(attrib)
		return TableModel(attrib)


	def create_widget(self, model):
		widget = TableViewWidget(model)
		self._widgets.add(widget)
		return widget

	def on_preferences_changed(self, preferences):
		for widget in self._widgets:
			widget.set_preferences(preferences)

	def dump(self, builder):

		builder.start("start")
		builder.data("data")
		builder.end("end")


class TableModel(ConnectorMixin, SignalEmitter):

	__signals__ = {
		'changed': (SIGNAL_RUN_LAST, None, ()),
		'model-changed': (SIGNAL_RUN_LAST, None, ()),
	}

	def __init__(self, attrib):
		self._attrib = attrib
		self.headers = []

	def get_object_data(self):
		return self._attrib, ""

	def change_model(self, newdefinition):
		self.emit('model-changed')
		self.emit('changed')



class TableViewWidget(InsertedObjectWidget):

	def __init__(self, model):

		InsertedObjectWidget.__init__(self)
		self.model = model
		self.cont = Gtk.HBox()
		link = Gtk.LinkButton(label="Previous")
		link.connect('button-press-event', self.on_button_press_event)
		self.cont.add(link)
		self.cont.add(Gtk.LinkButton(label="This"))
		self.cont.add(Gtk.LinkButton(label="Advance"))


		self.add(self.cont)

		# signals
		model.connect('model-changed', self.on_model_changed)

	def on_button_press_event(self, a, event):

		if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
			pass

	def _init_treeview(self, model):
		pass

	def on_model_changed(self, model):
		self.scroll_win.show_all()

	def on_focus_in(self, treeview, event, toolbar):
		'''After a table is selected, this function will be triggered'''

		self._keep_toolbar_open = False
		if self._timer:
			GObject.source_remove(self._timer)
		if self._toolbar_enabled:
			toolbar.show()

	def on_focus_out(self, treeview, event, toolbar):
		'''After a table is deselected, this function will be triggered'''
		def receive_alarm():
			return False

		self._timer = GObject.timeout_add(500, receive_alarm)



	def on_move_cursor(self, view, step_size, count):
		''' If you try to move the cursor out of the tableditor release the cursor to the parent textview '''
		return None  # let parent handle this signal

	def fetch_cell_by_event(self, event, treeview):
		'''	Looks for the cell where the mouse clicked on it '''
		#liststore = treeview.get_model()
		(xpos, ypos) = event.get_coords()
		#(treepath, treecol, xrel, yrel) = treeview.get_path_at_pos(int(xpos), int(ypos))
		#treeiter = liststore.get_iter(treepath)
		#cellvalue = liststore.get_value(treeiter, treeview.get_columns().index(treecol))
		#return cellvalue
		pass

	def get_linkurl(self, celltext):
		'''	Checks a cellvalue if it contains a link and returns only the link value '''
		linkregex = r'<span foreground="blue">.*?<span.*?>(.*?)</span></span>'
		matches = re.match(linkregex, celltext)
		linkvalue = matches.group(1) if matches else None
		return linkvalue


	def on_open_link(self, action, link):
		''' Context menu: Open a link, which is written in a cell '''
		self.emit('link-clicked', {'href': str(link)})

	def selection_info(self):
		''' Info-Popup for selecting a cell before this action can be done '''
		md = Gtk.MessageDialog(None, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE,
								_("Please select a row, before you push the button."))
		# T:
		md.run()
		md.destroy()








class InsertSymbolDialog(Dialog):

	def __init__(self, parent, plugin, pageview):
		Dialog.__init__(
			self,
			parent,
			_('Insert Symbol'), # T: Dialog title
			button=_('_Insert'),  # T: Button label
			defaultwindowsize=(350, 400)
		)
		self.plugin = plugin
		# #self.pageview = pageview
		# if not plugin.symbols:
		# 	plugin.load_file()
		#
		# self.textentry = InputEntry()
		# self.vbox.pack_start(self.textentry, False, True, 0)
		#
		# model = Gtk.ListStore(str, str) # text, shortcut
		# self.iconview = Gtk.IconView(model)
		# self.iconview.set_text_column(0)
		# self.iconview.set_column_spacing(0)
		# self.iconview.set_row_spacing(0)
		# self.iconview.set_property('has-tooltip', True)
		# self.iconview.set_property('activate-on-single-click', True)
		# self.iconview.connect('query-tooltip', self.on_query_tooltip)
		# self.iconview.connect('item-activated', self.on_activated)
		#
		# swindow = ScrolledWindow(self.iconview)
		# self.vbox.pack_start(swindow, True, True, 0)
		#
		# button = Gtk.Button.new_with_mnemonic(_('_Edit')) # T: Button label
		# button.connect('clicked', self.on_edit)
		# self.action_area.add(button)
		# self.action_area.reorder_child(button, 0)
		#
		# self.load_symbols()

	def load_symbols(self):
		model = self.iconview.get_model()
		model.clear()
		for symbol, shortcut in self.plugin.get_symbols():
			model.append((symbol, shortcut))

	def on_query_tooltip(self, iconview, x, y, keyboard, tooltip):
		if keyboard:
			return False

		x, y = iconview.convert_widget_to_bin_window_coords(x, y)
		path = iconview.get_path_at_pos(x, y)
		if path is None:
			return False

		model = iconview.get_model()
		iter = model.get_iter(path)
		text = model.get_value(iter, 1)
		if not text:
			return False

		tooltip.set_text(text)
		return True

	def on_activated(self, iconview, path):
		model = iconview.get_model()
		iter = model.get_iter(path)
		text = model.get_value(iter, 0)
		pos = self.textentry.get_position()
		self.textentry.insert_text(text, pos)
		self.textentry.set_position(pos + len(text))

	def on_edit(self, button):
		file = ConfigManager.get_config_file('symbols.list')
		if edit_config_file(self, file):
			self.plugin.load_file()
			self.load_symbols()

	def run(self):
		self.iconview.grab_focus()
		Dialog.run(self)

	def do_response_ok(self):
		text = self.textentry.get_text()
		textview = self.pageview.textview
		buffer = textview.get_buffer()
		buffer.insert_at_cursor(text)
		return True

