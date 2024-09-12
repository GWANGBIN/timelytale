############
#
# Copyright (c) 2022 MIT CSAIL and Joseph DelPreto
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# See https://action-net.csail.mit.edu for more usage information.
# Created 2021-2022 for the MIT ActionNet project by Joseph DelPreto [https://josephdelpreto.com].
#
############

from sensor_streamers.SensorStreamer import SensorStreamer
from visualizers.LinePlotVisualizer import LinePlotVisualizer
from visualizers.HeatmapVisualizer import HeatmapVisualizer
from visualizers.VideoVisualizer import VideoVisualizer

import socket
from collections import OrderedDict
import traceback
import time

################################################
################################################
# A template class for implementing a new sensor.
################################################
################################################
class TobiiStreamer(SensorStreamer):

    ########################
    ###### INITIALIZE ######
    ########################

    # Initialize the sensor streamer.
    # @param visualization_options Can be used to specify how data should be visualized.
    #   It should be a dictionary with the following keys:
    #     'visualize_streaming_data': Whether or not visualize any data during streaming.
    #     'update_period_s': How frequently to update the visualizations during streaming.
    #     'visualize_all_data_when_stopped': Whether to visualize a summary of data at the end of the experiment.
    #     'wait_while_visualization_windows_open': After the experiment finishes, whether to automatically close visualization windows or wait for the user to close them.
    #     'classes_to_visualize': [optional] A list of class names that should be visualized (others will be suppressed).  For example, ['TouchStreamer', 'MyoStreamer']
    #     'use_composite_video': Whether to combine visualizations from multiple streamers into a single tiled visualization.  If not, each streamer will create its own window.
    #     'composite_video_filepath': If using composite video, can specify a filepath to save it as a video.
    #     'composite_video_layout': If using composite video, can specify which streamers should be included and how to arrange them. See some of the launch files for examples.
    # @param log_player_options Can be used to replay data from an existing log instead of streaming real-time data.
    #   It should be a dictionary with the following keys:
    #     'log_dir': The directory with log data to replay (should directly contain the HDF5 file).
    #     'pause_to_replay_in_realtime': If reading from the logs is faster than real-time, can wait between reads to keep the replay in real time.
    #     'skip_timesteps_to_replay_in_realtime': If reading from the logs is slower than real-time, can skip timesteps as needed to remain in real time.
    #     'load_datasets_into_memory': Whether to load all data into memory before starting the replay, or whether to read from the HDF5 file each timestep.
    # @param print_status Whether or not to print messages with level 'status'
    # @param print_debug Whether or not to print messages with level 'debug'
    # @param log_history_filepath A filepath to save log messages if desired.
    def __init__(self,
                 log_player_options=None, visualization_options=None,
                 print_status=True, print_debug=False, log_history_filepath=None):
        SensorStreamer.__init__(self, streams_info=None,
                                visualization_options=visualization_options,
                                log_player_options=log_player_options,
                                print_status=print_status, print_debug=print_debug,
                                log_history_filepath=log_history_filepath)

        ## TODO: Add a tag here for your sensor that can be used in log messages.
        #        Try to keep it under 10 characters long.
        #        For example, 'myo' or 'scale'.
        self._log_source_tag = 'TobbiGlasses'

        ## TODO: Initialize any state that your sensor needs.
        # Initialize counts
        self._num_segments = None  # Neuron Studio sensor에서 사용하려는 segment 개수 정의함

        # Initialize state
        self._buffer = b''
        self._buffer_read_size = 1024
        self._socket = None
        self._tobii_sample_index = None  # The current NeuronStudio timestep being processed (each timestep will send multiple messages)
        self._tobii_message_start_time_s = None  # When a NeuronStudio message was first received
        self._tobii_timestep_receive_time_s = None  # When the first NeuronStudio message for a NeuronStudio timestep was received

        # Specify the NeuronStudio streaming configuration.
        self._tobii_network_protocol = 'udp'
        self._tobii_network_ip = '192.168.1.10'
        self._tobii_network_port = 5006

        fps_video_world = None

        ## TODO: Add devices and streams to organize data from your sensor.
        #        Data is organized as devices and then streams.
        #        For example, a Myo device may have streams for EMG and Acceleration.
        #        If desired, this could also be done in the connect() method instead.
        self.add_stream(device_name='tobii-eyetracking',
                        stream_name='gaze-values',
                        data_type='float32',
                        sample_size=[8],
                        # the size of data saved for each timestep; here, we expect a 2-element vector per timestep
                        sampling_rate_hz=50,  # the expected sampling rate for the stream
                        extra_data_info={},
                        # can add extra information beyond the data and the timestamp if needed (probably not needed, but see MyoStreamer for an example if desired)
                        # Notes can add metadata about the stream,
                        #  such as an overall description, data units, how to interpret the data, etc.
                        # The SensorStreamer.metadata_data_headings_key is special, and is used to
                        #  describe the headings for each entry in a timestep's data.
                        #  For example - if the data was saved in a spreadsheet with a row per timestep, what should the column headings be.
                        data_notes=OrderedDict([
                            ('Description', 'Gaze data'
                             ),
                            ('Units', ''),
                            (SensorStreamer.metadata_data_headings_key,
                             ['ContentsTime', 'gaze2dX', 'gaze2dY', 'gaze3dX', 'gaze3dY',
                              'gaze3dZ', 'leftpupil', 'rightpupil']),
                        ]))
        self.add_stream(device_name='tobii-acc',
                        stream_name='mss-values',
                        data_type='float32',
                        sample_size=[4],
                        # the size of data saved for each timestep; here, we expect a 2-element vector per timestep
                        sampling_rate_hz=50,  # the expected sampling rate for the stream
                        extra_data_info={},
                        # can add extra information beyond the data and the timestamp if needed (probably not needed, but see MyoStreamer for an example if desired)
                        # Notes can add metadata about the stream,
                        #  such as an overall description, data units, how to interpret the data, etc.
                        # The SensorStreamer.metadata_data_headings_key is special, and is used to
                        #  describe the headings for each entry in a timestep's data.
                        #  For example - if the data was saved in a spreadsheet with a row per timestep, what should the column headings be.
                        data_notes=OrderedDict([
                            ('Description', 'Joint Pos/Angle data from the hip joint.'
                             ),
                            ('Units', ''),
                            (SensorStreamer.metadata_data_headings_key,
                             ['WebTime', 'accX', 'accY', 'accZ',
                              ]),
                        ]))

        self.add_stream(device_name='tobii-gyro',
                        stream_name='mss-values',
                        data_type='float32',
                        sample_size=[4],
                        # the size of data saved for each timestep; here, we expect a 2-element vector per timestep
                        sampling_rate_hz=50,  # the expected sampling rate for the stream
                        extra_data_info={},
                        # can add extra information beyond the data and the timestamp if needed (probably not needed, but see MyoStreamer for an example if desired)
                        # Notes can add metadata about the stream,
                        #  such as an overall description, data units, how to interpret the data, etc.
                        # The SensorStreamer.metadata_data_headings_key is special, and is used to
                        #  describe the headings for each entry in a timestep's data.
                        #  For example - if the data was saved in a spreadsheet with a row per timestep, what should the column headings be.
                        data_notes=OrderedDict([
                            ('Description', 'Joint Pos/Angle data from the hip joint.'
                             ),
                            ('Units', ''),
                            (SensorStreamer.metadata_data_headings_key,
                             ['WebTime','gyroX', 'gyroY', 'gyroZ',
                              ]),
                        ]))
        self.add_stream(device_name='tobii-magneto',
                        stream_name='mss-values',
                        data_type='float32',
                        sample_size=[4],
                        # the size of data saved for each timestep; here, we expect a 2-element vector per timestep
                        sampling_rate_hz=50,  # the expected sampling rate for the stream
                        extra_data_info={},
                        # can add extra information beyond the data and the timestamp if needed (probably not needed, but see MyoStreamer for an example if desired)
                        # Notes can add metadata about the stream,
                        #  such as an overall description, data units, how to interpret the data, etc.
                        # The SensorStreamer.metadata_data_headings_key is special, and is used to
                        #  describe the headings for each entry in a timestep's data.
                        #  For example - if the data was saved in a spreadsheet with a row per timestep, what should the column headings be.
                        data_notes=OrderedDict([
                            ('Description', 'Joint Pos/Angle data from the hip joint.'
                             ),
                            ('Units', ''),
                            (SensorStreamer.metadata_data_headings_key,
                             ['WebTime', 'magnetoX', 'magnetoY', 'magnetoZ'
                              ]),
                        ]))
        # self.add_stream(device_name='eye-tracking-video-world', stream_name='frame_timestamp',
        #                 data_type='float64', sample_size=(1),
        #                 sampling_rate_hz=fps_video_world, extra_data_info=None,
        #                 data_notes=OrderedDict([
        #                     ('Description', 'eyetracking video'
        #                      ),
        #                     ('Units', ''),
        #                     (SensorStreamer.metadata_data_headings_key,
        #                      ['video', 'frame'
        #                       ]),
        #                 ]))
    #######################################
    # Connect to the sensor.
    # @param timeout_s How long to wait for the sensor to respond.
    def _connect(self, timeout_s=10):
        # Open a socket to the NeuronStudio network stream
        ## TODO: Add code for connecting to your sensor.
        #        Then return True or False to indicate whether connection was successful.

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._socket.settimeout(5)  # timeout for all socket operations, such as receiving if the NeuronStuido network stream is inactive
        option = 1 #SO_REUSEADDR의 옵션 값을 TRUE로

        # self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self._tobii_network_ip, self._tobii_network_port))
        self._log_status('Successfully connected to the NueronStudio streamer.')
        return True

    #######################################
    ###### INTERFACE WITH THE SENSOR ######
    #######################################

    ## TODO: Add functions to control your sensor and acquire data.
    #        [Optional but probably useful]

    # A function to read a timestep of data for the first stream.
    def _read_data(self):
        # For example, may want to return the data for the timestep
        #  and the time at which it was received.
        try:
            bytesAddressPair = self._socket.recvfrom(self._buffer_read_size)
        except:
            self._log_error('\n\n***ERROR reading from PnsStreamer:\n%s\n' % traceback.format_exc())
            time.sleep(1)
            return (None, None, None)
        message = bytesAddressPair[0].decode("utf-8")
        data = message.split(',')
        # print(len(data))
        # print(data)
        # print(float(data[9].replace('[', '').replace(']', '').split("'")[1]))
        # print(len(data))
        try:
            # Extract the device timestamp.

            time_s = float(data[0].replace('[', '').replace(']', '').split("'")[1])
            # print(data)
            # Joint Data
            eyetrackingData = []
            imuData = []

            if len(data) == 18:
                imuData.append(float(data[4].split('[',)[1].replace(']', '').split("'")[1]))
                imuData.append(float(data[5].replace('[', '').split("'")[1]))
                imuData.append(float(data[6].split("'")[1]))
                imuData.append(float(data[7].replace(']', '').split("'")[1]))
                imuData.append(float(data[9].split('[',)[1].replace(']', '').split("'")[1]))
                imuData.append(float(data[10].replace('[', '').split("'")[1]))
                imuData.append(float(data[11].split("'")[1]))
                imuData.append(float(data[12].replace(']', '').split("'")[1]))
                imuData.append(float(data[14].split('[',)[1].replace(']', '').split("'")[1]))
                imuData.append(float(data[15].replace('[', '').split("'")[1]))
                imuData.append(float(data[16].split("'")[1]))
                imuData.append(float(data[17].replace(']', '').split("'")[1]))

                eyetrackingData = [0, 0, 0, 0, 0, 0, 0, 0]

            elif len(data) == 29:
                eyetrackingData.append(float(data[2].split('[',)[1].replace(']', '').split("'")[1]))
                eyetrackingData.append(float(data[4].replace('[', '').split("'")[1]))
                eyetrackingData.append(float(data[5].replace(']', '').split("'")[1]))
                eyetrackingData.append(float(data[7].replace('[', '').split("'")[1]))
                eyetrackingData.append(float(data[8].split("'")[1]))
                eyetrackingData.append(float(data[9].replace(']', '').split("'")[1]))
                if data[11] == ' []':
                    eyetrackingData.append(0)
                else:
                    eyetrackingData.append(float(data[11].replace('[', '').replace(']', '').split("'")[1]))
                if data[13] == ' []':
                    eyetrackingData.append(0)
                else:
                    eyetrackingData.append(float(data[13].replace('[', '').replace(']', '').split("'")[1]))

                # print(eyetrackingData)

                imuData.append(float(data[15].split('[',)[1].replace(']', '').split("'")[1]))
                imuData.append(float(data[16].replace('[', '').split("'")[1]))
                imuData.append(float(data[17].split("'")[1]))
                imuData.append(float(data[18].replace(']', '').split("'")[1]))
                imuData.append(float(data[20].split('[',)[1].replace(']', '').split("'")[1]))
                imuData.append(float(data[21].replace('[', '').split("'")[1]))
                imuData.append(float(data[22].split("'")[1]))
                imuData.append(float(data[23].replace(']', '').split("'")[1]))
                imuData.append(float(data[25].split('[',)[1].replace(']', '').split("'")[1]))
                imuData.append(float(data[26].replace('[', '').split("'")[1]))
                imuData.append(float(data[27].split("'")[1]))
                imuData.append(float(data[28].replace(']', '').split("'")[1]))

            return (time_s, eyetrackingData, imuData)

        except IndexError:
            return (None, None, None)


    #####################
    ###### RUNNING ######
    #####################

    ## TODO: Continuously read data from your sensor.
    # Loop until self._running is False.
    # Acquire data from your sensor as desired, and for each timestep
    #  call self.append_data(device_name, stream_name, time_s, data).
    def _run(self):
        try:
            while self._running:
                # Read and store data for stream 1.
                (time_s, eyetrackingData, imuData) = self._read_data()
                # print(len(eyetrackingData))
                # print(len(imuData))

                if time_s is not None:
                    self.append_data('tobii-acc', 'mss-values', time_s, imuData[0:4])
                    self.append_data('tobii-gyro', 'mss-values', time_s, imuData[4:8])
                    self.append_data('tobii-magneto', 'mss-values', time_s, imuData[8:12])
                    self.append_data('tobii-eyetracking', 'gaze-values', time_s, eyetrackingData)

        except KeyboardInterrupt:  # The program was likely terminated
            pass
        except:
            self._log_error('\n\n***ERROR RUNNING MoticonStreamer:\n%s\n' % traceback.format_exc())
        finally:
            ## TODO: Disconnect from the sensor if desired.
            self._socket.close()

    # Clean up and quit
    def quit(self):
        ## TODO: Add any desired clean-up code.
        self._log_debug('NueronStudioStreamer quitting')
        self._socket.close()
        SensorStreamer.quit(self)

    ###########################
    ###### VISUALIZATION ######
    ###########################

    # Specify how the streams should be visualized.
    # Return a dict of the form options[device_name][stream_name] = stream_options
    #  Where stream_options is a dict with the following keys:
    #   'class': A subclass of Visualizer that should be used for the specified stream.
    #   Any other options that can be passed to the chosen class.
    def get_default_visualization_options(self, visualization_options=None):
        # Start by not visualizing any streams.
        processed_options = { }

        for (device_name, device_info) in self._streams_info.items():
            processed_options.setdefault(device_name, {})
            for (stream_name, stream_info) in device_info.items():
                processed_options[device_name].setdefault(stream_name, {'class': None})

        ## TODO: Specify whether some streams should be visualized.
        #        Examples of a line plot and a heatmap are below.
        #        To not visualize data, simply omit the following code and just leave each streamer mapped to the None class as shown above.
        # Use a line plot to visualize the weight.
        processed_options['tobii-acc']['mss-values'] = \
            {'class': LinePlotVisualizer,
               'single_graph': True,   # Whether to show each dimension on a subplot or all on the same plot.
               'plot_duration_s': 15,  # The timespan of the x axis (will scroll as more data is acquired).
               'downsample_factor': 1,  # Can optionally downsample data before visualizing to improve performance.
             }
        processed_options['tobii-eyetracking']['gaze-values'] = \
            {'class': LinePlotVisualizer,
             'single_graph': True,  # Whether to show each dimension on a subplot or all on the same plot.
             'plot_duration_s': 15,  # The timespan of the x axis (will scroll as more data is acquired).
             'downsample_factor': 1,  # Can optionally downsample data before visualizing to improve performance.
             }

        processed_options['tobii-gyro']['mss-values'] = \
            {'class': LinePlotVisualizer,
             'single_graph': True,  # Whether to show each dimension on a subplot or all on the same plot.
             'plot_duration_s': 15,  # The timespan of the x axis (will scroll as more data is acquired).
             'downsample_factor': 1,  # Can optionally downsample data before visualizing to improve performance.
             }

        processed_options['tobii-magneto']['mss-values'] = \
            {'class': LinePlotVisualizer,
             'single_graph': True,  # Whether to show each dimension on a subplot or all on the same plot.
             'plot_duration_s': 15,  # The timespan of the x axis (will scroll as more data is acquired).
             'downsample_factor': 1,  # Can optionally downsample data before visualizing to improve performance.
             }

        # Override the above defaults with any provided options.
        if isinstance(visualization_options, dict):
            for (device_name, device_info) in self._streams_info.items():
                if device_name in visualization_options:
                    device_options = visualization_options[device_name]
                    # Apply the provided options for this device to all of its streams.
                    for (stream_name, stream_info) in device_info.items():
                        for (k, v) in device_options.items():
                            processed_options[device_name][stream_name][k] = v

        return processed_options


#####################
###### TESTING ######
#####################
if __name__ == '__main__':

    # Configuration.
    duration_s = 30

    # Connect to the device(s).
    tobii_streamer = TobiiStreamer(print_status=True, print_debug=False)
    tobii_streamer.connect()

    # Run for the specified duration and periodically print the sample rate.
    print('\nRunning for %gs!' % duration_s)
    tobii_streamer.run()
    start_time_s = time.time()
    try:
        while time.time() - start_time_s < duration_s:
            time.sleep(2)
            # Print the sampling rates.
            msg = ' Duration: %6.2fs' % (time.time() - start_time_s)
            for device_name in tobii_streamer.get_device_names():
                stream_names = tobii_streamer.get_stream_names(device_name=device_name)
                for stream_name in stream_names:
                    num_timesteps = tobii_streamer.get_num_timesteps(device_name, stream_name)
                    msg += ' | %s-%s: %6.2f Hz (%4d Timesteps)' % \
                           (device_name, stream_name, ((num_timesteps) / (time.time() - start_time_s)), num_timesteps)
            print(msg)
    except:
        pass

    # Stop the streamer.
    tobii_streamer.stop()
    print('\n' * 2)
    print('=' * 75)
    print('Done!')
    print('\n' * 2)
















