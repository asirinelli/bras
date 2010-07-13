#!/usr/bin/env python

import gtk, sys, tables, os, csv
import numpy as np
import matplotlib 
matplotlib.use('GTK') 
from matplotlib.figure import Figure
from matplotlib import figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
import matplotlib.ticker as ticker
import gobject

def smooth(x,window_len=11,window='hanning'):
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."

    if window_len<3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s=np.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]


def format_min(x, pos=None):
    min = x //60
    sec = x % 60
    return "%d:%02d"%(min, sec)

class Application:
    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()

    def get_open_filename(self):    
        filename = None
        chooser = gtk.FileChooserDialog("Open File...", self.window,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                         gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        h5filter = gtk.FileFilter()
        h5filter.set_name("HDF5 files")
        h5filter.add_pattern("*.h5")
        chooser.add_filter(h5filter)
        response = chooser.run()
        if response == gtk.RESPONSE_OK: filename = chooser.get_filename()
        chooser.destroy()
        return filename

    def on_open_menu(self, menuitem, data=None):
        self.filename = self.get_open_filename()
        if self.filename:
            self.load_file(self.filename)
            self.set_bacteria(0)

    def on_save_menu(self, menuitem, data=None):
        file_save = self.get_save_filename(os.path.dirname(self.filename),
                                           os.path.splitext(os.path.split(self.filename)[1])[0] + '.csv')
        if file_save == None:
            return
        writer = csv.writer(open(file_save, 'w'))
        writer.writerow([os.path.split(self.filename)[1]])
        writer.writerow(['Bact.', 'start', 'stop', 'dt', 'v', 'v2', 'vfft'])
        for t in self.treestores:
            for r in t:
                data = r[5]
                writer.writerow([data['bacteria'],
                                 data['start'],
                                 data['stop'],
                                 data['dt'],
                                 data['v'],
                                 data['v2'],
                                 data['vfft']])

    def get_save_filename(self, directory, filename):
        filesave = None
        chooser = gtk.FileChooserDialog("Save File...", self.window,
                                        gtk.FILE_CHOOSER_ACTION_SAVE,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                         gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        csvfilter = gtk.FileFilter()
        csvfilter.set_name("CSV files")
        csvfilter.add_pattern("*.csv")
        chooser.add_filter(csvfilter)
        chooser.set_current_folder(directory)
        chooser.set_current_name(filename)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filesave = chooser.get_filename()
        chooser.destroy()
        return filesave

    def load_file(self, filename):
        f = tables.openFile(filename, 'r')
        self.IQ = f.root.IQ.read()
        print self.IQ.shape
        self.FPS = f.root.FPS.read()
        self.nb_bacteria = self.IQ.shape[0]
        f.close()
        self.treestores = []
        for ii in range(self.nb_bacteria):
            self.treestores.append(gtk.TreeStore(str, str, str, str, str, gobject.TYPE_PYOBJECT))

    def set_bacteria(self, index):
        self.index = index
        self.label.set_text("%d/%d"% (index, self.nb_bacteria-1))
        self.xc = self.IQ[index,:,0] + 1j *self.IQ[index,:,1]
        self.xc = self.xc -np.mean(self.xc)
        ph = np.unwrap(np.angle(self.xc))
        self.time = np.arange(len(ph), dtype=float)/self.FPS
        fact = self.FPS/2./np.pi
        self.vit_phase = fact*np.diff(ph)
        self.vit_phase_smooth = fact*smooth(np.diff(ph), self.FPS)
        self.ax_phase.clear()
        self.ax_phase.plot(self.time[:-1],
                           self.vit_phase)
        self.ax_phase.plot(self.time[:-1],
                           self.vit_phase_smooth,
                           lw=2)
        self.ax_phase.grid(True)
        self.ax_phase.set_title("%s / %d" % (os.path.basename(self.filename),
                                             self.index))
        self.ax_phase.set_ylabel('Rotation speed (Hz)')
        self.ax_spec.clear()
        self.ax_spec.specgram(self.xc, NFFT=128, Fs=self.FPS, noverlap=0)
        self.ax_spec.xaxis.set_major_formatter(ticker.FuncFormatter(format_min))
        self.ax_spec.grid(True)
        self.ax_spec.set_ylabel('Rotation speed (Hz)')
        self.ax_spec.set_xlabel('time (min:s)')

        self.canvas.draw()
        if index == 0:
            self.button_previous.set_sensitive(False)
        else:
            self.button_previous.set_sensitive(True)
        if index == (self.nb_bacteria - 1):
            self.button_next.set_sensitive(False)
        else:
            self.button_next.set_sensitive(True)
        self.treeview.set_model(self.treestores[index])

    def on_about(self, menuitem, data=None):
        if self.about_dialog: 
            self.about_dialog.present()
            return
        
        authors = [
        "Antoine Sirinelli <antoine@monte-stello.com.com>"
        ]
        
        about_dialog = gtk.AboutDialog()
        about_dialog.set_transient_for(self.window)
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("Click and Mean")
        about_dialog.set_version("0.1")
        about_dialog.set_copyright("Copyright \xc2\xa9 2010 Antoine Sirinelli")
        about_dialog.set_website("http://monte-stello.com/")
        about_dialog.set_comments("Data analysis for bacteria")
        about_dialog.set_authors(authors)
        about_dialog.set_logo_icon_name(gtk.STOCK_EDIT)
        
        # callbacks for destroying the dialog
        def close(dialog, response, editor):
            editor.about_dialog = None
            dialog.destroy()
            
        def delete_event(dialog, event, editor):
            editor.about_dialog = None
            return True
                    
        about_dialog.connect("response", close, self)
        about_dialog.connect("delete-event", delete_event, self)
        
        self.about_dialog = about_dialog
        about_dialog.show()

    def on_click(self, event):
        if self.last_clicked:
            self.canvas.mpl_disconnect(self.connection)
            ind1, ind2 = np.searchsorted(self.time,
                                         [self.last_clicked, event.xdata])
            xc_loc = self.xc[ind1:ind2]
            xc_loc = xc_loc - np.mean(xc_loc)
            vmean = np.mean(self.vit_phase[ind1:ind2])
            vmean2 = np.mean(self.FPS/2./np.pi*np.diff(np.unwrap(np.angle(xc_loc))))
            fft = np.abs(np.fft.fft(xc_loc))
            vit = np.fft.fftfreq(len(fft), 1./self.FPS)
            vmean3 = vit[np.argmax(fft)]
            data = {'start': self.last_clicked,
                    'stop': event.xdata,
                    'dt': event.xdata-self.last_clicked,
                    'v': vmean,
                    'v2': vmean2,
                    'vfft': vmean3,
                    'bacteria': self.index}
            self.treestores[self.index].append(None,
                                               [ format_min(data['start']),
                                                 format_min(data['stop']),
                                                 "%.2f" % data['v'],
                                                 "%.2f" % data['v2'],
                                                 "%.2f" % data['vfft'],
                                                 data])
            
            for widget in [self.button_add, self.button_del, self.treeview]:
                widget.set_sensitive(True)
            self.last_clicked = None
        else:
            self.last_clicked = event.xdata


    def on_button_add_clicked(self, widget, data=None):
        for widget in [self.button_add, self.button_del, self.treeview]:
            widget.set_sensitive(False)

        self.connection = self.canvas.mpl_connect('button_press_event',
                                                  self.on_click)

    def on_button_del_clicked(self, widget, data=None):
        treemodel, selected = self.treeview.get_selection().get_selected()
        if selected:
            self.treestores[self.index].remove(selected)
    
    def on_button_next_clicked(self, widget, data=None):
        if (self.index + 1) < self.nb_bacteria:
            self.set_bacteria(self.index+1)

    def on_button_previous_clicked(self, widget, data=None):
        if self.index >0 :
            self.set_bacteria(self.index-1)

    def __init__(self, xmlfile):
        # use GtkBuilder to build our interface from the XML file 
        try:
            builder = gtk.Builder()
            builder.add_from_file(xmlfile) 
        except:
            self.error_message("Failed to load UI XML file: %s"%xmlfile)
            sys.exit(1)
            
        # get the widgets which will be referenced in callbacks
        self.window = builder.get_object("window")
        self.statusbar = builder.get_object("statusbar")
        self.treeview = builder.get_object("treeview")
#        self.treeview.set_model(gtk.TreeStore(float, float, float, float, float))
        cell = gtk.CellRendererText()

        for ii, title in enumerate(["start", "stop", "<v>", "<v2>", "<vfft>"]):
            treeviewcolumn = gtk.TreeViewColumn(title)
            self.treeview.append_column(treeviewcolumn)
            treeviewcolumn.pack_start(cell, True)
            treeviewcolumn.add_attribute(cell, 'text', ii)

        self.plot = builder.get_object("plot")
        self.button_add = builder.get_object("button_add")
        self.button_del = builder.get_object("button_del")
        self.treestore = builder.get_object("treestore")
        self.label = builder.get_object("label")
        self.button_previous = builder.get_object("button_previous")
        self.button_next = builder.get_object("button_next")
        self.last_clicked = None
        self.about_dialog = None

        # connect signals
        builder.connect_signals(self)
        
        # setup and initialize our statusbar
        self.statusbar_cid = self.statusbar.get_context_id("Test")

        for button in [self.button_previous, self.button_next]:
            button.set_sensitive(False)

        # setup matplotlib stuff on first notebook page (empty graph)   
        self.figure = Figure(figsize=(6,4), dpi=72)   
        self.ax_phase = self.figure.add_subplot(211)   
        self.ax_phase.grid(True)
        self.ax_spec = self.figure.add_subplot(212, sharex=self.ax_phase,
                                               sharey=self.ax_phase)
        self.ax_spec.grid(True)
        self.canvas = FigureCanvas(self.figure) # a gtk.DrawingArea   
        self.toolbar = NavigationToolbar(self.canvas, self.window)
        self.plot.pack_start(self.canvas)
        self.plot.pack_start(self.toolbar, False, False)

        self.canvas.show()   

    # Run main application window
    def main(self):
        self.window.show()
        gtk.main()

if __name__ == "__main__":
    app = Application("click_mean.xml")
    app.main()
    
