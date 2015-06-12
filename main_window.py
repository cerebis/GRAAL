#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.6.7+ on Sun Jan 12 17:55:31 2014
#

import pdb

import wxversion
wxversion.select("2.8")

import wx
# import wx.aui

import numpy as np
import gettext
import os

import time
from threading import *

# The recommended way to use wx with mpl is with the WXAgg
# backend.
#
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
import pylab
import pyramid_sparse as pyr
import main_gl
import pycuda.driver as cuda
cuda.init()

# Button definitions
ID_START = wx.NewId()
ID_STOP = wx.NewId()

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()
EVT_TMP_RES_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class ResultEventGraal(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, gl_window):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.gl_window = gl_window


# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window, base_folder, size_pyramid, factor):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.base_folder = base_folder
        self.size_pyramid = size_pyramid
        self.factor = factor
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable

        pyramid = pyr.build_and_filter(self.base_folder, self.size_pyramid, self.factor)
        lev = pyr.level(pyramid, 2)
        # Here's where the result would be returned (this is an
        # example fixed result of the number 10, but it could be
        # any Python object)
        wx.PostEvent(self._notify_window, ResultEvent(pyramid))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1

# GUI Frame class that spins off the worker thread

class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)

        self.value = initval

        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.radio_auto = wx.RadioButton(self, -1,
            label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,
            label="Manual")
        self.manual_text = wx.TextCtrl(self, -1,
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)

        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())

    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()

    def is_auto(self):
        return self.radio_auto.GetValue()

    def manual_value(self):
        return self.value

