#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ford Mondeo Mk4 2007 TDCi Full Diagnostics Tool - GTK GUI Version
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango
import obd
import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime

# Set log level
obd.logger.setLevel(obd.logging.ERROR)

class MondeoDialogWindow:
    def __init__(self, parent, title, message, dialog_type="info"):
        self.dialog = Gtk.MessageDialog(
            transient_for=parent,
            flags=0,
            message_type=getattr(Gtk.MessageType, dialog_type.upper()),
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        self.dialog.format_secondary_text(message)
        self.dialog.set_modal(True)

    def run(self):
        response = self.dialog.run()
        self.dialog.destroy()
        return response

class MondeoProgressDialog:
    def __init__(self, parent, title, message):
        self.dialog = Gtk.Dialog(
            title=title,
            transient_for=parent,
            modal=True
        )
        self.dialog.set_default_size(400, 120)
        self.dialog.set_resizable(False)

        # Create content area
        content = self.dialog.get_content_area()
        content.set_border_width(20)

        # Add message label
        label = Gtk.Label(label=message)
        label.set_halign(Gtk.Align.CENTER)
        content.pack_start(label, False, False, 10)

        # Add progress bar
        self.progress = Gtk.ProgressBar()
        self.progress.set_pulse_step(0.1)
        content.pack_start(self.progress, False, False, 10)

        # Start pulsing
        self.timeout_id = GLib.timeout_add(100, self.pulse)

        self.dialog.show_all()

    def pulse(self):
        self.progress.pulse()
        return True

    def destroy(self):
        if hasattr(self, 'timeout_id'):
            GLib.source_remove(self.timeout_id)
        self.dialog.destroy()

class MondeoResultsDialog:
    def __init__(self, parent, title, results):
        self.dialog = Gtk.Dialog(
            title=title,
            transient_for=parent,
            modal=True
        )
        self.dialog.set_default_size(600, 400)
        self.dialog.add_button("Close", Gtk.ResponseType.CLOSE)

        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_border_width(10)

        # Create text view
        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)

        # Set monospace font
        font_desc = Pango.FontDescription("monospace 11")
        text_view.modify_font(font_desc)

        # Add text
        buffer = text_view.get_buffer()
        buffer.set_text(results)

        scrolled.add(text_view)
        self.dialog.get_content_area().pack_start(scrolled, True, True, 0)

        self.dialog.show_all()

    def run(self):
        response = self.dialog.run()
        self.dialog.destroy()
        return response

class MondeoPortSelectionDialog:
    def __init__(self, parent, available_ports):
        self.dialog = Gtk.Dialog(
            title="Select Serial Port",
            transient_for=parent,
            modal=True
        )
        self.dialog.set_default_size(400, 250)
        self.dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.dialog.add_button("Connect", Gtk.ResponseType.OK)

        content = self.dialog.get_content_area()
        content.set_border_width(20)

        # Add instruction label
        label = Gtk.Label(label="Select the serial port for your OBD-II adapter:")
        label.set_halign(Gtk.Align.START)
        content.pack_start(label, False, False, 10)

        # Create scrolled window for port list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_size_request(-1, 150)

        # Create list store and tree view
        self.liststore = Gtk.ListStore(str, str)
        self.treeview = Gtk.TreeView(model=self.liststore)
        
        # Add columns
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Port", renderer, text=0)
        self.treeview.append_column(column)
        
        renderer2 = Gtk.CellRendererText()
        column2 = Gtk.TreeViewColumn("Description", renderer2, text=1)
        self.treeview.append_column(column2)

        # Populate with available ports
        for port in available_ports:
            self.liststore.append([port.device, port.description])

        # Select first port by default
        if available_ports:
            selection = self.treeview.get_selection()
            selection.select_path(0)

        scrolled.add(self.treeview)
        content.pack_start(scrolled, True, True, 0)

        self.dialog.show_all()
        self.selected_port = None

    def run(self):
        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            selection = self.treeview.get_selection()
            model, treeiter = selection.get_selected()
            if treeiter:
                self.selected_port = model[treeiter][0]
        
        self.dialog.destroy()
        return response, self.selected_port

