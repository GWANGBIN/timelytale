clear all;
close all;
instrreset;

% Create a figure to capture key press events
f = figure('KeyPressFcn', @(src, event) assignin('base', 'keyPressed', event.Key));
drawnow;

% Initialize keyPressed variable
keyPressed = '';

disp('Press Ctrl+C or press "q" in the figure window to stop collecting LiDAR data!');

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

% Main data collection loop for LiDAR
while true
    current_time = posixtime(datetime('now'));
    
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
    
    % Display LiDAR frame rates every 5 seconds
    if current_time - lidar_last_time >= 5
        fprintf('LiDAR frame rate: %.2f Hz\n', lidar_frame_count / 5);
        lidar_frame_count = 0;
    end
    
    % Check for 'q' key press to exit loop
    keyPressed = evalin('base', 'keyPressed');
    if strcmp(keyPressed, 'q')
        disp('LiDAR loop halted by user.');
        break;
    end
    
    % Process event queue to ensure smooth GUI operation
    drawnow;
end

% Clean up: stop LiDAR acquisition
stop(lidar);

% Clear LiDAR object and close the figure window
clear lidar;
close(f);

% Save LiDAR point clouds and Unix timestamps to a .mat file
save('dooyoung_lidar.mat', 'pclouds', 'unix_timestamps_lidar', '-v7.3');
