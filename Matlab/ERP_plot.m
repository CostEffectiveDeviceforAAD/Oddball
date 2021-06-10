
clear all
close all
clc

sr = 125;

% Load raw data & trigger
% eeg_data = load('EEG_0609.mat'); % EEG trace
% trg_data = load('A_0609.mat'); % trigger trace

filename = '01_0609.xlsx';
All = xlsread(filename);
eeg_data = -All(:,1:16);
trg_data = All(:,17:18);

% invert
% for i = 1:8
% eeg_data(:,i) = -eeg_data(:,i);
% end

% Select block data
block = 1;   % block

% Import
% raw = squeeze(eeg_data.EEG(block,:,:));   % times by channel
% trg = squeeze(trg_data.AUX(block,:,:));

% Select sta & tar
standard_trg = trg_data(:,1);
detect_trg = trg_data(:,2);
% target_trg = trg(:,3);

% Channel labeling
%ch_name_cyton = ["Fp1","Fz","C3","C4","P7","P8","O1","O2","Cz","Pz","F3","F4","T7","T8","P3","P4"]; % recorded location -
ch_name = ["Fp1","F3","Fz","F4","T7","C3","Cz","C4","T8","P7","P3","Pz","P4","P8","O1","O2"]; % gui location

% % Change channel location for eeglab GUI
ch_num = [1,11, 2, 12, 13, 3, 9, 4, 14, 5, 15, 10, 16, 6, 7, 8];
for i = 1:16
    eeg(:,i) = eeg_data(:,ch_num(i));
end

% Set
ch = size(eeg,2); % The number of channel
ti = size(eeg,1); % time length

%% Preprocessing
%% Filter

% Filter design  - filt order default = 3*fix(srate/locutoff) = 375
design = designfilt('bandpassfir', 'FilterOrder',400, ...
    'CutoffFrequency1', 1, 'CutoffFrequency2', 30,...
    'SampleRate', 125);

% Filter design plot
%fvtool(design);

eeg_filt = filtfilt(design, eeg);


%% ICA with GUI

save('data.mat', 'eeg_filt');
eeglab

%% ICA data import
% after components removal

eeg_ica = EEG.data';
save('1_ica.mat', 'eeg_ica');

%% pre
%  per channel
for j = 1:ch
    m = mean(eeg_ica(:,j));
    eeg_ch(:,j) = eeg_ica(:,j) - m;
end

% Common Average Reference
for t = 1:ti
    m = mean(eeg_ch(t,[5 9]));
    eeg_pre(t,:) = eeg_ch(t,:) - m;
end

%% Save data
save('1_eeg_pre_2.mat', 'eeg_pre');

%% EEG Plot
L = length(eeg_pre);
t = linspace(0,L/sr,L); % time trace

figure
for i = 1:ch
    title(['block ' num2str(block)])
%     plot(t,eeg_trc_pre_1(:,i) + (i-1)*5);
    plot(t,eeg_pre(:,i)); hold on
    %xlim([0 302])
end

%% Trigger
L = length(eeg_pre);
t = linspace(0,L/sr,L); % time trace

% if index > 3.14 = 1, then index < 3.14 = 0
f_detect_trg = (detect_trg > 0);