class MondeoMainWindow:
    def __init__(self):
        self.connection = None
        self.setup_ui()
        self.update_connection_status()

    def setup_ui(self):
        # Main window
        self.window = Gtk.Window(title="Ford Mondeo Mk4 1.8 TDCi Diagnostics")
        self.window.set_default_size(500, 450)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("destroy", Gtk.main_quit)

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_border_width(20)

        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<span size='large' weight='bold'>Ford Mondeo Mk4 1.8 TDCi Diagnostics</span>")
        title_label.set_halign(Gtk.Align.CENTER)
        header_box.pack_start(title_label, False, False, 0)

        # Connection status
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.CENTER)
        header_box.pack_start(self.status_label, False, False, 0)

        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        header_box.pack_start(separator, False, False, 10)

        main_box.pack_start(header_box, False, False, 0)

        # Button container
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        button_box.set_halign(Gtk.Align.CENTER)

        # Read DTCs button
        self.read_button = Gtk.Button(label="Read Diagnostic Trouble Codes")
        self.read_button.set_size_request(300, 50)
        self.read_button.connect("clicked", self.on_read_codes)
        button_box.pack_start(self.read_button, False, False, 0)

        # Clear DTCs button
        self.clear_button = Gtk.Button(label="Clear Diagnostic Trouble Codes")
        self.clear_button.set_size_request(300, 50)
        self.clear_button.connect("clicked", self.on_clear_codes)
        button_box.pack_start(self.clear_button, False, False, 0)

        # Select port button
        self.port_button = Gtk.Button(label="Select Serial Port")
        self.port_button.set_size_request(300, 50)
        self.port_button.connect("clicked", self.on_select_port)
        button_box.pack_start(self.port_button, False, False, 0)

        # Reconnect button
        self.reconnect_button = Gtk.Button(label="Reconnect to Vehicle")
        self.reconnect_button.set_size_request(300, 50)
        self.reconnect_button.connect("clicked", self.on_reconnect)
        button_box.pack_start(self.reconnect_button, False, False, 0)

        main_box.pack_start(button_box, True, False, 0)

        # Footer
        footer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Separator
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        footer_box.pack_start(separator2, False, False, 10)

        # Info label
        info_label = Gtk.Label()
        info_label.set_markup("<span size='small' style='italic'>Make sure your OBD-II adapter is connected and ignition is on</span>")
        info_label.set_halign(Gtk.Align.CENTER)
        footer_box.pack_start(info_label, False, False, 0)

        # Exit button
        exit_button = Gtk.Button(label="Exit")
        exit_button.set_size_request(100, 30)
        exit_button.set_halign(Gtk.Align.CENTER)
        exit_button.connect("clicked", self.on_exit)
        footer_box.pack_start(exit_button, False, False, 0)

        main_box.pack_start(footer_box, False, False, 0)

        self.window.add(main_box)
        self.window.show_all()

        # Auto-connect on startup
        GLib.timeout_add(1000, self.auto_connect)

    def auto_connect(self):
        """Auto-connect to OBD adapter on startup"""
        if not self.connection:
            self.connect_to_obd()
        return False  # Don't repeat

    def update_connection_status(self):
        """Update the connection status display"""
        if self.connection and self.connection.is_connected():
            port_name = self.connection.port_name()
            self.status_label.set_markup(f"<span color='green' weight='bold'>CONNECTED to {port_name}</span>")
            self.read_button.set_sensitive(True)
            self.clear_button.set_sensitive(True)
        else:
            self.status_label.set_markup("<span color='red' weight='bold'>NOT CONNECTED</span>")
            self.read_button.set_sensitive(False)
            self.clear_button.set_sensitive(False)

    def get_available_ports(self):
        """Get list of available serial ports"""
        try:
            ports = list(serial.tools.list_ports.comports())
            # Filter for likely OBD-II adapters
            obd_ports = []
            for port in ports:
                # Common OBD-II adapter descriptions
                desc_lower = port.description.lower()
                if any(keyword in desc_lower for keyword in ['usb', 'serial', 'ch340', 'ftdi', 'cp210', 'obd']):
                    obd_ports.append(port)
            
            return obd_ports if obd_ports else ports
        except Exception as e:
            print(f"Error listing ports: {e}")
            return []

    def connect_to_obd(self, selected_port=None):
        """Connect to OBD-II adapter"""
        def connect_worker():
            try:
                if selected_port:
                    # Try connecting to specific port
                    conn = obd.OBD(selected_port, baudrate=38400, timeout=30)
                else:
                    # Try auto-connect
                    conn = obd.OBD(baudrate=38400, timeout=30)
                
                if conn.is_connected():
                    GLib.idle_add(self.connection_success, conn)
                else:
                    # If auto-connect failed, try different baudrates
                    for baudrate in [38400, 9600, 115200, 57600]:
                        try:
                            if selected_port:
                                conn = obd.OBD(selected_port, baudrate=baudrate, timeout=30)
                            else:
                                conn = obd.OBD(baudrate=baudrate, timeout=30)
                            
                            if conn.is_connected():
                                GLib.idle_add(self.connection_success, conn)
                                return
                            else:
                                conn.close()
                        except:
                            continue
                    
                    GLib.idle_add(self.connection_failed, "No connection detected. Check ignition, adapter, and cable.")
            except Exception as e:
                GLib.idle_add(self.connection_failed, f"Connection failed: {str(e)}")

        # Start connection in background thread
        thread = threading.Thread(target=connect_worker)
        thread.daemon = True
        thread.start()

    def connection_success(self, conn):
        """Handle successful connection"""
        self.connection = conn
        self.update_connection_status()
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.destroy()
        return False

    def connection_failed(self, error_msg):
        """Handle connection failure"""
        self.connection = None
        self.update_connection_status()
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.destroy()

        dialog = MondeoDialogWindow(
            self.window,
            "Connection Failed",
            error_msg,
            "error"
        )
        dialog.run()
        return False

    def on_select_port(self, button):
        """Handle select port button click"""
        available_ports = self.get_available_ports()
        
        if not available_ports:
            dialog = MondeoDialogWindow(
                self.window,
                "No Ports Found",
                "No serial ports detected. Please check that your OBD-II adapter is connected.",
                "error"
            )
            dialog.run()
            return

        # Show port selection dialog
        port_dialog = MondeoPortSelectionDialog(self.window, available_ports)
        response, selected_port = port_dialog.run()

        if response == Gtk.ResponseType.OK and selected_port:
            # Close existing connection
            if self.connection:
                try:
                    self.connection.close()
                except:
                    pass
                self.connection = None

            self.update_connection_status()

            # Show progress dialog
            self.progress_dialog = MondeoProgressDialog(
                self.window,
                "Connecting",
                f"Connecting to {selected_port}..."
            )

            # Start connection with selected port
            self.connect_to_obd(selected_port)

    def on_read_codes(self, button):
        """Handle read DTCs button click"""
        if not self.connection:
            dialog = MondeoDialogWindow(
                self.window,
                "Not Connected",
                "Please connect to the vehicle first.",
                "error"
            )
            dialog.run()
            return

        # Show progress dialog
        self.progress_dialog = MondeoProgressDialog(
            self.window,
            "Reading DTCs",
            "Reading Diagnostic Trouble Codes..."
        )

        def read_worker():
            try:
                codes = self.connection.get_dtc()
                GLib.idle_add(self.show_dtc_results, codes)
            except Exception as e:
                GLib.idle_add(self.show_error, f"Error reading DTCs: {str(e)}")

        thread = threading.Thread(target=read_worker)
        thread.daemon = True
        thread.start()

    def show_dtc_results(self, codes):
        """Display DTC results"""
        self.progress_dialog.destroy()

        if codes and codes.value:
            # Format results
            results = f"Diagnostic Trouble Codes Found ({len(codes.value)} total):\n\n"
            results += "=" * 50 + "\n\n"

            for i, (code, desc) in enumerate(codes.value, 1):
                results += f"{i}. Code: {code}\n"
                results += f"   Description: {desc}\n"
                results += f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            results += "=" * 50 + "\n"
            results += "Please consult your service manual or a qualified technician for proper diagnosis and repair."

            dialog = MondeoResultsDialog(self.window, "Diagnostic Trouble Codes", results)
            dialog.run()
        else:
            dialog = MondeoDialogWindow(
                self.window,
                "No DTCs Found",
                "No diagnostic trouble codes detected. Vehicle systems appear normal.",
                "info"
            )
            dialog.run()

        return False

    def on_clear_codes(self, button):
        """Handle clear DTCs button click"""
        if not self.connection:
            dialog = MondeoDialogWindow(
                self.window,
                "Not Connected",
                "Please connect to the vehicle first.",
                "error"
            )
            dialog.run()
            return

        # Confirmation dialog
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Clear Diagnostic Trouble Codes?"
        )
        confirm_dialog.format_secondary_text(
            "Are you sure you want to clear all diagnostic trouble codes? "
            "This will erase stored fault information that may be needed for diagnosis."
        )

        response = confirm_dialog.run()
        confirm_dialog.destroy()

        if response == Gtk.ResponseType.YES:
            # Show progress dialog
            self.progress_dialog = MondeoProgressDialog(
                self.window,
                "Clearing DTCs",
                "Clearing Diagnostic Trouble Codes..."
            )

            def clear_worker():
                try:
                    response = self.connection.clear_dtc()
                    GLib.idle_add(self.show_clear_results, response)
                except Exception as e:
                    GLib.idle_add(self.show_error, f"Error clearing DTCs: {str(e)}")

            thread = threading.Thread(target=clear_worker)
            thread.daemon = True
            thread.start()

    def show_clear_results(self, response):
        """Display clear DTCs results"""
        self.progress_dialog.destroy()

        if response.is_successful():
            dialog = MondeoDialogWindow(
                self.window,
                "DTCs Cleared",
                "Diagnostic trouble codes have been successfully cleared!",
                "info"
            )
            dialog.run()
        else:
            dialog = MondeoDialogWindow(
                self.window,
                "Clear Failed",
                "Failed to clear diagnostic trouble codes. Please try again.",
                "error"
            )
            dialog.run()

        return False

    def show_error(self, error_msg):
        """Display error message"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.destroy()

        dialog = MondeoDialogWindow(
            self.window,
            "Error",
            error_msg,
            "error"
        )
        dialog.run()
        return False

    def on_reconnect(self, button):
        """Handle reconnect button click"""
        # Close existing connection
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None

        self.update_connection_status()

        # Show progress dialog
        self.progress_dialog = MondeoProgressDialog(
            self.window,
            "Reconnecting",
            "Reconnecting to vehicle..."
        )

        # Start connection
        self.connect_to_obd()

    def on_exit(self, button):
        """Handle exit button click"""
        # Close OBD connection
        if self.connection:
            try:
                self.connection.close()
            except:
                pass

        Gtk.main_quit()

def main():
    """Main entry point"""
    app = MondeoMainWindow()

    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("\nExiting...")
        if app.connection:
            try:
                app.connection.close()
            except:
                pass

if __name__ == "__main__":
    main()
