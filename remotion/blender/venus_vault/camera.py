"""Five bounded camera paths, continuous in frame time. No legacy camera mutation."""
import math
PRESETS=('wide','reveal','orbit','low-angle','close-up')


def camera_pose(environment, preset='wide', frame=0, fps=30):
    if preset not in PRESETS or environment not in ['venus','arena-templars-well','arena-glass-throne']:
        raise ValueError('Unknown camera/environment')
    if type(frame) is not int or frame<0 or fps not in [24,30]:raise ValueError('Invalid camera time')
    t=frame/fps;u=min(t/4,1);smooth=u*u*(3-2*u)
    target=(0,10,6);lens=38
    if environment=='venus':
        target=(0,18,6);pos=(27,-34,19)
        if preset=='reveal':pos=(19-smooth*5,-30+smooth*7,14-smooth*3)
        if preset=='orbit':a=-1.2+t*.1;pos=(35*math.cos(a),15+35*math.sin(a),15)
        if preset=='low-angle':pos=(5,-12,2);target=(0,20,10);lens=27
        if preset=='close-up':pos=(8,6,9);target=(12,18,6);lens=50
    else:
        if preset=='wide':pos=(26,-33,22);target=(0,11,7);lens=34
        elif preset=='reveal':pos=(12-smooth*4,-24+smooth*9,10);target=(0,9,7);lens=43
        elif preset=='orbit':a=-math.pi/2-.48+t*.16;pos=(25*math.cos(a),9+25*math.sin(a),11);lens=43
        elif preset=='low-angle':pos=(9,-10,2.5);target=(0,9,8);lens=32
        else:pos=(5,-2,10);target=(0,9,9.9 if environment=='arena-glass-throne' else 5.9);lens=65
    return dict(position=pos,target=target,lens=lens,near=.1,far=250)
