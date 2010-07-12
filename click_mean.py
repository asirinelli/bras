import gtk, sys, tables
import numpy as np
import matplotlib 
matplotlib.use('GTK') 
from matplotlib.figure import Figure
from matplotlib import figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
import matplotlib.ticker as ticker


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
        filename = self.get_open_filename()
        if filename:
            self.load_file(filename)
            self.set_bacteria(0)

    def load_file(self, filename):
        f = tables.openFile(filename, 'r')
        self.IQ = f.root.IQ.read()
        print self.IQ.shape
        self.FPS = f.root.FPS.read()
        self.nb_bacteria = self.IQ.shape[0]
        f.close()

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
        self.ax_spec.clear()
        self.ax_spec.specgram(self.xc, NFFT=128, Fs=self.FPS, noverlap=0)
        self.ax_spec.xaxis.set_major_formatter(ticker.FuncFormatter(format_min))
        self.ax_spec.grid(True)
        self.canvas.draw()
        if index == 0:
            self.button_previous.set_sensitive(False)
        else:
            self.button_previous.set_sensitive(True)
        if index == (self.nb_bacteria - 1):
            self.button_next.set_sensitive(False)
        else:
            self.button_next.set_sensitive(True)

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
            self.treestore.append(None, [self.last_clicked,
                                         event.xdata,vmean,vmean2,vmean3])
            
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
            self.treestore.remove(selected)
    
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
        self.treeviewcolumn1 = builder.get_object("treeviewcolumn1")
        self.treeviewcolumn2 = builder.get_object("treeviewcolumn2")
        self.treeviewcolumn3 = builder.get_object("treeviewcolumn3")
        self.treeviewcolumn4 = builder.get_object("treeviewcolumn4")
        self.treeviewcolumn5 = builder.get_object("treeviewcolumn5")
        self.plot = builder.get_object("plot")
        self.button_add = builder.get_object("button_add")
        self.button_del = builder.get_object("button_del")
        self.treestore = builder.get_object("treestore")
        self.label = builder.get_object("label")
        self.button_previous = builder.get_object("button_previous")
        self.button_next = builder.get_object("button_next")
        self.last_clicked = None
        self.about_dialog = None

        self.cell = gtk.CellRendererText()
        self.treeviewcolumn1.pack_start(self.cell, True)
        self.treeviewcolumn1.add_attribute(self.cell, 'text', 0)
        self.treeviewcolumn2.pack_start(self.cell, True)
        self.treeviewcolumn2.add_attribute(self.cell, 'text', 1)
        self.treeviewcolumn3.pack_start(self.cell, True)
        self.treeviewcolumn3.add_attribute(self.cell, 'text', 2)
        self.treeviewcolumn4.pack_start(self.cell, True)
        self.treeviewcolumn4.add_attribute(self.cell, 'text', 3)
        self.treeviewcolumn5.pack_start(self.cell, True)
        self.treeviewcolumn5.add_attribute(self.cell, 'text', 4)

        # connect signals
        builder.connect_signals(self)
        
        # setup and initialize our statusbar
        self.statusbar_cid = self.statusbar.get_context_id("Test")

        for button in [self.button_previous, self.button_next]:
            button.set_sensitive(False)

        # setup matplotlib stuff on first notebook page (empty graph)   
        self.figure = Figure(figsize=(6,4), dpi=72)   
        self.ax_phase = self.figure.add_subplot(211)   
        self.ax_phase.set_xlabel('time')   
        self.ax_phase.set_ylabel('Speed')   
        self.ax_phase.set_title('Title')   
        self.ax_phase.grid(True)
        self.ax_spec = self.figure.add_subplot(212, sharex=self.ax_phase,
                                               sharey=self.ax_phase)

        self.canvas = FigureCanvas(self.figure) # a gtk.DrawingArea   
        self.toolbar = NavigationToolbar(self.canvas, self.window)
        self.plot.pack_start(self.canvas)
        self.plot.pack_start(self.toolbar, False, False)
        self.ax_phase.plot([1,2,3,2,1])
        self.canvas.show()   

    # Run main application window
    def main(self):
        self.window.show()
        gtk.main()

if __name__ == "__main__":
    app = Application("click_mean.xml")
    app.main()
    
