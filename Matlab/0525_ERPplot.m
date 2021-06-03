
clear all
close all
clc

sr = 125;

% Load raw data & trigger
eeg_data = load('EEG_0526.mat'); % EEG trace
trg_data = load('A_0526.mat'); % trigger trace

% Select block data
block = 3;   % block

% Import
raw = squeeze(eeg_data.EEG(block,:,:));   % times by channel
trg = squeeze(trg_data.AUX(block,:,:));

% Select sta & tar
standard_trg = trg(:,1);
target_trg = trg(:,2);

% Channel labeling
%ch_name_cyton = ["Fp1","Fz","C3","C4","P7","P8","O1","O2","Cz","Pz","F3","F4","T7","T8","P3","P4"]; % recorded location -
ch_name = ["Fp1","F3","Fz","F4","T7","C3","Cz","C4","T8","P7","P3","Pz","P4","P8","O1","O2"]; % gui location

% Change channel location for eeglab GUI
ch_num = [1,11, 2, 12, 13, 3, 9, 4, 14, 5, 15, 10, 16, 6, 7, 8];
for i = 1:16
    eeg(:,i) = raw(:,ch_num(i));
end

% Set
ch = size(eeg,2); % The number of channel
ti = size(eeg,1); % time length

%% Preprocessing
%% Filter

% Filter design  - filt order default = 3*fix(srate/locutoff) = 375
design = designfilt('bandpassfir', 'FilterOrder',375, ...
    'CutoffFrequency1', 1, 'CutoffFrequency2', 30,...
    'SampleRate', 125);

% Filter design plot
%fvtool(design);

eeg_filt = filtfilt(design, eeg);

%% Bad channel

eeg_filt(:,5) = [];
ch = ch-1;

%% ICA with GUI

save('data.mat', 'eeg_filt');
eeglab

%% ICA data import
% after components removal

eeg_ica = EEG.data';

%% 
%  per channel
for j = 1:ch
    m = mean(eeg_ica(:,j));
    eeg_ch(:,j) = eeg_ica(:,j) - m;
end

% Common Average Reference
for t = 1:ti
    m = mean(eeg_ch(t,:));
    eeg_pre(t,:) = eeg_ch(t,:) - m;
end

%% Save data
save('1_eeg.mat', 'eeg_pre');

%% EEG Plot
L = length(eeg_pre);
t = linspace(0,L/sr,L); % time trace

figure
for i = 1:ch
    title(['block ' num2str(block)])
%     plot(t,eeg_trc_pre_1(:,i) + (i-1)*5);
    plot(t,eeg_pre(:,i)); hold on
    xlim([0 302])
end

%% Trigger
L = length(eeg_pre);
t = linspace(0,L/sr,L); % time trace

% if index > 3.14 = 1, then index < 3.14 = 0
f_target_trg = (target_trg > 3.14);
f_standard_trg = (standard_trg > 3.14);

% Detect trigger onset
% x[i]-x[i-1] ''''
d_f_target_trg = diff(f_target_trg);    % 37499 by 1
d_f_standard_trg = diff(f_standard_trg);

% Remove offset
d_f_target_trg = (d_f_target_trg == 1);
d_f_standard_trg = (d_f_standard_trg == 1); 

% Plus first trial
d_f_target_trg = [d_f_target_trg; 0];
d_f_standard_trg = [d_f_standard_trg; 0];

% Find target
target_trg_inx = find(d_f_target_trg == 1);   % Index of Target sound
standard_trg_inx = find(d_f_standard_trg == 1); 
n_target = length(target_trg_inx);
n_standard = length(standard_trg_inx);

% Check trigger
figure(1)
clf
% 
% subplot(211)
for i = 1:15
    plot(t,eeg_pre(:,i) + (i-1)*15); hold on
end
% set(gca, 'xlim', [0,10])
% subplot(312)
% plot(t, d_f_standard_trg,'b');
% % set(gca, 'xlim', [0,10])
% subplot(212)
plot(t, (d_f_standard_trg*300)-40,'r');
% set(gca, 'xlim', [0,10])


%xlim([0,300]);

subplot(212)
plot(t, d_f_target_trg, 'r');
xlim([0,300]);

%% Epoch_target

% Retrieve Target onset triggered response
eeg_tar = zeros(n_target,sr*0.8,size(eeg_pre,2));  % trial by epoch times by channel

for ich = 1:ch
    for i = 1:n_target
        pos = target_trg_inx(i);
        eeg_tar(i,:,ich) = eeg_pre(pos-floor(sr*0.1):pos+floor(sr*0.7),ich);
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
eeg_sta = zeros((n_standard-1),sr*0.8,size(eeg_pre,2));  % trial by epoch times by channel

for ich = 1:ch
    for i = 2:n_standard
        pos = standard_trg_inx(i);
        eeg_sta(i-1,:,ich) = eeg_pre(pos-floor(sr*0.1):pos+floor(sr*0.7),ich);
    end
end

% Baseline correction
for j = 2:n_standard
    for i = 1:ich
        base = mean(eeg_sta(j-1,1:floor(sr*0.1)-1,i));
        eeg_sta(j-1,:,i) = eeg_sta(j-1,:,i) - base;
    end
end

n_standard = n_standard-1;

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
save('1_target.mat', 'target_epoch');
save('1_standard.mat', 'standard_epoch');

eeglab

%% ERP

erp_t = squeeze(mean(eeg_tar));
erp_s = squeeze(mean(eeg_sta));

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
    xlim([-0.1 0.7]);
    grid on
end


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

%% All block

epoch_1 = load('1_target.mat');  % channel * time(100) * trial
epoch_2 = load('2_target.mat');
epoch_3 = load('3_target.mat');
epoch_s_1 = load('1_standard.mat');  % channel * time(100) * trial
epoch_s_2 = load('2_standard.mat');
epoch_s_3 = load('3_standard.mat');


epoch_all = cat(3, epoch_1.target_epoch,epoch_2.target_epoch,epoch_3.target_epoch);
epoch_s_all =cat(3, epoch_s_1.standard_epoch,epoch_s_2.standard_epoch,epoch_s_3.standard_epoch);

erp_all = squeeze(mean(epoch_all,3))';
erp_s_all = squeeze(mean(epoch_s_all,3))';

epoch_L = length(erp_all);
epoch_T = linspace(-(sr*0.1)/sr,(sr*0.7)/sr,epoch_L);

% target
figure
for i = 1:ch
    subplot(4,4,i)
    plot(epoch_T,erp_all(:,i))
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


%%

save('all_target.mat', 'epoch_all');

%%

figure
for i = 1:ch
    subplot(4,4,i)
    plot(epoch_T,erp_all(:,i)); hold on 
    plot(epoch_T,erp_s_all(:,i), '-r');
    titles = sprintf("%s",ch_name(i));
    title(titles)
    xlim([-0.1 0.7]);
    ylim([-2.5 2.5]);
    grid on
end









