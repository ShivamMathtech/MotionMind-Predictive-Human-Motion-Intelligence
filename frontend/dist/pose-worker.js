/* Classic worker keeps MediaPipe WASM and all synchronous detection off the UI thread. */
self.exports={};
let pose=null;
self.onmessage=async ({data})=>{
 if(data.type==='init'){
  try{
   importScripts('/vendor/vision_bundle.js');
   const {FilesetResolver,PoseLandmarker}=self.exports;
   const files=await FilesetResolver.forVisionTasks('/wasm');
   pose=await PoseLandmarker.createFromOptions(files,{baseOptions:{modelAssetPath:'/models/pose_landmarker_lite.task',delegate:'CPU'},
      runningMode:'VIDEO',numPoses:1,minPoseDetectionConfidence:.5,minPosePresenceConfidence:.5,minTrackingConfidence:.5,
      outputSegmentationMasks:false,canvas:new OffscreenCanvas(2,2)});
   const warmup=new OffscreenCanvas(256,256);
   warmup.getContext('2d').fillRect(0,0,256,256);
   pose.detectForVideo(warmup,0);
   self.postMessage({type:'ready'});
  }catch(e){self.postMessage({type:'error',message:'Pose model could not load: '+e.message+'. Run the asset setup and use Chrome or Edge.'});}
 }else if(data.type==='frame'){
  try{
   const start=performance.now();const result=pose.detectForVideo(data.bitmap,data.timestamp);
   self.postMessage({type:'result',timestamp:data.timestamp,ms:performance.now()-start,landmarks:result.landmarks[0]||[],world:result.worldLandmarks[0]||[]});
  }catch(e){self.postMessage({type:'frame-error',message:e.message});}
  finally{data.bitmap.close();}
 }
};
