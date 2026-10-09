import {memo,useEffect,useRef,useState,type MutableRefObject} from 'react';
import * as THREE from 'three';
import {BONES,type Landmark} from '../types';
export type PoseBuffer={pose:Landmark[];predicted:Landmark[];world:Landmark[];aspect:number};
export const Overlay=memo(function Overlay({buffer,visible,demo}:{buffer:MutableRefObject<PoseBuffer>;visible:boolean;demo:boolean}){
 const ref=useRef<HTMLCanvasElement>(null);
 useEffect(()=>{let raf=0;const draw=()=>{
   const c=ref.current;if(!c)return;const box=c.getBoundingClientRect(),dpr=Math.min(devicePixelRatio,2);
   if(c.width!==Math.round(box.width*dpr)||c.height!==Math.round(box.height*dpr)){c.width=Math.round(box.width*dpr);c.height=Math.round(box.height*dpr);}
   const ctx=c.getContext('2d')!;ctx.clearRect(0,0,c.width,c.height);ctx.save();ctx.scale(dpr,dpr);
   const p=buffer.current.pose;const a=buffer.current.aspect||16/9;
   const w=Math.min(box.width,box.height*a),h=w/a,x=(box.width-w)/2,y=(box.height-h)/2;
   if(demo){ctx.strokeStyle='#163346';ctx.lineWidth=1;for(let i=0;i<10;i++){ctx.beginPath();ctx.moveTo(0,box.height*.83+i*9);ctx.lineTo(box.width,box.height*.83+i*9);ctx.stroke();}for(let i=0;i<12;i++){ctx.beginPath();ctx.moveTo(box.width/2,box.height*.65);ctx.lineTo(i*box.width/11,box.height);ctx.stroke();}}
   if(visible&&p.length===33){ctx.lineWidth=demo?4:3;ctx.strokeStyle='#23e3c2';ctx.shadowColor='#16dfba';ctx.shadowBlur=demo?12:3;
    for(const [a,b]of BONES){if(Math.min(p[a].visibility,p[b].visibility)<.55)continue;ctx.beginPath();ctx.moveTo(x+p[a].x*w,y+p[a].y*h);ctx.lineTo(x+p[b].x*w,y+p[b].y*h);ctx.stroke();}
    for(const i of [0,11,12,13,14,15,16,23,24,25,26,27,28,31,32]){if(p[i].visibility<.55)continue;ctx.fillStyle=i<17?'#75f7dc':'#d2f68b';ctx.beginPath();ctx.arc(x+p[i].x*w,y+p[i].y*h,i===0&&demo?14:4,0,Math.PI*2);ctx.fill();}
   }ctx.restore();raf=requestAnimationFrame(draw);
 };raf=requestAnimationFrame(draw);return()=>cancelAnimationFrame(raf);},[buffer,visible,demo]);
 return <canvas ref={ref} className="pose-overlay" aria-label="Live skeleton overlay"/>;
});
export const Motion3D=memo(function Motion3D({buffer,prediction}:{buffer:MutableRefObject<PoseBuffer>;prediction:boolean}){
 const host=useRef<HTMLDivElement>(null);const [error,setError]=useState('');
 useEffect(()=>{
  if(!host.current)return;const el=host.current;let renderer:THREE.WebGLRenderer;
  try{renderer=new THREE.WebGLRenderer({alpha:true,antialias:true,powerPreference:'low-power'});}catch{setError('3D view unavailable: WebGL is disabled. 2D tracking is still available.');return;}
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(40,1,.01,100);camera.position.set(1.6,1.1,3.2);camera.lookAt(0,0,0);
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));el.appendChild(renderer.domElement);
  const grid=new THREE.GridHelper(4,16,0x184d68,0x10283c);grid.position.y=-1;scene.add(grid);scene.add(new THREE.AxesHelper(.4));
  const groups=[new THREE.Group(),new THREE.Group()];const objects:{line:THREE.LineSegments;points:THREE.Points}[]=[];
  groups.forEach((group,j)=>{scene.add(group);const geom=new THREE.BufferGeometry();geom.setAttribute('position',new THREE.BufferAttribute(new Float32Array(BONES.length*6),3));
    const line=new THREE.LineSegments(geom,new THREE.LineBasicMaterial({color:j?0x375b93:0x60cfff,transparent:true,opacity:j?.5:1}));group.add(line);
    const pg=new THREE.BufferGeometry();pg.setAttribute('position',new THREE.BufferAttribute(new Float32Array(33*3),3));const points=new THREE.Points(pg,new THREE.PointsMaterial({color:j?0x638bf9:0xc9f6ff,size:.045}));group.add(points);objects.push({line,points});});
  const observer=new ResizeObserver(()=>{const w=el.clientWidth,h=el.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();});observer.observe(el);
  let raf=0,last=0;const render=(now:number)=>{raf=requestAnimationFrame(render);if(now-last<33)return;last=now;
   [buffer.current.pose,prediction?buffer.current.predicted:[]].forEach((p,j)=>{groups[j].visible=p.length===33;if(p.length!==33)return;
    const hip={x:(p[23].x+p[24].x)/2,y:(p[23].y+p[24].y)/2,z:(p[23].z+p[24].z)/2};
    const xyz=p.map(q=>[(q.x-hip.x)*3*buffer.current.aspect,-(q.y-hip.y)*3,-(q.z-hip.z)*2]);
    const lines=objects[j].line.geometry.attributes.position as THREE.BufferAttribute;
    BONES.forEach(([a,b],i)=>{lines.setXYZ(i*2,...xyz[a] as [number,number,number]);lines.setXYZ(i*2+1,...xyz[b] as [number,number,number]);});lines.needsUpdate=true;
    const points=objects[j].points.geometry.attributes.position as THREE.BufferAttribute;xyz.forEach((q,i)=>points.setXYZ(i,...q as [number,number,number]));points.needsUpdate=true;
   });renderer.render(scene,camera);
  };raf=requestAnimationFrame(render);
  return()=>{cancelAnimationFrame(raf);observer.disconnect();scene.traverse(o=>{const m=o as THREE.Mesh;if(m.geometry)m.geometry.dispose();if(m.material){const ms=Array.isArray(m.material)?m.material:[m.material];ms.forEach(x=>x.dispose());}});renderer.dispose();renderer.domElement.remove();};
 },[buffer,prediction]);
 return <div className="three-host" ref={host}>{error&&<p className="muted p-4">{error}</p>}<span className="three-caption">Cyan: current · Blue: projected<br/>Relative pose coordinates</span></div>;
});
