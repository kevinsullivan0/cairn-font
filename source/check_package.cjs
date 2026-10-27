// Offline DOM checks. Does not claim browser layout verification.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const {parseHTML}=require('linkedom');
const root=path.resolve(process.argv[2]||path.join(__dirname,'..'));
async function exercise(file,mode){
  const text=fs.readFileSync(file,'utf8'),{window}=parseHTML(text),{document}=window;
  let requested=[];
  if(mode!=='unavailable')document.fonts={load:async s=>{requested.push(s);if(mode==='failure')throw Error('font fetch failed');return [{}];}};
  const script=document.querySelector('script');
  new vm.Script(script.textContent).runInContext(vm.createContext({document,console}));
  await new Promise(r=>setImmediate(r));
  const $=id=>document.getElementById(id);
  assert.equal(document.querySelectorAll('.card').length,4);
  assert.equal(document.querySelectorAll('.essay p').length,5);
  assert.match($('coverage').textContent,/Every character/);
  $('sample-input').value='<img src=x onerror=alert(1)> Ω é';
  $('sample-input').dispatchEvent(new window.Event('input'));
  for(const s of document.querySelectorAll('.sample')){assert.equal(s.textContent,$('sample-input').value);assert.equal(s.children.length,0);}
  assert.match($('coverage').textContent,/Ω é/);
  $('sample-input').value='“Cairn”—‘stone’… © ¥ @ [a] •';$('sample-input').dispatchEvent(new window.Event('input'));
  assert.match($('coverage').textContent,/Every character/);
  for(const size of ['12','14','16','18','28']){
    $('size').value=size;$('size').dispatchEvent(new window.Event('input'));
    assert.equal(document.documentElement.style.getPropertyValue('--size'),size+'px');
    assert.equal($('size-label').textContent,size+' px');
  }
  $('theme').click();assert(document.body.classList.contains('dark'));assert.equal($('theme').getAttribute('aria-pressed'),'true');
  $('theme').click();assert(!document.body.classList.contains('dark'));
  // linkedom lacks the browser's writable select.value behavior.
  Object.defineProperty($('leading'),'value',{value:'1.8',writable:true});
  $('leading').dispatchEvent(new window.Event('change'));assert.equal(document.documentElement.style.getPropertyValue('--leading'),'1.8');
  if(mode==='success'){assert.equal(requested.length,4);assert.match($('font-status').textContent,/All four/);}
  if(mode==='failure')assert.match($('font-status').textContent,/could not load/);
  if(mode==='unavailable')assert.match($('font-status').textContent,/unavailable/);
}
(async()=>{
  await exercise(path.join(root,'specimen.html'),'success');
  await exercise(path.join(root,'specimen.html'),'failure');
  await exercise(path.join(root,'web/example.html'),'unavailable');
  let links=0;
  for(const name of ['specimen.html','README.html','web/example.html']){
    const file=path.join(root,name),{document}=parseHTML(fs.readFileSync(file,'utf8'));
    for(const node of document.querySelectorAll('[href],[src]')){
      const ref=node.getAttribute('href')||node.getAttribute('src');
      if(ref.startsWith('#')){assert(document.getElementById(ref.slice(1)));continue;}
      assert(!/^(https?:|file:|\/)/.test(ref),'Unexpected external link');
      assert(fs.existsSync(path.resolve(path.dirname(file),ref)),ref);links++;
    }
  }
  const css=fs.readFileSync(path.join(root,'web/cairn.css'),'utf8');
  const embedded=fs.readFileSync(path.join(root,'web/cairn-embedded.css'),'utf8');
  assert.equal((css.match(/@font-face/g)||[]).length,4);
  const bytes=[...embedded.matchAll(/base64,([A-Za-z0-9+/=]+)/g)];assert.equal(bytes.length,4);
  for(const [i,style]of['Regular','Italic','Bold','BoldItalic'].entries()){
    assert(Buffer.from(bytes[i][1],'base64').equals(fs.readFileSync(path.join(root,`web/fonts/Cairn-${style}.woff`))));
  }
  for(const m of css.matchAll(/url\("([^\"]+)"\)/g))assert(fs.existsSync(path.join(root,'web',m[1])));
  assert(css.includes('font-synthesis: none'));assert(css.includes('tabular-nums'));
  const report={status:'passed',styles:4,embedded_font_matches:4,package_links:links,controls:['text size','leading','theme','safe sample editing','coverage notice'],font_load_statuses:['success','failure','unavailable'],scope:'Offline DOM and package checks; no browser screenshot or visual layout claim'};
  fs.writeFileSync(path.join(root,'web-validation.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exit(1)});