class MainWindow(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MainWindow.__init__
        kwds["style"] = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.RESIZE_BORDER | wx.FRAME_NO_TASKBAR | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.button_loader = wx.Button(self, wx.ID_ANY, ("Load Data..."))
        self.button_loader.Bind(wx.EVT_BUTTON, self.OnDir)
        
        self.Status_dir = wx.StaticText(self, wx.ID_ANY, ("No data"))
        
        self.button_assembly = wx.Button(self, wx.ID_ANY, ("GRAAL"))
        self.button_assembly.Bind(wx.EVT_BUTTON, self.OnAssembly)
        
        self.button_viz = wx.Button(self, wx.ID_ANY, ("Visualize..."))
        self.button_viz.Bind(wx.EVT_BUTTON, self.visualize)

        self.__set_properties()
        self.__do_layout()
        self.pyramid = None
        # end wxGlade

    def visualize(self, event):
        lev = self.pyramid.get_level(0)
        mat = lev.sparse_mat_csr
        plt.figure()
        plt.spy(mat, precision=0, markersize=0.05)
        plt.show()

    def __set_properties(self):
        # begin wxGlade: MainWindow.__set_properties
        self.SetTitle(_("Main"))
        self.SetSize((350, 120))
        self.button_loader.SetMinSize((150, 27))
        self.Status_dir.SetMinSize((149, 17))
        self.button_assembly.SetMinSize((149, 27))
        self.button_viz.SetMinSize((149, 27))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MainWindow.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(2, 2, 0, 0)
        grid_sizer_1.Add(self.button_loader, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_1.Add(self.Status_dir, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_1.Add(self.button_assembly, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_1.Add(self.button_viz, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        sizer_1.Add(grid_sizer_1, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def OnDir(self, event):
        # Args below are: parent, question, dialog title, default answer
        dd = wx.DirDialog(None, "Select directory to open", "~/", 0, (10, 10), wx.Size(400, 300))

        # This function returns the button pressed to close the dialog
        ret = dd.ShowModal()

        # Let's check if user clicked OK or pressed ENTER
        self.data_directory = ""
        if ret == wx.ID_OK:
            self.data_directory = dd.GetPath()
            print('You selected: %s\n' % self.data_directory)
        else:
            print('You clicked cancel')

        # The dialog is not in the screen anymore, but it's still in memory
        #for you to access it's values. remove it from there.
        dd.Destroy()
        self.frame_2 = LoaderWindow(None, wx.ID_ANY, "'")
        self.frame_2.data_directory = self.data_directory
        self.frame_2.main_window = self
        app.SetTopWindow(self.frame_2)
        self.frame_2.Show()

    def OnAssembly(self, event):
        if self.pyramid != None:
            self.frame_assembly = GraalFrame(None, title="GRAAL", pyramid=self.pyramid, fasta_file=self.fasta_file, base_folder=self.data_directory)
            app.SetTopWindow(self.frame_assembly)
            self.frame_assembly.Show()
        else:
            print "pyramid not loaded!"

    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

# end of class MainWindow

class LoaderWindow(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: LoaderWindow.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        # self.data_directory = data_directory
        wx.Frame.__init__(self, *args, **kwds)
        self.label_size_pyr = wx.StaticText(self, wx.ID_ANY, _("Size of the pyramid"), style=wx.ALIGN_RIGHT | wx.ALIGN_CENTRE)
        # self.text_ctrl_size_pyr = wx.TextCtrl(self, wx.ID_ANY, _("4"))
        self.cmb_size_pyr = wx.ComboBox(self, wx.ID_ANY, value="4", choices=["4", "5", "6"], style=wx.CB_READONLY)
        self.label_fact_comp = wx.StaticText(self, wx.ID_ANY, _("Sub sampling factor : "))
        # self.text_ctrl_factor = wx.TextCtrl(self, wx.ID_ANY, _("3"))
        self.cmb_factor = wx.ComboBox(self, wx.ID_ANY, value="3", choices=["3"], style=wx.CB_READONLY)

        self.button_load_fasta = wx.Button(self, wx.ID_ANY, _("Load Fasta file..."))
        self.button_load_fasta.Bind(wx.EVT_BUTTON, self.OnLoadFasta)
        self.text_ctrl_fasta = wx.TextCtrl(self, wx.ID_ANY, _("..."))

        self.button_create_pyr = wx.Button(self, wx.ID_ANY, _("Build Pyramid"))
        self.button_create_pyr.Bind(wx.EVT_BUTTON, self.OnCreatePyr)

        self.button_return = wx.Button(self, wx.ID_ANY, _("Load Pyramid"))
        self.button_return.Bind(wx.EVT_BUTTON, self.OnReturn)

        self.label_status = wx.StaticText(self, wx.ID_ANY, _("Status:"))
        self.ctrl_status_pyr = wx.StaticText(self, wx.ID_ANY, _("data not created"))

        self.data_directory = ""
        self.data_fasta_file = ""
        self.__set_properties()
        self.__do_layout()
        EVT_RESULT(self, self.OnResult)
        self.worker = None
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: LoaderWindow.__set_properties
        self.SetTitle(_("Pyramid Builder"))
        self.SetSize((350, 290))
        self.label_size_pyr.SetMinSize((144, 17))
        self.cmb_size_pyr.SetMinSize((50, 27))
        # self.text_ctrl_size_pyr.SetMinSize((50, 27))
        self.label_fact_comp.SetMinSize((144, 17))
        # self.text_ctrl_factor.SetMinSize((50, 27))
        self.cmb_factor.SetMinSize((50, 27))
        self.button_create_pyr.SetMinSize((149, 27))
        self.button_load_fasta.SetMinSize((149, 27))
        self.text_ctrl_fasta.SetMinSize((149, 27))
        self.button_return.SetMinSize((149, 27))
        self.label_status.SetMinSize((144, 17))
        self.ctrl_status_pyr.SetMinSize((144, 17))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: LoaderWindow.__do_layout
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_2 = wx.FlexGridSizer(5, 2, 0, 0)
        grid_sizer_2.Add(self.button_load_fasta, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_2.Add(self.text_ctrl_fasta, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_2.Add(self.label_size_pyr, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        # grid_sizer_2.Add(self.text_ctrl_size_pyr, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_2.Add(self.cmb_size_pyr, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_2.Add(self.label_fact_comp, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        # grid_sizer_2.Add(self.text_ctrl_factor, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_2.Add(self.cmb_factor, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_2.Add(self.button_create_pyr, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_2.Add(self.button_return, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_2.Add(self.label_status, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_2.Add(self.ctrl_status_pyr, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_2.Add(grid_sizer_2, 1, wx.EXPAND, 0)

        self.SetSizer(sizer_2)
        self.Layout()
        self.Centre()
        # end wxGlade

    def OnLoadFasta(self, event):
        # Args below are: parent, question, dialog title, default answer
        # dd = wx.FileDialog(None, "Select Fasta File", "~/", 0, (10, 10), wx.Size(400, 300))
        wcd = "All files(*.*)|*.*|Text files (*.txt)|*.txt|"
        dd = wx.FileDialog(None, "Select Fasta File","", "", wcd, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        # This function returns the button pressed to close the dialog
        ret = dd.ShowModal()

        # Let's check if user clicked OK or pressed ENTER
        self.data_fasta_file = ""
        if ret == wx.ID_OK:
            self.data_fasta_file = dd.GetPath()
            print('Fasta file: %s\n' % self.data_fasta_file)
        else:
            print('No fasta file selected')

        # The dialog is not in the screen anymore, but it's still in memory
        #for you to access it's values. remove it from there.
        dd.Destroy()
        self.text_ctrl_fasta.SetValue(self.data_fasta_file)
        self.text_ctrl_fasta.Refresh()

    def OnCreatePyr(self, event):
        base_folder = self.data_directory
        size_pyramid = int(self.cmb_size_pyr.GetValue())
        factor = int(self.cmb_factor.GetValue())
        if not self.worker:
            self.worker = WorkerThread(self, base_folder, size_pyramid, factor)


    def OnReturn(self, event):
        self.main_window.pyramid = self.pyramid
        self.main_window.base_folder = self.data_directory
        self.main_window.fasta_file = self.data_fasta_file
        if self.pyramid != None and self.data_fasta_file !=  "" :
            # dlg = wx.MessageDialog(self,
            # "Do you really want to go back to the main window?",
            #     "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            # result = dlg.ShowModal()
            # dlg.Destroy()
            self.main_window.Status_dir.SetLabel('Pyramid loaded!')
            self.main_window.Status_dir.SetForegroundColour((255,0,0))
        #
        # if result == wx.ID_OK:
            self.Destroy()

    def OnResult(self, event):
        """Show Result status."""
        if event.data is None:
            # Thread aborted (using our convention of None return)
            self.ctrl_status_pyr.SetLabel('pyramid not created')
        else:
            # Process results here
            self.ctrl_status_pyr.SetLabel('pyramid built!')
            self.ctrl_status_pyr.SetForegroundColour((255,0,0))
            self.pyramid = event.data
        # In either event, the worker is done
        self.worker = None

# end of class LoaderWindow


# Thread class that executes processing
class GraalThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window,):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.pyramid = notify_window.pyramid
        self.level = notify_window.level
        self.n_iterations = notify_window.n_iterations
        self.scrambled = notify_window.scrambled
        self.sample_parameters = notify_window.sample_parameters
        self.fasta_file = notify_window.fasta_file
        self.title_data_set = notify_window.title_data_set
        self.blacklisted_contig = notify_window.blacklisted_contig
        self.perform_optim = notify_window.perform_optim
        self.is_simu = notify_window.is_simu
        self.output_folder = notify_window.output_folder
        self.n_neighbours = notify_window.n_neighbours
        self.allow_repeats = notify_window.allow_repeats
        self.id_selected_gpu = notify_window.id_selected_gpu
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable

        # Here's where the result would be returned (this is an
        # example fixed result of the number 10, but it could be
        # any Python object)

        gl_window = main_gl.window(self.pyramid, self.name, self.level, self.n_iterations, self.is_simu,
                                        self.scrambled,
                                        self.perform_optim, self.sample_parameters, self.output_folder, self.fasta_file,
                                        self.blacklisted_contig,self.n_neighbours, self.allow_repeats, self.id_selected_gpu,
                                        self)

        gl_window.start_EM()
        gl_window.simulation.release()
        wx.PostEvent(self._notify_window, ResultEventGraal('Done'))


    def update_gui(self, likelihood, n_contigs, mean_len, dist, slope, d_max):
        wx.CallAfter(self._notify_window.redraw, likelihood, n_contigs, mean_len, dist, slope, d_max)
    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1


class GraalFrame(wx.Frame):



    def __init__(self,*args, **kwargs):

        # print kwargs['pyramid']
        new_kwargs = {key: value for key, value in kwargs.items()
             if key is not 'pyramid' and key is not 'fasta_file' and key is not 'base_folder'}
        self.pyramid = kwargs['pyramid']
        self.fasta_file = kwargs['fasta_file']
        self.default_output_folder = os.path.join(kwargs['base_folder'], 'output_graal')
        if not(os.path.exists(self.default_output_folder)):
            os.mkdir(self.default_output_folder)
        self.list_contigs_name = [ele for ele in self.pyramid.list_contigs_name]
        self.n_level = self.pyramid.n_levels
        self.list_sub_sample_fact = [str(i) for i in range(1, self.n_level)]
        self.list_n_neihbours = [str(i) for i in range(3, 6)]
        wx.Frame.__init__(self, *args, **new_kwargs)
        self.n_devices_gpu = cuda.Device.count()
        self.list_gpu_name = [cuda.Device(i).name() for i in range(0, self.n_devices_gpu)]
        self.create_main_panel()
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        self.redraw_timer.Start(100)
        self.paused = True
        self.worker = None
        self.processing = False


    def create_main_panel(self):
        self.init_plot()
        self.panel = wx.Panel(self)
        ################################################################################################################
        self.hboxfig = wx.StaticBox(self.panel, -1, 'Simulation')
        self.vsizerfig = wx.StaticBoxSizer(self.hboxfig, wx.VERTICAL)
        self.canvas = FigCanvas(self.panel, -1, self.fig)
        ################################################################################################################
        self.vboxvariables = wx.StaticBox(self.panel, -1, 'Variables')
        self.subbox1 = wx.StaticBoxSizer(self.vboxvariables, wx.HORIZONTAL)
        self.radio_n_contigs = wx.RadioButton(self.panel, -1, label="N contigs", style=wx.RB_GROUP)
        self.radio_mean_contigs = wx.RadioButton(self.panel, -1, label="Mean contigs length (kb)")
        self.radio_dist_g0 = wx.RadioButton(self.panel, -1, label="Distance from G0")
        self.radio_slope = wx.RadioButton(self.panel, -1, label="Slope")
        self.radio_dist_intra = wx.RadioButton(self.panel, -1, label="Max intra distance (kb)")

        self.subbox1.Add(self.radio_n_contigs, border=5, flag=wx.ALL)
        self.subbox1.AddSpacer(5)
        self.subbox1.Add(self.radio_mean_contigs, border=5, flag=wx.ALL)
        self.subbox1.AddSpacer(5)
        self.subbox1.Add(self.radio_dist_g0, border=5, flag=wx.ALL)
        self.subbox1.AddSpacer(5)
        self.subbox1.Add(self.radio_slope, border=5, flag=wx.ALL)
        self.subbox1.AddSpacer(5)
        self.subbox1.Add(self.radio_dist_intra, border=5, flag=wx.ALL)
        ################################################################################################################
        self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)

        self.subbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.subbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.subbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.subbox2.AddSpacer(24)
        self.subbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.subbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
        ################################################################################################################
        self.vsizerfig.Add(self.canvas, border=15,flag=wx.ALL |wx.GROW,)
        self.vsizerfig.AddSpacer(3)
        self.vsizerfig.Add(self.subbox1, border=15,flag=wx.ALL |wx.GROW,)
        self.vsizerfig.AddSpacer(3)
        self.vsizerfig.Add(self.subbox2, border=15,flag=wx.ALL |wx.GROW,)
        ################################################################################################################
        ################################################################################################################
        self.vsizer_left = wx.FlexGridSizer(2, 1, 1, 1)
        self.layout_parameters()
        self.vsizer_left.Add(self.vsizer_param, 1, flag=wx.EXPAND)
        self.layout_run()
        self.vsizer_left.Add(self.vsizer_run, 1, flag=wx.EXPAND)
        ################################################################################################################
        self.BigHbox = wx.BoxSizer(wx.HORIZONTAL)
        self.BigHbox.Add(self.vsizer_left, 0.5, border=15, flag=wx.ALL)
        self.BigHbox.Add(self.vsizerfig, 10, border=15, flag=wx.LEFT | wx.TOP| wx.GROW,)
        # self.BigHbox.Add(self.canvas, 10, border=15, flag=wx.LEFT | wx.TOP | wx.GROW,)

        self.panel.SetSizer(self.BigHbox)
        self.BigHbox.Fit(self)
        self.panel.SetMinSize(self.BigHbox.GetMinSize())
    def layout_parameters(self):

        self.vboxparam = wx.StaticBox(self.panel, -1, 'Parameters')
        self.vsizer_param = wx.StaticBoxSizer(self.vboxparam)
        self.gs_param = wx.FlexGridSizer(8, 2, 20, 20)
        ################################################################################################################
        self.txt_sub_sample_lev = wx.StaticText(self.panel, -1, _("Pyramid level:"))
        self.cmb_sub_sample_lev = wx.ComboBox(self.panel, -1, value=self.list_sub_sample_fact[-1],
                                              choices=self.list_sub_sample_fact,
                                              style=wx.CB_READONLY, )
        ################################################################################################################
        self.txt_n_cycles = wx.StaticText(self.panel, -1, _("Number of cycles:"))
        self.text_ctrl_n_cycles = wx.TextCtrl(self.panel, -1, _("10"),)
        ################################################################################################################
        self.txt_n_neighbours = wx.StaticText(self.panel, -1, _("Neighbours per iteration:"))
        self.cmb_n_neighbours = wx.ComboBox(self.panel, -1, value="3", choices=self.list_n_neihbours,
                                              style=wx.CB_READONLY, )
        ################################################################################################################
        self.cb_sample_param = wx.CheckBox(self.panel, -1, "Sample parameters of the model", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.cb_sample_param.SetValue(True)
        ################################################################################################################
        self.cb_allow_repeat = wx.CheckBox(self.panel, -1, "Allow repeated fragments", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.cb_allow_repeat.SetValue(True)
        ################################################################################################################
        self.txt_select_cuda = wx.StaticText(self.panel, -1, _("CUDA device: "))
        self.cmb_cuda_device = wx.ComboBox(self.panel, -1, value=self.list_gpu_name[0], choices=self.list_gpu_name,
                                              style=wx.CB_READONLY,)
        ################################################################################################################
        self.txt_ctg_blacklisted = wx.StaticText(self.panel, -1, _("Blacklisted contig:"))
        self.list_str_combo = ['None']
        self.list_str_combo.extend(self.list_contigs_name)
        self.cmb_ctg_blacklisted = wx.ComboBox(self.panel, -1, value="None", choices=self.list_str_combo,
                                               style=wx.CB_READONLY,)
        ################################################################################################################
        self.perform_optim = True
        ################################################################################################################
        self.cb_explode_genome = wx.CheckBox(self.panel, -1, "Explode Genome", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.cb_explode_genome.SetValue(True)
        ################################################################################################################


        list_param = [self.txt_sub_sample_lev,self.cmb_sub_sample_lev,
                      self.txt_select_cuda, self.cmb_cuda_device,
                      self.txt_ctg_blacklisted, self.cmb_ctg_blacklisted,
                      self.txt_n_cycles, (self.text_ctrl_n_cycles, 1, wx.EXPAND),
                      self.txt_n_neighbours, self.cmb_n_neighbours,
                      self.cb_sample_param,(wx.StaticText(self.panel, -1), wx.EXPAND),
                      self.cb_allow_repeat,(wx.StaticText(self.panel, -1), wx.EXPAND),
                      self.cb_explode_genome,(wx.StaticText(self.panel, -1), wx.EXPAND)]

        self.gs_param.AddMany(list_param)
        self.vsizer_param.Add(self.gs_param, proportion=1, flag=wx.EXPAND)

    def layout_run(self):
        self.vboxrun = wx.StaticBox(self.panel, -1, 'Run')
        self.vsizer_run = wx.StaticBoxSizer(self.vboxrun)
        self.gs_run = wx.GridSizer(2, 2, 20, 20)
        size_button = (150, 30)
        size_txt_ctrl = (300, 30)
        ################################################################################################################
        self.output_folder_button = wx.Button(self.panel, -1, "Output folder...", size=size_button)
        self.Bind(wx.EVT_BUTTON, self.on_output_folder, self.output_folder_button)
        self.text_ctrl_output_folder = wx.TextCtrl(self.panel, -1, _(self.default_output_folder),)
        ################################################################################################################
        self.start_button = wx.Button(self.panel, -1, "      Start      ",)
        self.export_button = wx.Button(self.panel, -1, "Export results", )
        self.Bind(wx.EVT_BUTTON, self.on_start_button, self.start_button)
        self.Bind(wx.EVT_BUTTON, self.on_export_button, self.export_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_start_button, self.start_button)
        ################################################################################################################
        list_run = [(self.output_folder_button, 1, wx.EXPAND), (self.text_ctrl_output_folder, 1, wx.EXPAND),
                    (self.start_button, 1, wx.EXPAND), (self.export_button, 1, wx.EXPAND)]

        self.gs_run.AddMany(list_run)
        self.vsizer_run.Add(self.gs_run, proportion=1, flag=wx.EXPAND)

    def on_output_folder(self, event):
        # Args below are: parent, question, dialog title, default answer
        dd = wx.DirDialog(None, "Select output directory", "~/", 0, (10, 10), wx.Size(400, 300))

        # This function returns the button pressed to close the dialog
        ret = dd.ShowModal()

        # Let's check if user clicked OK or pressed ENTER
        self.data_directory = ""
        if ret == wx.ID_OK:
            self.data_directory = dd.GetPath()
            print('Output folder: %s\n' % self.data_directory)
        else:
            print('No output folder selected')
        dd.Destroy()
        self.text_ctrl_output_folder.SetValue(self.data_directory)
        self.text_ctrl_output_folder.Refresh()

    def on_start_button(self, event):
        self.processing = True
        self.paused = not self.paused
        self.level = int(self.cmb_sub_sample_lev.GetValue())
        self.n_iterations = int(self.text_ctrl_n_cycles.GetValue())
        self.n_neighbours = int(self.cmb_n_neighbours.GetValue())
        self.output_folder = self.text_ctrl_output_folder.GetValue()
        self.scrambled = self.cb_explode_genome.IsChecked()
        self.sample_parameters = self.cb_sample_param.IsChecked()
        self.allow_repeats = self.cb_allow_repeat.IsChecked()
        # self.perform_optim = self.radio_optimization.GetValue()
        self.title_data_set = 'to include in hdf5!!!'
        self.blacklisted_contig = [max(0, self.cmb_ctg_blacklisted.GetCurrentSelection())]
        self.id_selected_gpu  = max(0, self.cmb_cuda_device.GetCurrentSelection())
        print "blacklisted contigs = ", self.blacklisted_contig
        print "Id selected gpu = ", self.id_selected_gpu
        self.is_simu = False
        if not self.worker:
            self.worker = GraalThread(self,)
        self.processing = False


    def on_update_start_button(self, event):
        label = "Start" if self.paused else "Computing..."
        self.start_button.SetLabel(label)

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)

        self.list_str_opt_param = ['N contigs',
                                   'Mean length of the contigs (kb)',
                                   'Distance to G0',
                                   'Slope',
                                   'Max intra distance (kb)']

        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor('black')
        self.axes.set_title('', size=12)

        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        self.axes.set_xlabel('Iterations', fontsize=8)
        self.axes.set_ylabel('Log likelihood', fontsize=8)

        # plot the data as a line series, and save the reference
        # to the plotted line series

        self.data_likelihood = [0]
        self.data_opt = []
        for i in range(0, 5):
            self.data_opt.append([0])

        self.iterations = [0]
        self.plot_data_likelihood = self.axes.plot(self.iterations, self.data_likelihood,'y')[0]

        self.opt_ax = []
        self.opt_plot = []

        self.opt_ax.append(self.axes.twinx())
        pylab.setp(self.opt_ax[-1].get_yticklabels(), fontsize=8)
        self.opt_plot.append(self.opt_ax[-1].plot(self.iterations, self.data_opt[0],'r')[0])

        self.opt_ax.append(self.axes.twinx())
        pylab.setp(self.opt_ax[-1].get_yticklabels(), fontsize=8)
        self.opt_plot.append(self.opt_ax[-1].plot(self.iterations, self.data_opt[1],'b')[0])

        self.opt_ax.append(self.axes.twinx())
        pylab.setp(self.opt_ax[-1].get_yticklabels(), fontsize=8)
        self.opt_plot.append(self.opt_ax[-1].plot(self.iterations, self.data_opt[2],'g')[0])

        self.opt_ax.append(self.axes.twinx())
        pylab.setp(self.opt_ax[-1].get_yticklabels(), fontsize=8)
        self.opt_plot.append(self.opt_ax[-1].plot(self.iterations, self.data_opt[3],'w')[0])

        self.opt_ax.append(self.axes.twinx())
        pylab.setp(self.opt_ax[-1].get_yticklabels(), fontsize=8)
        self.opt_plot.append(self.opt_ax[-1].plot(self.iterations, self.data_opt[4],'c')[0])


    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #

        if self.xmax_control.is_auto():
            xmax = len(self.iterations) if len(self.iterations) > 50 else 50
        else:
            xmax = float(self.xmax_control.manual_value())

        if self.xmin_control.is_auto():
            xmin = 0
        else:
            xmin = float(self.xmin_control.manual_value())

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        #
        # note that it's easy to change this scheme to the
        # minimal/maximal value in the current display, and not
        # the whole data set.
        #

        ymin_likeli = round(min(self.data_likelihood), 0) - 1
        ymax_likeli = round(max(self.data_likelihood), 0) + 1

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin_likeli, upper=ymax_likeli)

        if self.radio_n_contigs.GetValue():
            self.select = 0
        elif self.radio_mean_contigs.GetValue():
            self.select = 1
        elif self.radio_dist_g0.GetValue():
            self.select = 2
        elif self.radio_slope.GetValue():
            self.select = 3
        elif self.radio_dist_intra.GetValue():
            self.select = 4

        list_plot = range(0, 5)
        list_plot.remove(self.select)
        for p in list_plot:
            self.opt_plot[p].set_xdata(np.arange(len([0])))
            self.opt_plot[p].set_ydata(np.array([0]))
            pylab.setp(self.opt_ax[p].get_yticklabels(),
                        visible=False)
            self.opt_ax[p].set_ylabel('', fontsize=8)

        if self.ymin_control.is_auto():
            ymin_opt = round(min(self.data_opt[self.select]), 0) - 1
        else:
            ymin_opt = float(self.ymin_control.manual_value())

        if self.ymax_control.is_auto():
            ymax_opt = round(max(self.data_opt[self.select]), 0) + 1
        else:
            ymax_opt = float(self.ymax_control.manual_value())


        axes2 = self.opt_ax[self.select]
        axes2.set_ylabel(self.list_str_opt_param[self.select], fontsize=8)
        pylab.setp(axes2.get_yticklabels(),
                        visible=True)
        axes2.set_xbound(lower=xmin, upper=xmax)
        axes2.set_ybound(lower=ymin_opt, upper=ymax_opt)


        self.axes.grid(True, color='gray')


        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly
        # iterate, and setp already handles this.
        #
        pylab.setp(self.axes.get_xticklabels(),
            visible=True)

        self.plot_data_likelihood.set_xdata(np.arange(len(self.data_likelihood)))
        self.plot_data_likelihood.set_ydata(np.array(self.data_likelihood))

        self.opt_plot[self.select].set_xdata(np.arange(len(self.data_opt[self.select])))
        self.opt_plot[self.select].set_ydata(np.array(self.data_opt[self.select]))


        self.canvas.draw()

    def redraw(self, likelihood, n_contigs, mean_len, dist, slope, d_max):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        self.iterations.append(self.iterations[-1] + 1)
        self.data_likelihood.append(likelihood)
        self.data_opt[0].append(n_contigs)
        self.data_opt[1].append(mean_len)
        self.data_opt[2].append(dist)
        self.data_opt[3].append(slope)
        self.data_opt[4].append(d_max)
        self.draw_plot()


    def on_redraw_timer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)

        #
        if not self.processing:
            self.draw_plot()


    def on_export_button(self, event):
        if self.select != None:
            data = self.data_opt[self.select]
            file_choices = "PNG (*.png)|*.png"

            dlg = wx.FileDialog(
                self,
                message="Save plot as...",
                defaultDir=self.output_folder,
                defaultFile="plot.png",
                wildcard=file_choices,
                style=wx.SAVE)

            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                self.canvas.print_figure(path, dpi=self.dpi)
                fig = pylab.figure(dpi=self.dpi)
                axes = fig.add_subplot(111)
                axes.hist(data)
                axes.set_title('Histogram of ' + self.list_str_opt_param[self.select], size=12)
                axes.set_xlabel(self.list_str_opt_param[self.select], size=8)
                pylab.savefig(os.path.join(self.output_folder, 'hist_data'+self.list_str_opt_param[self.select]+'.pdf'))



if __name__ == "__main__":
    gettext.install("app") # replace with the appropriate catalog name
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MainWindow(None, wx.ID_ANY, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
