clear all;
close all;
instrreset;

% Create a figure to capture key press events
f = figure('KeyPressFcn', @(src, event) assignin('base', 'keyPressed', event.Key));
drawnow;

% Initialize keyPressed variable
keyPressed = '';

disp('Press Ctrl+C or press "q" in the figure window to stop collecting data!');

% Initialize IMU serial port
s_imu = serial('com13', 'baudrate', 9600);
fopen(s_imu);

% Initialize GPS serial port
s_gps = serial('COM6', 'BaudRate', 115200);
fopen(s_gps);

% Initialize OBD serial port
s_obd = serial('COM7', 'BaudRate', 9600);
fopen(s_obd);

% Initialize LiDAR
lidar = velodynelidar('VLP16');
start(lidar);

% Pre-allocate arrays for LiDAR point clouds and timestamps
pclouds = {};
unix_timestamps_lidar = [];

% Set LiDAR timing variables
lidar_last_time = 0;
lidar_interval = 1 / 10; % 10 Hz frame rate

% Initialize LiDAR frame counter and data index
lidar_frame_count = 0;
lidar_data_index = 0;
lidar_start_time = tic;

% Pre-allocate memory for sensor data
nSamplesIMU = 90000; % 30 Hz * 60 seconds/minute * 50 minutes
nSamplesGPS = 15000; % 5 Hz * 60 seconds/minute * 50 minutes
nSamplesOBD = 15000; % 5 Hz * 60 seconds/minute * 50 minutes

% IMU data arrays
imu_acceleration = zeros(nSamplesIMU, 3);
imu_angular_velocity = zeros(nSamplesIMU, 3);
imu_angle = zeros(nSamplesIMU, 3);
imu_timestamps = zeros(nSamplesIMU, 1); % Unix time

% GPS data arrays
gps_data = zeros(nSamplesGPS, 9);
gps_timestamps = zeros(nSamplesGPS, 1); % Unix time

% OBD data arrays
obd_data = zeros(nSamplesOBD, 5);
obd_timestamps = zeros(nSamplesOBD, 1); % Unix time

% Set sensor sampling intervals (Hz)
imu_interval = 1 / 50; % 50 Hz for IMU
gps_interval = 1 / 5; % 5 Hz for GPS
obd_interval = 1 / 5; % 5 Hz for OBD

% Initialize sensor frame counters and timestamps
imu_frame_count = 0;
gps_frame_count = 0;
obd_frame_count = 0;

imu_data_index = 0;
gps_data_index = 0;
obd_data_index = 0;

% Variables for frame rate display timing
frame_rate_display_interval = 5; % seconds
imu_last_display_time = 0;
gps_last_display_time = 0;
lidar_last_display_time = 0;
obd_last_display_time = 0;

% Initialize IMU sensor readings
imu_acc = [0; 0; 0];
imu_ang_velocity = [0; 0; 0];
imu_angle_reading = [0; 0; 0];

% Main data collection loop
while true
    current_time = posixtime(datetime('now'));
    
    % Read IMU data at 50 Hz
    if current_time - imu_last_time >= imu_interval
        imu_last_time = current_time;
        
        % Read IMU data
        imu_header = fread(s_imu, 2, 'uint8');
        if (imu_header(1) ~= uint8(85))
            continue;
        end
        
        switch imu_header(2)
            case 81 % Acceleration
                imu_acc = fread(s_imu, 3, 'int16') / 32768 * 16;
            case 82 % Angular velocity
                imu_ang_velocity = fread(s_imu, 3, 'int16') / 32768 * 2000;
            case 83 % Angle
                imu_angle_reading = fread(s_imu, 3, 'int16') / 32768 * 180;
        end
        
        % Store IMU data
        imu_frame_count = imu_frame_count + 1;
        imu_data_index = imu_data_index + 1;
        imu_acceleration(imu_data_index, :) = imu_acc';
        imu_angular_velocity(imu_data_index, :) = imu_ang_velocity';
        imu_angle(imu_data_index, :) = imu_angle_reading';
        imu_timestamps(imu_data_index) = current_time;
        
        % Read end of IMU data packet
        fread(s_imu, 3, 'uint8');
    end
    
    % Read GPS data at 5 Hz
    if current_time - gps_last_time >= gps_interval
        gps_last_time = current_time;
        
        % Read GPS data
        gps_raw_data = fscanf(s_gps);
        gps_parsed_data = str2double(strsplit(gps_raw_data, ','));
        
        if length(gps_parsed_data) == 9
            gps_frame_count = gps_frame_count + 1;
            gps_data_index = gps_data_index + 1;
            gps_data(gps_data_index, :) = gps_parsed_data;
            gps_timestamps(gps_data_index) = current_time;
        end
    end

    % Read OBD data at 5 Hz
    if current_time - obd_last_time >= obd_interval
        obd_last_time = current_time;
        
        % Read OBD data
        obd_raw_data = fscanf(s_obd);
        obd_parsed_data = str2double(strsplit(obd_raw_data, ','));
        
        if length(obd_parsed_data) == 5
            obd_frame_count = obd_frame_count + 1;
            obd_data_index = obd_data_index + 1;
            obd_data(obd_data_index, :) = obd_parsed_data;
            obd_timestamps(obd_data_index) = current_time;
        end
    end

    % Read LiDAR data at 10 Hz
    if current_time - lidar_last_time >= lidar_interval
        lidar_last_time = current_time;
        
        % Read and store LiDAR point cloud and timestamp
        [point_cloud, timestamp] = read(lidar, 'latest');
        lidar_frame_count = lidar_frame_count + 1;
        lidar_data_index = lidar_data_index + 1;
        
        unix_time_lidar = posixtime(timestamp);
        pclouds{lidar_data_index} = point_cloud;
        unix_timestamps_lidar(lidar_data_index) = unix_time_lidar;
    end
    
    % Display frame rates every 5 seconds
    if current_time - imu_last_display_time >= frame_rate_display_interval
        fprintf('IMU frame rate: %.2f Hz\n', imu_frame_count / frame_rate_display_interval);
        imu_frame_count = 0;
        imu_last_display_time = current_time;
    end
    
    if current_time - gps_last_display_time >= frame_rate_display_interval
        fprintf('GPS frame rate: %.2f Hz\n', gps_frame_count / frame_rate_display_interval);
        gps_frame_count = 0;
        gps_last_display_time = current_time;
    end
    
    if current_time - obd_last_display_time >= frame_rate_display_interval
        fprintf('OBD frame rate: %.2f Hz\n', obd_frame_count / frame_rate_display_interval);
        obd_frame_count = 0;
        obd_last_display_time = current_time;
    end
    
    if current_time - lidar_last_display_time >= frame_rate_display_interval
        fprintf('LiDAR frame rate: %.2f Hz\n', lidar_frame_count / frame_rate_display_interval);
        lidar_frame_count = 0;
        lidar_last_display_time = current_time;
    end
    
    % Check for 'q' key press to exit loop
    keyPressed = evalin('base', 'keyPressed');
    if strcmp(keyPressed, 'q')
        disp('Loop halted by user.');
        break;
    end
    
    % Process event queue to ensure smooth GUI operation
    drawnow;
end

% Clean up: Close serial ports and stop LiDAR acquisition
fclose(s_imu);
fclose(s_gps);
fclose(s_obd);
stop(lidar);

% Clear LiDAR object and close the figure window
clear lidar;
close(f);
