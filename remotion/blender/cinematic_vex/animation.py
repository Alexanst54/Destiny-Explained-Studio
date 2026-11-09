"""Deterministic FK + analytic three-dimensional two-bone leg IK, Z-up.
Stance targets are fixed in world space. No simulation history or external motion clips.
"""
import math
from cinematic_vex.atheon import THIGH,SHIN,GROUND


def qmul(a,b):
    w,x,y,z=a;v,i,j,k=b
    return (w*v-x*i-y*j-z*k,w*i+x*v+y*k-z*j,w*j-x*k+y*v+z*i,w*k+x*j-y*i+z*v)


def axis_q(axis,angle):
    q=[math.cos(angle/2),0,0,0];q[axis+1]=math.sin(angle/2);return tuple(q)


def quaternion_euler(q):
    w,x,y,z=q
    return (math.atan2(2*(w*x+y*z),1-2*(x*x+y*y)),
            math.asin(max(-1,min(1,2*(w*y-z*x)))),
            math.atan2(2*(w*z+x*y),1-2*(y*y+z*z)))


def solve_leg(hip,target):
    dx,dy,dz=[target[i]-hip[i] for i in range(3)];dist=math.sqrt(dx*dx+dy*dy+dz*dz)
    if not abs(THIGH-SHIN)+1e-6<dist<THIGH+SHIN-1e-6:raise ValueError('Leg target is unreachable')
    knee=math.acos(max(-1,min(1,(dist*dist-THIGH*THIGH-SHIN*SHIN)/(2*THIGH*SHIN))))
    roll=math.atan2(-dx,-dz)
    pitch=math.atan2(dy,math.sqrt(dx*dx+dz*dz))-math.atan2(SHIN*math.sin(knee),THIGH+SHIN*math.cos(knee))
    hipq=qmul(axis_q(1,roll),axis_q(0,pitch));kneeq=axis_q(0,knee);world=qmul(hipq,kneeq)
    return {'hip':(pitch,roll,0),'knee':(knee,0,0),'footQuaternion':(world[0],-world[1],-world[2],-world[3])}


def foot_target(t,side,walk):
    if not walk:return (side*1.45,8.7,GROUND+.2),True
    # Two full 1.8 s cycles; then a planted idle hold within the reusable set.
    motion=min(t,3.6);offset=0 if side<0 else .5;phase=motion/1.8+offset
    cycle=math.floor(phase+1e-9);p=max(0,phase-cycle);duty=.65
    anchor=9-2.4*1.8*(cycle-offset+.325)
    stance=p<duty
    if stance:y=anchor;lift=0
    else:
        u=(p-duty)/(1-duty);smooth=u*u*(3-2*u);y=anchor-2.4*1.8*smooth;lift=.65*math.sin(math.pi*u)**2
    return (side*1.45,y,GROUND+.2+lift),stance


def evaluate(boss_id,animation='idle',frame=0,fps=30):
    allowed={'boss-atheon':['idle','walk','combat','temporal','reveal'],'boss-templar':['idle','rotate','move','attack','reveal']}
    if boss_id not in allowed or animation not in allowed[boss_id]:raise ValueError('Unsupported boss animation')
    if type(frame) is not int or frame<0 or type(fps) is not int or fps not in [24,30]:raise ValueError('Invalid animation time')
    t=frame/fps;rot={};pos={};quat={};scales={};contacts={}
    if boss_id=='boss-atheon':
        motion=min(t,3.6) if animation=='walk' else 0
        phase=motion*math.tau/1.8
        root=(.15*math.sin(phase) if animation=='walk' else 0,9-motion*2.4,GROUND)
        pelvis=(0,0,8.5-.10*math.cos(phase*2) if animation=='walk' else 8.5+.025*math.sin(t*1.8))
        pos.update(root=root,pelvis=pelvis)
        rot['torso']=(.025*math.sin(t*1.7),.035*math.sin(phase),.025*math.sin(t*.8))
        rot['head']=(.018*math.sin(t*1.4),0,.045*math.sin(t*.9))
        for side,n in [(-1,'L'),(1,'R')]:
            target,stance=foot_target(t,side,animation=='walk')
            hip=(root[0]+side*1.45,root[1],root[2]+pelvis[2]-.3)
            leg=solve_leg(hip,target);rot['hip'+n]=leg['hip'];rot['knee'+n]=leg['knee'];quat['foot'+n]=leg['footQuaternion'];rot['foot'+n]=quaternion_euler(leg['footQuaternion'])
            contacts[n]={'ankle':target,'stance':stance,'soleZ':target[2]-.2}
            rot['shoulder-upper'+n]=(-side*.15*math.sin(phase),0,side*.12)
            rot['elbow-upper'+n]=(-.15,0,0)
        if animation in ['combat','temporal','reveal']:
            u=max(0,min(1,t/1.4));k=u*u*(3-2*u)
            rot['shoulder-upperL']=(-1.1*k,0,-.25*k);rot['elbow-upperL']=(-.8*k,0,0)
            rot['shoulder-upperR']=(-.65*k,0,.15);rot['elbow-upperR']=(-.45*k,0,0)
            rot['torso']=(.03,0,.14*k*math.sin(t*1.1))
            rot['head']=(-.08*k,0,-.08*k)
        rot['weapon']=(-.75,0,.3)
        rot['energy']=(t*.65,t*.8,t*1.2)
        k=min(1,t/1.4) if animation in ['temporal','reveal'] else .12
        scales['energy']=(k*(1+.12*math.sin(t*3)),)*3
    else:
        pos['pelvis']=(0,0,6.8+math.sin(t*1.7)*.12)
        pos['root']=(math.sin(t*.65)*1.8,9+math.sin(t*.45),1.35) if animation=='move' else (0,9,1.35)
        rot['pelvis']=(.025*math.sin(t*1.2),.025*math.sin(t),t*.18 if animation=='rotate' else .035*math.sin(t*.7))
        rot['halo']=(0,0,t*.42)
        for side,n in [(-1,'L'),(1,'R')]:
            rot['carapace'+n]=(.025*math.sin(t*1.5+side),0,side*.018*math.sin(t))
            pulse=max(0,math.sin(t*math.tau*1.8+side*.5))**8 if animation=='attack' else 0
            rot['cannon'+str(side)]=(.08*pulse,0,0);scales['blast'+str(side)]=(max(.001,pulse),1,max(.001,pulse))
        for tier in range(3):rot['ventral'+str(tier)]=(.025*math.sin(t*1.8+tier*.8),0,.035*math.sin(t+tier*.5))
    return dict(rotation=rot,position=pos,quaternion=quat,scale=scales,contacts=contacts,
                emissionPulse=1+.12*math.sin(t*3)+(.6*math.sin(t*2)**2 if animation=='temporal' else 0))
