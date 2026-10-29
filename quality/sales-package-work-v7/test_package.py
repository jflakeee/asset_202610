from pathlib import Path
import json,tempfile,shutil,sys,zipfile,warnings,stat,subprocess
from package import build,staging_errors,archive_errors,safe,sha,R,plan
root=Path(sys.argv[1]).resolve();colliders=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else None;results=[];archives=[]
for subset in ['full','trial']:
    with tempfile.TemporaryDirectory(prefix='tw-package-') as tmp:
        base=Path(tmp);stage=base/subset;payload,files,archive=build(root,stage,subset,colliders)
        assert not staging_errors(stage,files) and not archive_errors(archive,files)
        other_payload,other_files,other_archive=build(root,base/(subset+'repeat'),subset,colliders)
        assert archive.read_bytes()==other_archive.read_bytes();results.append(subset+': reproducible archive bytes')
        for name in files:
            assert safe(name)
            assert not name.endswith(('.py','.pyc','.blend1')) and 'recipes/' not in name and '__pycache__' not in name
            if name.endswith(('.json','.md','.txt','.csv')):
                data=files[name].decode('utf-8-sig');assert '/workspace/' not in data and '/Users/' not in data and 'C:\\' not in data
        # Every assembly reference resolves within the current package, not an internal source folder.
        for name,data in files.items():
            if name.startswith('examples/scenes/'):
                for instance in json.loads(data)['instances']:assert instance['file'] in files
        assert len(payload['asset_ids'])==(84 if subset=='full' else 8)
        assert len(payload['exports'])==(252 if subset=='full' else 8)
        if subset=='trial':assert not any(n.startswith(('source/','examples/')) or '/dry/' in n or '/dusk/' in n for n in files)
        if colliders:
            assert payload['collider_overrides_applied']==(24 if subset=='full' else 4)
            for m in payload['models']:
                if m['asset_id'].startswith('TW_TREE_'):assert all(p['type']=='capsule' for p in m['collider']['parts'])
            results.append(subset+': hash-bound collider overrides applied to exact allowed models')
        results.append(subset+': exact IDs/themes, no generators/cache/absolute paths, all scene references resolve')
        extra=stage/'research.bin';extra.write_bytes(b'TEST');assert 'K001' in staging_errors(stage,files);extra.unlink();results.append(subset+': unlisted file blocked')
        model=stage/next(n for n in files if n.endswith('.glb'));original=model.read_bytes()
        model.write_bytes(original+b'CHANGED');assert 'K002' in staging_errors(stage,files);model.unlink();assert 'K002' in staging_errors(stage,files);model.write_bytes(original);results.append(subset+': mutated and missing model blocked')
        model.unlink();model.symlink_to(stage/'README.md');assert 'K001' in staging_errors(stage,files);model.unlink();model.write_bytes(original);results.append(subset+': symlink model blocked')
        manifest=stage/'release_manifest.json';original_manifest=manifest.read_bytes();m=json.loads(original_manifest)
        m['asset_ids'].append('PAID_ONLY_CONTAMINATION');manifest.write_text(json.dumps(m));assert 'K002' in staging_errors(stage,files)
        manifest.write_text('{bad');assert 'K002' in staging_errors(stage,files);manifest.write_bytes(original_manifest);results.append(subset+': altered IDs and malformed manifest blocked')
        model.write_bytes(original+b'CHANGED');m=json.loads(original_manifest);rel=model.relative_to(stage).as_posix();m['files'][rel]={'bytes':model.stat().st_size,'sha256':sha(model.read_bytes())};manifest.write_text(json.dumps(m));assert 'K002' in staging_errors(stage,files);model.write_bytes(original);manifest.write_bytes(original_manifest);results.append(subset+': self-consistent tampered manifest rejected against trusted plan')
        if subset=='trial':
            extra=stage/'models/glb/lod0/moss/TW_TREE_ROUND_SMALL_B_LOD0.glb';extra.write_bytes((root/'creation/theme_output/MOSS_01/models/TW_TREE_ROUND_SMALL_B_LOD0.glb').read_bytes());assert 'K001' in staging_errors(stage,files);extra.unlink();results.append('trial: actual paid-only model contamination rejected')
        bad=dict(files);bad['../escape.bin']=b'TEST';assert 'K001' in staging_errors(stage,bad);assert not safe('/tmp/abs') and not safe('models\\bad') and not safe('models//bad') and not safe('C:/bad');results.append(subset+': traversal/noncanonical paths rejected')
        for name,data in [('extra.bin',b'TEST'),('../escape.bin',b'TEST'),('manifest.csv',b'MUTATED')]:
            changed=base/'changed.zip';shutil.copy2(archive,changed)
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                with zipfile.ZipFile(changed,'a') as z:z.writestr(name,data)
            assert archive_errors(changed,files);results.append(subset+': archive '+name+' rejected')
        changed=base/'symlink.zip';shutil.copy2(archive,changed)
        with zipfile.ZipFile(changed,'a') as z:
            info=zipfile.ZipInfo('link');info.external_attr=(stat.S_IFLNK|0o777)<<16;z.writestr(info,'README.md')
        assert 'K001' in archive_errors(changed,files);results.append(subset+': archive symlink blocked')
        contaminated=base/'contaminated';contaminated.mkdir();(contaminated/'foreign.bin').write_bytes(b'TEST')
        try:build(root,contaminated,subset,colliders)
        except ValueError:pass
        else:raise AssertionError('Existing staging accepted')
        results.append(subset+': existing staging rejected without deleting contents')
        output=R/f'{subset}_customer_layout_review_20261029.zip';shutil.copy2(archive,output)
        archives.append(dict(subset=subset,file=output.name,bytes=output.stat().st_size,sha256=sha(output.read_bytes()),unique_models=len(payload['asset_ids']),glb_files=len(payload['exports']),files=len(files)+1,sales_approved=False))
with tempfile.TemporaryDirectory(prefix='tw-invalid-ids-') as tmp:
    fake=Path(tmp);(fake/'creation/asset_records_output').mkdir(parents=True)
    shutil.copy2(root/'original_asset_pack_design_v1.md',fake/'original_asset_pack_design_v1.md')
    records=json.loads((root/'creation/asset_records_output/asset_records.json').read_text())
    for replacement in ['TW_NOT_IN_DESIGN_A',records['records'][1]['asset_id']]:
        changed=json.loads(json.dumps(records));changed['records'][0]['asset_id']=replacement
        (fake/'creation/asset_records_output/asset_records.json').write_text(json.dumps(changed))
        try:plan(fake,'full')
        except AssertionError:pass
        else:raise AssertionError('Noncanonical/duplicate source ID accepted')
    results.append('Original design42 families/84 exact IDs enforced; noncanonical/duplicate records rejected')
command=[sys.executable,str(R/'package.py'),str(root),'--out',str(R/'should_not_exist'),'--channel','sales']
p=subprocess.run(command,text=True,capture_output=True);assert p.returncode==2 and not (R/'should_not_exist').exists();results.append('Sales mode exits2 before creating output')
(R/'reports/package_validation.json').write_text(json.dumps(dict(passed=True,checks=results,archives=archives,sales_mode_blocked=True,sales_approved=False,full_design_complete=False),indent=2))
print(json.dumps(dict(passed=True,checks=len(results),archives=archives),indent=2))
