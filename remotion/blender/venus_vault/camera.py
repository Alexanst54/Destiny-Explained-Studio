"""Monumental boss framing; explicit paths, no resolution-dependent geometry or framing."""
import math
PRESETS=('wide','reveal','orbit','low-angle','close-up','front','profile','ground-reveal','mechanism','temporal')


def camera_pose(environment,preset='wide',frame=0,fps=30):
    if preset not in PRESETS or environment not in ['venus','arena-templars-well','arena-glass-throne']:raise ValueError('Unknown camera/environment')
    if type(frame) is not int or frame<0 or type(fps) is not int or fps not in [24,30]:raise ValueError('Invalid camera time')
    t=frame/fps;u=min(t/4,1);smooth=u*u*(3-2*u);ath=environment=='arena-glass-throne'
    target=(0,9,10 if ath else 7);lens=42
    if environment=='venus':
        target=(0,18,6);pos=(27,-34,19);lens=38
        if preset in ['reveal','ground-reveal']:pos=(19-smooth*5,-30+smooth*7,14-smooth*3)
        if preset=='orbit':a=-1.2+t*.1;pos=(35*math.cos(a),15+35*math.sin(a),15)
        if preset=='low-angle':pos=(5,-12,2);target=(0,20,10);lens=27
        if preset in ['close-up','mechanism']:pos=(8,6,9);target=(12,18,6);lens=50
        if preset in ['front','profile','temporal']:pos=(27,-34,19)
    elif ath:
        if preset=='wide':pos=(17,-48,21);target=(0,21,15);lens=30
        elif preset=='front':pos=(0,-39,10.5)
        elif preset=='profile':pos=(48,9,10.5)
        elif preset=='orbit':a=-math.pi/2-.35+t*.10;pos=(48*math.cos(a),9+48*math.sin(a),10.5)
        elif preset=='low-angle':pos=(12,-28,2.2);target=(0,9,10);lens=31
        elif preset in ['close-up','mechanism']:pos=(9,-13,15);target=(0,9,14.3);lens=51
        elif preset=='temporal':pos=(-23,-28,12);target=(-1,6,11.5);lens=42
        elif preset=='ground-reveal':pos=(6,-33,2.0+smooth*11);target=(0,9,2.0+smooth*12);lens=40
        else:pos=(8-smooth*3,-44+smooth*5,8+smooth*2);target=(0,9,10);lens=40
    else:
        if preset=='wide':pos=(0,-32,10);target=(0,9,7.8);lens=38
        elif preset=='front':pos=(4,-25,8.5);target=(0,9,7.5);lens=44
        elif preset=='profile':pos=(40,9,10);target=(0,9,7.8);lens=38
        elif preset=='orbit':a=-math.pi/2-.35+t*.1;pos=(41*math.cos(a),9+41*math.sin(a),10);lens=38;target=(0,9,7.8)
        elif preset=='low-angle':pos=(9,-23,2);target=(0,9,8);lens=32
        elif preset in ['close-up','mechanism']:pos=(6,-15,11);target=(0,9,8.5);lens=52
        elif preset=='ground-reveal':pos=(4,-30,2+smooth*10);target=(0,9,3+smooth*6);lens=38
        else:pos=(7-smooth*3,-35+smooth*4,9);target=(0,9,7.8);lens=40
    return dict(position=pos,target=target,lens=lens,sensorFit='VERTICAL',sensorHeight=24,near=.1,far=350)
