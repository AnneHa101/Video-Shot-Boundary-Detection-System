# Video-Shot-Boundary-Detection-System

IDEAS OF TWIN-COMPARISION BASED APPROACH
Twin-comparison requires the use of two cutoff thresholds: 
- Tb is used for camera break (cut) detection. 
- In addition, a second, lower, threshold Ts is used for gradual transition detection. 

The detection process begins by comparing consecutive frames using Eq. 1 to get SD. Whenever the difference value reaches threshold Tb, a camera break is declared, e.g. Fb in Fig. 1. The twin-comparison also detects differences that are smaller than Tb but greater than or equal to Ts. Any frame that exhibits such a difference value is marked as the potential start (Fs _candi) of a gradual transition (labeled in Fig. 1). The end frame (Fe_candi) of the transition is detected when its next continuous Tor (a preset threshold) numbers of SD values are lower than Ts or it reaches cut Tb threshold. Then if all the SD values between Fs_candi and Fe_candi add up to be greater than or equal to Tb, this duration is considered to contain a gradual transition. Otherwise this section is dropped and the search continues for other gradual transitions.

ALGORITHM IMPLEMENTATION
1. Read the video sequence directly. For each frame (from frames #1,000 to #4,999), make sure the frame number the program captured matches with the one shown in VirtualDub.

2. Get frame-to-frame different
    SDi = H_i(j)-H_i+1(j), for 1 <= j <= 25

3. Set thresholds for cuts and gradual transition
    For cut:
            Tb = mean(SD) + std (SD) *11
    For gradual transition:
            Ts = mean(SD)*2 
            Tor = 2

4. Loop through SDs
- If SDi >= Tb, then cut starts at i(i.e. Cs=i) and ends at i+1 (i.e., Ce = i+1)
- If Ts <= SDi < Tb, consider it as the potential start (Fs_candi) of a gradual transition. Continue to check its following SD values. The end frame (Fe _ candi) of the transition is detected when its next 2 (i.e. defined by Tor) consecutive SD values are lower than Ts or reaches a cut boundary. 
- If SUM(SDi) >= Tb from Fs_candi to Fe_candi, then Fs_candi and Fe_candi are taken as real start Fs_candi (Fs) and ending (Fe) of a gradual transition. Otherwise, this section is dropped and the search continues for other gradual transitions.
- Outputs the sets of (Cs,Ce) and (Fs,Fe).

5. Build system GUI:
- Show first frame of each shot: considering Ce, Fs +1 the first frame of each shot
(Cs, Fs the end frame of its previous shot).
- Allow user to view the corresponding video shot (i.e., the shot can be played) by
clicking on its first frame.





