const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const validator=require(process.argv[2]);const root=process.argv[3];
(async()=>{
 const totals=[];
 for(const theme of ['MOSS_01','DRY_01','DUSK_01']){
  const dir=path.join(root,'theme_output',theme);const results=[];
  for(const file of fs.readdirSync(path.join(dir,'models')).filter(f=>f.endsWith('.glb')).sort()){
   const bytes=fs.readFileSync(path.join(dir,'models',file));const report=await validator.validateBytes(new Uint8Array(bytes),{uri:file,format:'glb',writeTimestamp:false,maxIssues:0});
   results.push({file,errors:report.issues.numErrors,warnings:report.issues.numWarnings,infos:report.issues.numInfos,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
  }
  fs.writeFileSync(path.join(dir,'khronos_summary.json'),JSON.stringify({validator:validator.version(),results},null,2));totals.push({theme,files:results.length,errors:results.reduce((s,r)=>s+r.errors,0),warnings:results.reduce((s,r)=>s+r.warnings,0)});
 }
 console.log(JSON.stringify(totals));fs.writeFileSync(path.join(__dirname,'reports','catalog_validation.json'),JSON.stringify({validator:validator.version(),themes:totals,scope:'Fresh validation of regenerated GLBs with SHA-256 in per-theme results'},null,2));
 if(totals.some(t=>t.errors||t.warnings))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
