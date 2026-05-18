async function j(u,o){let r=await fetch(u,o);return r.json()}
async function refresh(){document.getElementById('status').textContent=JSON.stringify(await j('/api/status'),null,2);document.getElementById('logs').textContent=(await j('/api/logs?tail=200')).log}
async function runNow(){await j('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pc:+pc.value,mobile:+mobile.value,force:force.checked})});refresh()}
async function stopNow(){await j('/api/stop',{method:'POST'});refresh()}
setInterval(refresh,3000);refresh();
