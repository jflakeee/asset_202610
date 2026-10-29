const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const validator=require(process.argv[2]);const root=__dirname;
(async()=>{
 const results=[];
 for(const file of fs.readdirSync(path.join(root,'models')).filter(f=>f.endsWith('.glb')).sort()){
  const raw=fs.readFileSync(path.join(root,'models',file));const r=await validator.validateBytes(new Uint8Array(raw),{uri:file,format:'glb',writeTimestamp:false,maxIssues:0});
  results.push({file,sha256:crypto.createHash('sha256').update(raw).digest('hex'),errors:r.issues.numErrors,warnings:r.issues.numWarnings});
 }
 fs.writeFileSync(path.join(root,'reports/validator.json'),JSON.stringify({validator:validator.version(),results},null,2));console.log('FILES',results.length,'ERRORS',results.reduce((s,r)=>s+r.errors,0),'WARNINGS',results.reduce((s,r)=>s+r.warnings,0));if(results.some(r=>r.errors||r.warnings))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