% Detect trigger onset
% x[i]-x[i-1] ''''
d_f_detect_trg = diff(f_detect_trg);

% Remove offset

d_f_detect_trg = (d_f_detect_trg == 1);
d_f_detect_trg = [0; d_f_detect_trg];

%
detect_trg_inx = find(d_f_detect_trg == 1); 
target_trg_inx = [];
standard_trg_inx =[];

for i = 1:size(detect_trg_inx,1);
    
    pos = detect_trg_inx(i,:);
    
    if standard_trg(pos) > 0
        standard_trg_inx = [standard_trg_inx; pos];
    elseif standard_trg(pos) == 0
        target_trg_inx = [target_trg_inx; pos];
    end
end
    
    
% Find target
n_target = length(target_trg_inx);
n_standard = length(standard_trg_inx);
n_detect = length(detect_trg_inx);


%% Epoch_target

% Retrieve Target onset triggered response
eeg_tar = zeros(n_target,floor(sr*1.1),size(eeg_pre,2));  % trial by epoch times by channel

for ich = 1:ch
    for i = 1:n_target
        pos = target_trg_inx(i);
        eeg_tar(i,:,ich) = eeg_pre(pos-floor(sr*0.1):pos+floor(sr*1.0)-1,ich);
    end
end

% Baseline correction
for j = 1:n_target
    for i = 1:ich
        base = mean(eeg_tar(j,1:floor(sr*0.1)-1,i));
        eeg_tar(j,:,i) = eeg_tar(j,:,i) - base;
    end
end

%% Epoch_standard

% Retrieve Target onset triggered response
eeg_sta = zeros(n_standard,floor(sr*1.1),size(eeg_pre,2));  % trial by epoch times by channel

for ich = 1:ch
    for i = 1:n_standard-1
        pos = standard_trg_inx(i);
        eeg_sta(i,:,ich) = eeg_pre(pos-floor(sr*0.1):pos+floor(sr*1.0)-1,ich);
    end
end

% Baseline correction
for j = 1:n_standard
    for i = 1:ich
        base = mean(eeg_sta(j,1:floor(sr*0.1)-1,i));
        eeg_sta(j,:,i) = eeg_sta(j,:,i) - base;
    end
end


%% Find bad Trial

idx = [];
% Target trial
for i = 1:n_target
    t_tr = abs(squeeze(eeg_tar(i,:,:))); 
    bad = find(abs(t_tr) > 100);
    if length(bad) > 0
        idx = [idx i];
    end
end

for j = length(idx):-1:1
    i = idx(j);
    eeg_tar(i,:,:) = [];
end

idx = [];
% Standard trial
for i = 1:n_standard
    t_tr = abs(squeeze(eeg_sta(i,:,:))); 
    bad = find(abs(t_tr) > 100);
    if length(bad) > 0
        idx = [idx i];
    end
end

for j = length(idx):-1:1
    i = idx(j);
    eeg_sta(i,:,:) = [];
end

%% save epoched data

target_epoch = permute(eeg_tar, [3 2 1]);
standard_epoch = permute(eeg_sta, [3 2 1]);
save('1_target_2.mat', 'target_epoch');
save('1_standard_2.mat', 'standard_epoch');

% To reject bad trial
%eeglab

%% import  rejected trial

eeg_rej_s = EEG.data;
eeg_rej_t = EEG.data;


%% ERP

erp_t = squeeze(mean(eeg_rej_t,3))';
erp_s = squeeze(mean(eeg_rej_s,3))';

%% save

save('1_eeg_rej_s_2', 'eeg_rej_s');
save('1_eeg_rej_t_2', 'eeg_rej_t');
save('1_erp_s_2', 'erp_s');
save('1_erp_t_2', 'erp_t');

%% ERP_target plot

% Set
epoch_L = length(erp_t);
epoch_T = linspace(-(sr*0.1)/sr,(sr*0.7)/sr,epoch_L);

figure
for i = 1:ch
    subplot(4,4,i)
    plot(epoch_T,erp_t(:,i))
    titles = sprintf("%s",ch_name(i));
    title(titles)
    xlim([-0.1 0.7]);
    ylim([-3 3]);
    grid on
end

%% ERP_standard plot

% Set
epoch_L = length(erp_s);
epoch_T = linspace(-(sr*0.1)/sr,(sr*0.7)/sr,epoch_L);

figure
for i = 1:ch
    subplot(4,4,i)
    plot(epoch_T,erp_s(:,i))
    titles = sprintf("%s",ch_name(i));
    title(titles)
    ylim([-3 3]);
    xlim([-0.1 0.7]);
    grid on
end

%% together
epoch_L = length(erp_t);
epoch_T = linspace(-(sr*0.1)/sr,(sr*0.7)/sr,epoch_L);

figure
for i = 1:ch
    subplot(4,4,i)
    plot(epoch_T,erp_s(:,i),'k'); hold on 
    plot(epoch_T,erp_t(:,i), '-r');
    %plot(epoch_T, mmn(:,i), 'k');
    titles = sprintf("%s",ch_name(i));
    title(titles)
    xlim([-0.1 0.7]);
    ylim([-3 3]);
    grid on
end


%% All block

epoch_t_1 = load('1_eeg_rej_t_2.mat');  % channel * time(100) * trial
epoch_t_2 = load('2_eeg_rej_t_2.mat');
%epoch_3 = load('3_target.mat');
epoch_s_1 = load('1_eeg_rej_s_2.mat');  % channel * time(100) * trial
epoch_s_2 = load('2_eeg_rej_s_2.mat');
%epoch_s_3 = load('3_standard.mat');


epoch_t_all = cat(3, epoch_t_1.eeg_rej_t,epoch_t_2.eeg_rej_t);
epoch_s_all =cat(3, epoch_s_1.eeg_rej_s,epoch_s_2.eeg_rej_s);

erp_t_all = squeeze(mean(epoch_t_all,3))';
erp_s_all = squeeze(mean(epoch_s_all,3))';

%%
epoch_L = length(erp_t_all);
epoch_T = linspace(-(sr*0.1)/sr,(sr*0.7)/sr,epoch_L);

% target
figure
for i = 1:ch
    subplot(4,4,i)
    plot(epoch_T,erp_t_all(:,i))
    titles = sprintf("%s",ch_name(i));
    title(titles)
    xlim([-0.1 0.7]);
    grid on
end

% standard
figure
for i = 1:ch
    subplot(4,4,i)
    plot(epoch_T,erp_s_all(:,i))
    titles = sprintf("%s",ch_name(i));
    title(titles)
    xlim([-0.1 0.7]);
    grid on
end


%% all save

save('all_eeg_s_2.mat', 'epoch_s_all');
save('all_eeg_t_2.mat', 'epoch_t_all');
save('all_erp_t_2.mat', 'erp_t_all');
save('all_erp_s_2.mat', 'erp_s_all');

%% all together
epoch_L = length(erp_t_all);
epoch_T = linspace(-(sr*0.1)/sr,(sr*0.7)/sr,epoch_L);

figure
for i = 1:ch
    subplot(4,4,i)
    plot(epoch_T,erp_s_all(:,i),'k'); hold on 
    plot(epoch_T,erp_t_all(:,i), '-r');
    %plot(epoch_T, mmn(:,i), 'k');
    titles = sprintf("%s",ch_name(i));
    title(titles)
    xlim([-0.1 0.7]);
    ylim([-3 3]);
    grid on
end

%% mmn
for i = 1: size(erp_t_all,2)
    for j= 1:size(erp_t_all,1)
        
        a = abs(erp_t_all(j,i));
        b = abs(erp_s_all(j,i));
        c(j,i) = a-b;
        if erp_t_all(j,i) < 0
            mmn(j,i) = -c(j,i);
        else
            mmn(j,i) = c(j,i);
        end
    end
end

figure
for i = 1:ch
    subplot(4,4,i)
    plot(epoch_T, mmn(:,i), 'k'); hold on
    titles = sprintf("%s",ch_name(i));
    title(titles)
    xlim([-0.1 0.7]);
    ylim([-3 3]);
    grid on
    
end

%% invert

for i = 13:16
    erp_s(:,i) = -erp_s(:,i);
    erp_t(:,i) = -erp_t(:,i);
end

%% tohether

figure
for i = 1:ch
    subplot(4,4,i)
    plot(epoch_T,erp_s(:,i),'k'); hold on 
    plot(epoch_T,erp_t(:,i), '-r');
    %plot(epoch_T, mmn(:,i), 'k');
    titles = sprintf("%s",ch_name(i));
    title(titles)
    xlim([-0.1 0.7]);
    ylim([-3 3]);
    grid on
end


%%

save('1_standard_rej.mat', 'eeg_rej_e_sta');
save('1_target_rej.mat', 'eeg_rej_e_tar');
%%
save('all_tar.mat', 'erp_all');
save('all_sta.mat', 'erp_s_all');


%% Data per trial plot - Target
% Set
epoch_L = length(erp_t);
epoch_T = linspace(-(sr*0.1)/sr,(sr*0.7)/sr,epoch_L); % 0.8 s

figure(1)
clf
for i = 1:round(size(eeg_tar,1)/2)
    
    t_tr = squeeze(eeg_tar(i,:,:));    % trial by time by channel
  
    subplot(5,10,i)
    plot(epoch_T,t_tr); hold on
    %ylim([-4 4]);
    titles = sprintf("%d",i);
    title(titles)

end

figure(2)
clf
for i = round(size(eeg_tar,1)/2)+1:size(eeg_tar,1)
    
    
    t_tr = squeeze(eeg_tar(i,:,:));

    subplot(5,10,i-round(size(eeg_tar,1)/2))
    plot(epoch_T,t_tr); hold on
    %ylim([-4 4]);
    titles = sprintf("%d",i);
    title(titles)
end
