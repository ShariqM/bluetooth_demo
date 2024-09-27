import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from functools import partial

import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 50

import tkinter as tk
import numpy as np

def plot(canvas, ax):
    ax.clear()

    # Plot data on Matplotlib Figure
    t = np.arange(0, 2*np.pi, .01)
    n = 0.1 * np.random.randn(len(t))
    ax.plot(t, n + np.sin(t))
    canvas.draw()

def plot_frequency_graph(ax, marker, color, label,
    freqs, values):

    ax.plot(freqs, values, label=label,
        color=color, marker=marker)
    ax.set_xscale('log')
    ax.set_xticks(freqs)
    ax.get_xaxis().set_major_formatter(
        matplotlib.ticker.ScalarFormatter())
    plt.minorticks_off()
    ax.grid('on')

    ax.set_xlim([freqs[0] * 0.8, 1.2*freqs[-1]])
    # ax.set_xlabel("Frequency [Hz]")
    # ax.set_title(f"Audiogram Thresholds")
    plt.legend()

def plot_audiogram(ax, freqs, audiogram, side):
    if side == 'left':
        color = '#8caeff'
        marker = 'x'
    else:
        color = '#ff8684'
        marker = 'o'
    plot_frequency_graph(ax, marker, color, side,
        freqs, audiogram)
    ax.set_ylim([0, 80])
    ax.set_ylabel("PTA Threshold [dB]")
    plt.legend()

def plot_frequency_gain(ax, freqs, speech_dB, gains, MPOs, side):
    # Speech
    marker = None
    color = 'green'
    label = f"Moderate Speech ({side})"
    plot_frequency_graph(ax, marker, color, label,
        freqs, [speech_dB] * len(freqs))

    # Speech + Gain
    marker = 'd'
    color = 'green'
    label = f"Moderate Speech + Gain ({side})"
    plot_frequency_graph(ax, marker, color, label,
        freqs, np.array(gains) + speech_dB)

    # MPO
    marker = '*'
    color = 'black'
    label = f"MPO ({side})"
    plot_frequency_graph(ax, marker, color, label,
        freqs, MPOs)

    ax.set_ylim([30, 120])
    ax.set_ylabel("Volume (dB SPL)")
    plt.legend()

