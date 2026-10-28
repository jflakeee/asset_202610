const fs=require('node:fs');
const path=require('node:path');
const validator=require(process.argv[2]||'gltf-validator');
(async()=>{
 const models=JSON.parse(fs.readFileSync(path.join(__dirname,'manifest.json')));
 const summary=[];
 fs.mkdirSync(path.join(__dirname,'validation'),{recursive:true});
 for(const {id} of models){
  const bytes=fs.readFileSync(path.join(__dirname,'models',id+'.glb'));
  const report=await validator.validateBytes(new Uint8Array(bytes),{uri:id+'.glb',format:'glb',writeTimestamp:false,maxIssues:0});
  fs.writeFileSync(path.join(__dirname,'validation',id+'.json'),JSON.stringify(report,null,2));
  summary.push({id,errors:report.issues.numErrors,warnings:report.issues.numWarnings,infos:report.issues.numInfos,hints:report.issues.numHints});
 }
 fs.writeFileSync(path.join(__dirname,'validation','summary.json'),JSON.stringify({validator:validator.version(),models:summary},null,2));
 console.log(summary);
 if(summary.some(r=>r.errors||r.warnings))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
