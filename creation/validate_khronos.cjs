// npm install gltf-validator@2.0.0-dev.3.10
const fs = require('fs');
const path = require('path');
const validator = require('gltf-validator');
(async () => {
  const root = path.resolve(process.argv[2] || 'output');
  const results = [];
  for (const filename of fs.readdirSync(path.join(root, 'models')).filter(x => x.endsWith('.glb')).sort()) {
    const report = await validator.validateBytes(new Uint8Array(fs.readFileSync(path.join(root,'models',filename))), {uri: filename});
    fs.writeFileSync(path.join(root, filename+'.khronos.json'), JSON.stringify(report,null,2));
    results.push({file: filename, errors: report.issues.numErrors, warnings: report.issues.numWarnings, infos: report.issues.numInfos});
  }
  fs.writeFileSync(path.join(root,'khronos_summary.json'), JSON.stringify({validator:validator.version(),results},null,2));
  console.log(JSON.stringify(results,null,2));
  if (results.some(r => r.errors)) process.exitCode = 1;
})().catch(error => { console.error(error); process.exitCode=1; });
