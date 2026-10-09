import type {Landmark} from '../types';
// Deterministic synthetic landmarks pass through exactly the same server engine as camera poses.
export function demoPose(exercise:string,t:number):Landmark[]{
 const aspect=16/9, p:Landmark[]=Array.from({length:33},()=>({x:.5,y:.2,z:0,visibility:.98}));
 const u=(1-Math.cos(t*Math.PI/2))/2;
 const set=(i:number,x:number,y:number,z=0)=>{p[i]={x:x/aspect+.2,y,z,visibility:.98};};
 const pair=(i:number,x:number,y:number)=>{set(i,x-.035,y,-.04);set(i+1,x+.035,y+.004,.04);};
 pair(11,.5,.28);pair(13,.48,.44);pair(15,.49,.61);pair(23,.5,.53);pair(25,.5,.70);pair(27,.5,.89);
 if(['squat','lunge','reverse_lunge'].includes(exercise)){
   const angle=174-u*91, bend=(180-angle)*Math.PI/180;
   for(const o of [0,1]){const x=.5+o*.09;const hX=x+.23*Math.sin(bend),hY=.66-.23*Math.cos(bend);
     set(27+o,x,.89,o*.08);set(25+o,x,.66,o*.08);set(23+o,hX,hY,o*.08);set(11+o,hX-.065,hY-.23,o*.08);
     set(13+o,hX-.18,hY-.10,o*.08);set(15+o,hX-.24,hY-.25,o*.08);}
 }else if(['bicep_curl','tricep_extension','shoulder_press','pushup'].includes(exercise)){
   const value=exercise==='bicep_curl'?170-u*127:exercise==='shoulder_press'?80+u*92:175-u*98;
   const bend=(180-value)*Math.PI/180;
   if(exercise==='pushup'){pair(11,.26,.39);pair(23,.58,.43);pair(25,.76,.46);pair(27,.94,.48);}
   for(const o of [0,1]){const x=p[11+o].x*aspect-.2*aspect;const sy=p[11+o].y;
     set(13+o,x,sy+.17,o*.08);set(15+o,x+.17*Math.sin(bend),sy+.17+.17*Math.cos(bend),o*.08);}
 }else if(['lateral_raise','jumping_jack'].includes(exercise)){
   const value=(10+u*(exercise==='jumping_jack'?158:85))*Math.PI/180;
   for(const o of [0,1]){const sign=o?1:-1;const x=.5+sign*.07;set(11+o,x,.28,o*.08);set(13+o,x+sign*.18*Math.sin(value),.28+.18*Math.cos(value),o*.08);set(15+o,x+sign*.35*Math.sin(value),.28+.35*Math.cos(value),o*.08);if(exercise==='jumping_jack'){set(25+o,.5+sign*(.06+.12*u),.70);set(27+o,.5+sign*(.07+.24*u),.89);}}
 }else if(exercise==='plank'){
   pair(11,.23,.45);pair(13,.23,.62);pair(15,.12,.65);pair(23,.55,.46);pair(25,.76,.47);pair(27,.96,.48);
 }else if(['situp','crunch','leg_raise','mountain_climber'].includes(exercise)){
   const value=exercise==='crunch'?175-u*48:178-u*112, theta=(180-value)*Math.PI/180;
   pair(11,.24,.44);pair(23,.55,.44);pair(25,.55+.23*Math.cos(theta),.44+.23*Math.sin(theta));pair(27,.55+.44*Math.cos(theta),.44+.44*Math.sin(theta));pair(13,.25,.60);pair(15,.12,.60);
 }
 for(let i=0;i<11;i++)set(i,p[11].x*aspect-.2*aspect-.01,p[11].y-.075);
 for(const o of [0,1]){p[29+o]={...p[27+o],y:p[27+o].y+.012};p[31+o]={...p[27+o],x:p[27+o].x-.05,y:p[27+o].y+.015};}
 return p;
}
