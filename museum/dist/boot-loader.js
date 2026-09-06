// This small independent script remains useful even if the main bundle stalls.
(()=>{
 const status=document.getElementById('loading-message');
 const zh=new URLSearchParams(location.search).get('lang')==='zh'||navigator.language.startsWith('zh');
 const slow=setTimeout(()=>{if(!document.body.dataset.museumReady)status.textContent=zh?'网络较慢，正在连接展馆。你可以先打开图文展览。':'The connection is slow. You can open the reading gallery while the museum connects.';},12000);
 window.addEventListener('museum-ready',()=>clearTimeout(slow),{once:true});
 const script=document.createElement('script');script.src='./museum.bundle.js?v=1.22.0.d6588457e76b';script.async=true;
 script.onerror=()=>{clearTimeout(slow);status.textContent=zh?'画面程序暂时未能下载。请重试，或打开图文展览。':'The viewer could not download. Retry or open the reading gallery.';};
 document.getElementById('retry-loading').onclick=()=>location.reload();
 document.head.append(script);
})();