class ControllerState(object):
    def __init__(self, axes, canvases, frequencies):
        self.axes = axes
        self.canvases = canvases
        self.frequencies = frequencies
        self.left_audiogram = [0] * len(frequencies)
        self.right_audiogram = [0] * len(frequencies)

        self.inc_gain_buttons = [0] * len(frequencies)
        self.dec_gain_buttons = [0] * len(frequencies)

        self.default_mpo_dB = 90
        self.default_moderate_dB = 55
        n = len(self.frequencies)

        self.left_mpos = [self.default_mpo_dB] * n
        self.left_loud_gains = [0] * n
        self.left_moderate_gains = [0] * n
        self.left_soft_gains = [0] * n

        self.left_mpo_labels = []
        self.left_loud_gain_labels = []
        self.left_moderate_gain_labels = []
        self.left_soft_gain_labels = []

        self.right_mpos = [self.default_mpo_dB] * n
        self.right_loud_gains = [0] * n
        self.right_moderate_gains = [0] * n
        self.right_soft_gains = [0] * n

        self.right_mpo_labels = []
        self.right_loud_gain_labels = []
        self.right_moderate_gain_labels = []
        self.right_soft_gain_labels = []

        plot_audiogram(self.axes[0][0], self.frequencies,
            self.left_audiogram, 'left')
        plot_audiogram(self.axes[0][1], self.frequencies,
            self.right_audiogram, 'right')

        plot_frequency_gain(self.axes[1][0], self.frequencies,
            self.default_moderate_dB,
            self.left_moderate_gains,
            self.left_mpos, 'left')
        plot_frequency_gain(self.axes[1][1], self.frequencies,
            self.default_moderate_dB,
            self.right_moderate_gains,
            self.right_mpos, 'right')

        self.status_label = None

    def report_info(self, msg):
        self.status_label["text"] = f"Status: {msg}"
        self.status_label["fg"] = "black"

    def report_error(self, msg):
        self.status_label["text"] = f"Status: {msg}"
        self.status_label["fg"] = "red"

    def clear_status(self):
        self.status_label["text"] = "Status:"
        self.status_label["fg"] = "black"

    def bluetooth_connect(self):
        self.report_info("Connecting to Bluetooth...")

    def update_threshold(self, side, freq_i, event):
        x = event.widget.get("1.0", "end-1c")
        if x == "":
            return

        event.widget.tag_add("center", "1.0", "end")

        try:
            new_threshold_dB = int(x)
            self.clear_status()
        except Exception as e:
            self.report_error(f"Non int character entered: {e}")
            return # Non int character entered, e.g. ''

        if new_threshold_dB < 0 or new_threshold_dB > 80:
            self.report_error(f"Threshold out of accepted range.")
            return

        j = 0 if side == 'left' else 1
        ax = self.axes[0][j]
        canvas = self.canvases[0][j]

        ax.clear()

        if side == 'left':
            self.left_audiogram[freq_i] = new_threshold_dB
            plot_audiogram(ax, self.frequencies, self.left_audiogram, side)
        else:
            self.right_audiogram[freq_i] = new_threshold_dB
            plot_audiogram(ax, self.frequencies, self.right_audiogram, side)
        canvas.draw()
        plt.legend()

    def copy_gain_to_labels(self):
        for i in range(len(self.frequencies)):
            self.left_mpo_labels[i]["text"] = str(self.left_mpos[i])
            self.left_soft_gain_labels[i]["text"] = (
                str(self.left_soft_gains[i]))
            self.left_moderate_gain_labels[i]["text"] = (
                str(self.left_moderate_gains[i]))
            self.left_loud_gain_labels[i]["text"] = (
                str(self.left_loud_gains[i]))

        for i in range(len(self.frequencies)):
            self.right_mpo_labels[i]["text"] = str(self.left_mpos[i])
            self.right_soft_gain_labels[i]["text"] = (
                str(self.right_soft_gains[i]))
            self.right_moderate_gain_labels[i]["text"] = (
                str(self.right_moderate_gains[i]))
            self.right_loud_gain_labels[i]["text"] = (
                str(self.right_loud_gains[i]))

    def calculate_gain(self):
        for i in range(len(self.frequencies)):
            self.left_mpos[i] = 90 + (i % 2)
            self.left_soft_gains[i] = self.left_audiogram[i]
            self.left_moderate_gains[i] = (
                int(0.6 * self.left_audiogram[i]))
            self.left_loud_gains[i] = (
                int(0.3 * self.left_audiogram[i]))

        self.axes[1][0].clear()
        plot_frequency_gain(self.axes[1][0],
            self.frequencies,
            self.default_moderate_dB,
            self.left_moderate_gains,
            self.left_mpos, 'left')
        self.canvases[1][0].draw()

        for i in range(len(self.frequencies)):
            self.right_mpos[i] = 90 + (i % 2)
            self.right_soft_gains[i] = self.right_audiogram[i]
            self.right_moderate_gains[i] = (
                int(0.6 * self.right_audiogram[i]))
            self.right_loud_gains[i] = (
                int(0.3 * self.right_audiogram[i]))

        self.axes[1][1].clear()
        plot_frequency_gain(self.axes[1][1],
            self.frequencies,
            self.default_moderate_dB,
            self.right_moderate_gains,
            self.right_mpos, 'right')
        self.canvases[1][1].draw()

        self.copy_gain_to_labels()

    def gain_up(self, side, freq_i):
        assert freq_i >= 0
        frequency = self.frequencies[freq_i]

    def gain_down(self, side, freq_i):
        assert freq_i >= 0
        frequency = self.frequencies[freq_i]

def make_text_impl(root, borderwidth, relief, height,
        width=-1, bg="x", font="x"):
    return tk.Text(root, borderwidth=borderwidth, relief=relief,
        height=height, width=width, bg=bg, font=font)

def make_label_impl(root, borderwidth, relief,
        width=-1, text="", bg="x", font="x"):
    return tk.Label(root, borderwidth=borderwidth, relief=relief,
        width=width, text=text, bg=bg, font=font)

def focus_prev_widget(event):
    event.widget.tk_focusPrev().focus()
    return("break")

def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    return("break")

