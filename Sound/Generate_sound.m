% Generate Sound

sr = 44100;   % sampling rate / Hz 
time = 0.1;   % time / s
fs1 = 1000;    % frequency / Hz
fs2 = 2000;
t = 0:1/sr:time;
y1 = sin(2*pi*fs1*t);
y2 = sin(2*pi*fs2*t);

ramp_dur=.010;   % rise/fall : 10ms
rampSamps = floor(sr*ramp_dur);
window=hanning(2*rampSamps)';
w1=window(1:ceil((length(window))/2)); %use the first half of hanning function for onramp
w2=window(ceil((length(window))/2)+1:end); %use second half of hanning function of off ramp
w1 = [w1 ones(1,length(y1)-length(w1))];
w2 = [ones(1,length(y1)-length(w2)) w2];

%ramp stimuli
y1 = y1.*w1.*w2; 
y2 = y2.*w1.*w2;

%plot(t, y1)
%plot(t, y2)

sound(y1,sr);
pause(0.8);
sound(y1,sr);
pause(0.8);
sound(y1,sr);
pause(0.8);
sound(y1,sr);
pause(0.8);
sound(y2,sr);
pause(0.8);
sound(y1,sr);
pause(0.8);
sound(y1,sr);
pause(0.8);
sound(y1,sr);
pause(0.8);
sound(y1,sr);
pause(0.8);
sound(y2,sr);


%audiowrite('001_Standard.wav',y1,sr);
%audiowrite('002_Target.wav',y2,sr);



