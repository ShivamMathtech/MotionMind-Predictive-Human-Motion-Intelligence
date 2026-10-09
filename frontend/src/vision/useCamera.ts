import {useRef,useState,useEffect,useCallback} from 'react';
import type {Landmark,Settings} from '../types';
export function useCamera(settings:Settings,onPose:(p:Landmark[],t:number,aspect:number,world?:Landmark[])=>void){
 const videoRef=useRef<HTMLVideoElement|null>(null),workerRef=useRef<Worker|null>(null),streamRef=useRef<MediaStream|null>(null);
 const callback=useRef(onPose);callback.current=onPose;
 const settingsRef=useRef(settings);settingsRef.current=settings;
 const [status,setStatus]=useState('off'),[error,setError]=useState(''),[devices,setDevices]=useState<MediaDeviceInfo[]>([]);
 const [diagnostics,setDiagnostics]=useState({inferenceFPS:0,latency:0,cameraFPS:0,resolution:'—',dropped:0,effectiveFPS:0});
 const active=useRef(false),busy=useRef(false),ready=useRef(false),generation=useRef(0);
 const stop=useCallback(()=>{generation.current++;active.current=false;ready.current=false;busy.current=false;workerRef.current?.terminate();workerRef.current=null;streamRef.current?.getTracks().forEach(t=>t.stop());streamRef.current=null;if(videoRef.current)videoRef.current.srcObject=null;setStatus('off');},[]);
 const listDevices=useCallback(async()=>{if(navigator.mediaDevices)setDevices((await navigator.mediaDevices.enumerateDevices()).filter(d=>d.kind==='videoinput'));},[]);
 useEffect(()=>{listDevices().catch(()=>{});return stop;},[stop,listDevices]);
 const start=useCallback(async()=>{
  stop();const gen=generation.current;setError('');setStatus('loading');
  try{
   if(!navigator.mediaDevices?.getUserMedia)throw Error('Camera access requires localhost or HTTPS and a supported browser.');
   const [width,height]=settingsRef.current.resolution.split('x').map(Number);
   const stream=await navigator.mediaDevices.getUserMedia({video:{deviceId:settingsRef.current.cameraId?{exact:settingsRef.current.cameraId}:undefined,width:{ideal:width},height:{ideal:height},frameRate:{ideal:30}},audio:false});
   if(gen!==generation.current){stream.getTracks().forEach(t=>t.stop());return;}
   streamRef.current=stream;active.current=true;
   if(videoRef.current){videoRef.current.srcObject=stream;await videoRef.current.play();}
   await listDevices();
   const worker=new Worker('/pose-worker.js');workerRef.current=worker;
   let last=0,latency=0,frames=0,statsAt=performance.now(),dropped=0,lastVideoTime=-1;
   worker.onmessage=({data})=>{
    if(gen!==generation.current)return;
    if(data.type==='ready'){ready.current=true;setStatus('ready');}
    if(data.type==='error'){setError(data.message);stop();setStatus('error');}
    if(data.type==='frame-error'){busy.current=false;setError('Frame skipped: '+data.message);}
    if(data.type==='result'){
     busy.current=false;latency=latency?latency*.8+data.ms*.2:data.ms;frames++;
     const v=videoRef.current;if(v)callback.current(data.landmarks,data.timestamp/1000,v.videoWidth/v.videoHeight,data.world);
    }
   };
   worker.onerror=()=>{setError('Pose worker failed. Check model assets, then reconnect the camera.');stop();setStatus('error');};
   worker.postMessage({type:'init'});
   const loop=async(now:number)=>{
    if(!active.current||gen!==generation.current)return;
    const v=videoRef.current;
    const target=Math.max(5,Math.min(settingsRef.current.fps,1000/(latency*1.25||1)));
    if(v&&ready.current&&v.readyState>=2&&now-last>=1000/target&&v.currentTime!==lastVideoTime){
     last=now;
     if(busy.current)dropped++;
     else{
      busy.current=true;lastVideoTime=v.currentTime;
      try{
       const processingWidth=latency>110?480:settingsRef.current.performance==='quality'?960:640;
       const bitmap=await createImageBitmap(v,{resizeWidth:processingWidth,resizeHeight:Math.round(processingWidth*v.videoHeight/v.videoWidth)});
       if(!active.current||gen!==generation.current){bitmap.close();return;}
       worker.postMessage({type:'frame',bitmap,timestamp:performance.now()},[bitmap]);
      }catch(e){busy.current=false;setError('Frame capture failed. Reconnect camera.');}
     }
    }
    if(now-statsAt>1000){const cfg=stream.getVideoTracks()[0].getSettings();setDiagnostics({inferenceFPS:Math.round(frames*1000/(now-statsAt)),latency:Math.round(latency),cameraFPS:Math.round(cfg.frameRate||0),resolution:`${cfg.width} × ${cfg.height}`,dropped,effectiveFPS:Math.round(target)});frames=0;statsAt=now;}
    requestAnimationFrame(loop);
   };requestAnimationFrame(loop);
  }catch(e){if(gen!==generation.current)return;setError(e instanceof Error?e.message:'Camera could not start.');stop();setStatus('error');}
 },[stop,listDevices]);
 return {videoRef,status,error,devices,diagnostics,start,stop,listDevices};
}