############
### MAIN ###
############
def main():
    num_rows = 39 + 1
    num_cols = 26 + 1
    # boot.title("Acceptable Noise Level (ANL) Test")

    root = tk.Tk()
    root.title("CAM2 Fitting Software")
    width = 5
    frequencies = [250, 500, 1000, 2000, 3000, 4000, 6000, 8000]
    freq_labels = [250, 500, "1k", "2k", "3k", "4k", "6k", "8k"]

    panel = tk.Label(root, text="CAM2 Fitting Software")

    default_font = "Helvetica 14"
    bold_font = "Helvetica 14 bold"
    ia_light = "#D1E4E4"
    ia_light_grey = "#EEEEEE"
    ia_grey = "#CCCCCC"
    ia_dark  = "#93B4BC"
    ia_white = "#FFFFFF"
    ia_black = "#000000"
    left_blue = "#8caeff"
    right_red = "#ff8684"

    header_columnspan = 3
    header_width = header_columnspan * width

    graph_columnspan = header_columnspan + len(freq_labels)
    graph_rowspan = 12

    default_audiogram = [0] * len(frequencies)
    default_MPOs = [90] * len(frequencies)
    default_gains = [30] * len(frequencies)
    default_moderate_dB = 55

    # Setup figures
    axes = [[], []]
    canvases = [[], []]
    fig_objs = [[], []]
    for i in range(2):
        for j in range(2):
            fig, ax = plt.subplots(figsize=(5, 3.2))
            canvas = FigureCanvasTkAgg(fig, master=root)

            axes[i].append(ax)
            canvases[i].append(canvas)
            fig_objs[i].append(canvas.get_tk_widget())

    controller_state = ControllerState(
        axes, canvases, frequencies)

    make_label = partial(make_label_impl, root, 1, "solid")
    make_text = partial(make_text_impl, root, 1, "solid", 1.4)
    instructions_text = (
        "1) Run ./audiofocus on the AudioFocus Prototoype."
        " 2) Bluetooth Pair this MacBook with AudioFocus (Top Left)."
        " 3) Click Bluetooth connect below to connect to AudioFocus.")
    inst_columnspan = 21
    inst_width = inst_columnspan * width


    for r in range(num_rows):
        for c in range(num_cols):
            rowspan = 1
            columnspan = 1
            obj = tk.Label(root, width=width, text="")
            if r == 0:
                obj = tk.Label(root, width=width, text=f"{c}")
            elif c == 0:
                obj = tk.Label(root, width=width, text=f"{r}")
                # obj = tk.Label(root, width=int(0.5*width), text=f"{r}")
            else:
                if r == 1: # Bluetooth
                    if c == 12:
                        columnspan = header_columnspan
                        obj = make_label(width=header_width,
                            text="Bluetooth", bg=ia_dark, font=bold_font)
                    elif c <= 12-1+header_columnspan:
                        obj = None # Don't overwrite "Bluetooth" header
                    else:
                        pass
                elif r == 2:  # Instructions
                    if c == 3:
                        columnspan = inst_columnspan
                        obj = make_label(width=inst_width,
                            text=instructions_text, bg=ia_grey, font=bold_font)
                    elif c <= 3-1+inst_columnspan:
                        obj = None # Don't overwrite "Bluetooth" header
                    else:
                        pass
                elif r == 3:  # Instructions
                    if c == 12:
                        columnspan = header_columnspan
                        bluetooth_connect_p = partial(
                            controller_state.bluetooth_connect)
                        obj = tk.Button(root, width=header_width,
                            text="Bluetooth Connect",
                            bg=ia_black, font=bold_font,
                            command=bluetooth_connect_p)
                    elif c <= 12-1+inst_columnspan:
                        obj = None # Don't overwrite "Bluetooth" header
                    else:
                        pass
                elif r == 4:  # Status
                    if c == 3:
                        columnspan = inst_columnspan
                        obj = make_label(width=inst_width,
                            text="Status: ", bg=ia_grey, font=bold_font)
                        obj["anchor"] = "w"
                        controller_state.status_label = obj
                    elif c <= 3-1+inst_columnspan:
                        obj = None # Don't overwrite "Bluetooth" header
                    else:
                        pass
                elif r >= 7 and r <= 19:   # Top Row Graphs
                    if c >= 1 and c <= 11:  # Top Left Graph
                        if r == 7 and c == 1:
                            obj = fig_objs[0][0]
                            columnspan = graph_columnspan
                            rowspan = graph_rowspan
                        else:
                            obj = None
                    elif c >= 15 and c <= 15-1+graph_columnspan: # Top Right Graph
                        if r == 7 and c == 15:
                            obj = fig_objs[0][1]
                            columnspan = graph_columnspan
                            rowspan = graph_rowspan
                        else:
                            obj = None
                elif r >= 27 and r <= 39:   # Bottom Row Graphs
                    if c >= 1 and c <= 11:  # Bottom Left Graph
                        if r == 27 and c == 1:
                            obj = fig_objs[1][0]
                            columnspan = graph_columnspan
                            rowspan = graph_rowspan
                        else:
                            obj = None
                    elif c >= 15 and c <= 15-1+graph_columnspan: # Top Right Graph
                        if r == 27 and c == 15:
                            obj = fig_objs[1][1]
                            columnspan = graph_columnspan
                            rowspan = graph_rowspan
                        else:
                            obj = None
                elif r == 5: # Top Row (Thresholds)
                    if c == 1:
                        obj = make_label(width=header_width, text="L",
                            bg=left_blue, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= header_columnspan + len(freq_labels):
                        offset = header_columnspan+1
                        obj = make_label( width=width,
                            text=freq_labels[c-offset], bg=ia_light, font=bold_font)
                    elif c == 12:
                        obj = make_label( width=header_width,
                            text="--Thresholds--", bg=ia_dark, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= 12-1+header_columnspan:
                        obj = None # DOn't overwrite "Threshold" header
                    elif c == 15:
                        obj = make_label( width=header_width, text="R",
                            bg=right_red, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= 15-1+header_columnspan:
                        obj = None # Don't overwrite the R header
                    elif c <= 15-1+header_columnspan+len(freq_labels):
                        offset = 15-1+header_columnspan+1
                        obj = make_label(width=width, bg=ia_light,
                            text=freq_labels[c-offset], font=bold_font)
                    else:
                        pass
                elif r == 6: ### SPL THRESHOLD ####
                    if c == 1:
                        ### LEFT ###
                        obj = make_label( width=header_width,
                            text="SPL Threshold", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= header_columnspan:
                        obj = None # Don't overwrite the SPL header
                    elif c <= header_columnspan + len(freq_labels):
                        offset = header_columnspan+1
                        obj = make_text(width=width, bg=ia_light_grey,
                            font=default_font)
                        obj.tag_configure("center", justify='center')
                        # obj.insert("1.0", "0")
                        obj.tag_add("center", "1.0", "end")
                        side = 'left'
                        update_threshold_p = partial(
                            controller_state.update_threshold, side, c-offset)
                        obj.bind('<KeyRelease>', update_threshold_p)
                        obj.bind('<Tab>', focus_next_widget)
                        obj.bind('<Shift-Tab>', focus_prev_widget)
                        if c == header_columnspan+1:
                            obj.focus() # Start cursor on first left freq.
                    elif c == 15:
                        ### RIGHT ###
                        obj = make_label( width=header_width,
                            text="SPL Threshold", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= 15-1+header_columnspan:
                        obj = None # Don't overwrite the SPL header
                    elif c <= 15-1+header_columnspan+len(freq_labels):
                        offset = 15-1+header_columnspan+1
                        obj = make_text(width=width,
                            bg=ia_light_grey, font=default_font)
                        obj.tag_configure("center", justify='center')
                        # obj.insert("1.0", "0")
                        obj.tag_add("center", "1.0", "end")
                        side = 'right'
                        update_threshold_p = partial(
                            controller_state.update_threshold, side, c-offset)
                        obj.bind('<KeyRelease>', update_threshold_p)
                        obj.bind('<Tab>', focus_next_widget)
                        obj.bind('<Shift-Tab>', focus_prev_widget)
                    else:
                        pass
                elif r == 20: # Bottom Row (Gains)
                    if c == 1:
                        obj = make_label( width=header_width, text="L",
                            bg=left_blue, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= header_columnspan + len(freq_labels):
                        offset = header_columnspan+1
                        obj = make_label( width=width,
                            text=freq_labels[c-offset], bg=ia_light, font=bold_font)
                    elif c == 12:
                        obj = make_label( width=header_width,
                            text="----Gains----", bg=ia_dark, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= 12-1+header_columnspan:
                        obj = None # DOn't overwrite "Threshold" header
                    elif c == 15:
                        obj = make_label( width=header_width, text="R",
                            bg=right_red, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= 15-1+header_columnspan:
                        obj = None # Don't overwrite the R header
                    elif c <= 15-1+header_columnspan+len(freq_labels):
                        offset = 15-1+header_columnspan+1
                        obj = make_label( width=width,
                            text=freq_labels[c-offset], bg=ia_light, font=bold_font)
                    else:
                        pass
                elif r == 21: # MPO
                    if c == 1:
                        obj = make_label( width=header_width,
                            text="MPO", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= header_columnspan+len(frequencies):
                        obj = make_label(width=width,
                            text="0", bg=ia_grey, font=default_font)
                        controller_state.left_mpo_labels.append(obj)
                    elif c <= 12:
                        calculate_gain_p = partial(
                            controller_state.calculate_gain)
                        columnspan = header_columnspan
                        obj = tk.Button(root, width=header_width,
                            text="Calculate Gains",
                            bg=ia_black, font=bold_font,
                            command=calculate_gain_p)
                    elif c <= 12-1+header_columnspan:
                        obj = None # Don't overwrite the g header
                    elif c == 15:
                        obj = make_label( width=header_width,
                            text="MPO", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= 15-1+header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= 15-1+header_columnspan+len(freq_labels):
                        obj = make_label(width=width,
                            text="0", bg=ia_grey, font=default_font)
                        controller_state.right_mpo_labels.append(obj)
                    else:
                        pass
                elif r == 22: # Loud
                    if c == 1:
                        obj = make_label( width=header_width,
                            text="Loud", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= header_columnspan+len(frequencies):
                        obj = make_label(width=width,
                            text="0", bg=ia_grey, font=default_font)
                        controller_state.left_loud_gain_labels.append(obj)
                    elif c == 15:
                        obj = make_label( width=header_width,
                            text="Loud", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= 15-1+header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= 15-1+header_columnspan+len(freq_labels):
                        obj = make_label(width=width,
                            text="0", bg=ia_grey, font=default_font)
                        controller_state.right_loud_gain_labels.append(obj)
                    else:
                        pass
                elif r == 23: # Moderate
                    if c == 1:
                        obj = make_label( width=header_width,
                            text="Moderate", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= header_columnspan+len(frequencies):
                        obj = make_label(width=width,
                            text="0", bg=ia_grey, font=default_font)
                        controller_state.left_moderate_gain_labels.append(obj)
                    elif c == 15:
                        obj = make_label( width=header_width,
                            text="Moderate", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= 15-1+header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= 15-1+header_columnspan+len(freq_labels):
                        obj = make_label(width=width,
                            text="0", bg=ia_grey, font=default_font)
                        controller_state.right_moderate_gain_labels.append(obj)
                    else:
                        pass
                elif r == 24: # Soft
                    if c == 1:
                        obj = make_label( width=header_width,
                            text="Soft", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= header_columnspan+len(frequencies):
                        obj = make_label(width=width,
                            text="0", bg=ia_grey, font=default_font)
                        controller_state.left_soft_gain_labels.append(obj)
                    elif c == 15:
                        obj = make_label(width=header_width,
                            text="Soft", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= 15-1+header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= 15-1+header_columnspan+len(freq_labels):
                        obj = make_label(width=width,
                            text="0", bg=ia_grey, font=default_font)
                        controller_state.right_soft_gain_labels.append(obj)
                    else:
                        pass
                elif r == 25: # Increase Gain
                    if c == 1:
                        obj = make_label(width=header_width,
                            text="Increase Gain", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= header_columnspan + len(freq_labels):
                        offset = header_columnspan+1
                        side = 'left'
                        gain_up_p = partial(
                            controller_state.gain_up, side, c-offset)
                        obj = tk.Button(root, width=width, text="+",
                            bg=ia_black, font=bold_font,
                            command=gain_up_p)
                    elif c == 15:
                        obj = make_label( width=header_width,
                            text="Increase Gain", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= 15-1+header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= 15-1+header_columnspan+len(freq_labels):
                        offset = 15-1+header_columnspan+1
                        side = 'right'
                        gain_up_p = partial(
                            controller_state.gain_up, side, c-offset)
                        obj = tk.Button(root, width=width, text="+",
                            bg=ia_black, font=bold_font,
                            command=gain_up_p)
                    else:
                        pass

                elif r == 26: # Decrease Gain
                    if c == 1:
                        obj = make_label( width=header_width,
                            text="Decrease Gain", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= header_columnspan + len(freq_labels):
                        offset = header_columnspan+1
                        side = 'left'
                        gain_down_p = partial(
                            controller_state.gain_down, side, c-offset)
                        obj = tk.Button(root, width=width, text="-",
                            bg=ia_black, font=bold_font,
                            command=gain_down_p)
                    elif c == 15:
                        obj = make_label( width=header_width,
                            text="Decrease Gain", bg=ia_light, font=bold_font)
                        columnspan = header_columnspan
                    elif c <= 15-1+header_columnspan:
                        obj = None # Don't overwrite the L header
                    elif c <= 15-1+header_columnspan+len(freq_labels):
                        offset = 15-1+header_columnspan+1
                        side = 'right'
                        gain_down_p = partial(
                            controller_state.gain_down, side, c-offset)
                        obj = tk.Button(root, width=width, text="-",
                            bg=ia_black, font=bold_font,
                            command=gain_down_p)
                    else:
                        pass

            if obj is not None:
                obj.configure(bd=0)
                obj.configure(highlightthickness=0)
                obj.grid(row=r, column=c, rowspan=rowspan,
                    columnspan=columnspan, padx=0, pady=0, sticky="nsew")


    root.mainloop()

if __name__ == "__main__":
    main()
