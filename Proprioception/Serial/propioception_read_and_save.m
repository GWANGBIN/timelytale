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

% Initialize IMU sensor readings
imu_acc = [0; 0; 0];
imu_ang_velocity = [0; 0; 0];
imu_angle_reading = [0; 0; 0];

% Main data collection loop for interoception
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
