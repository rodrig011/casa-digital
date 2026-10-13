const B=require('./engine');
let st=null;
const run=(...xs)=>{for(const x of xs){const r=B.handle(st,x);st=r.state;console.log('>>',x);r.messages.forEach(m=>console.log(B.toText(m)||'[foto]'));console.log('---');}};
run('hola','1','llamador','222-2650','10','Finalizar pedido','Envío a mi ciudad','La Ceiba, barrio El Centro','Menú','2','Portón','3 x 2.2','2','Tegucigalpa','Sin foto','menu','3','120-1048 x 20\n130-1024 x 50\n110-702 x 2\nXYZ x 1','Finalizar pedido','1','5','SW-1046','6','7','2');
