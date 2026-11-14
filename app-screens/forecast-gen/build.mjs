import * as esbuild from 'esbuild';
const stub = { name:'stub', setup(b){ b.onResolve({filter:/i18n\/strings$/}, a=>({path:'stub', namespace:'stub'})); b.onLoad({filter:/.*/, namespace:'stub'}, ()=>({contents:"export const t=(k,l)=>((globalThis.DICT||{})[k]||{})[l]||'';", loader:'js'})); } };
await esbuild.build({ entryPoints:['entry2.ts'], bundle:true, format:'iife', platform:'neutral', outfile:'logic.js', plugins:[stub], minify:false });
