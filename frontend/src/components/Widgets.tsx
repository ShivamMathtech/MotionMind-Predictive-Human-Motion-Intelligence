import type {ReactNode} from 'react';
import {Activity} from 'lucide-react';
export function Panel({title,icon,children,className='',action}:{title:string;icon?:ReactNode;children:ReactNode;className?:string;action?:ReactNode}){return <section className={'panel '+className}><header className="panel-title"><span>{icon||<Activity size={16}/>} {title}</span>{action}</header>{children}</section>;}
export function Ring({value,label,size=92}:{value:number|null;label:string;size?:number}){return <div className="ring" style={{width:size,height:size,background:`conic-gradient(var(--mint) ${Math.max(0,Math.min(100,value||0))*3.6}deg, #193047 0)`}}><div><strong>{value===null?'—':Math.round(value)}</strong><small>{label}</small></div></div>;}
export function Metric({label,value,note}:{label:string;value:ReactNode;note?:string}){return <div className="metric"><small>{label}</small><strong>{value}</strong>{note&&<span>{note}</span>}</div>;}
export function Empty({text}:{text:string}){return <div className="empty"><Activity size={32}/><h3>No workout data yet</h3><p>{text}</p></div>;}
