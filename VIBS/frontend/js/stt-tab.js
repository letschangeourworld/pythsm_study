'use strict';
(function(global){
  let activeTab='chat', sttLines=[], transLines=[];
  const MAX_LINES=300;

  function init(){renderTabBar();renderPanels();injectStyles();
    console.log('[STT-Tab] v2.0 초기화');}

  function renderTabBar(){
    const header=document.querySelector('.chat-header');
    if(!header)return;
    const chatLabel=(typeof T!=='undefined'&&T.chatTabLabel)||'Chat';
    const sttLabel=(typeof T!=='undefined'&&T.sttTabLabel)||'Live Text';
    const transLabel=(typeof T!=='undefined'&&T.transTabLabel)||'Live Translation';
    header.innerHTML=`<div class="stt-tab-group">
      <button class="stt-tab-btn active" id="tabBtnChat" onclick="STTTab.switchTab('chat')">💬 <span>${chatLabel}</span></button>
      <button class="stt-tab-btn" id="tabBtnStt" onclick="STTTab.switchTab('stt')">📝 <span>${sttLabel}</span><span class="tab-new-badge hidden" id="sttBadge">NEW</span></button>
      <button class="stt-tab-btn" id="tabBtnTrans" onclick="STTTab.switchTab('translation')">🌐 <span>${transLabel}</span><span class="tab-new-badge hidden" id="transBadge">NEW</span></button>
    </div>`;}

  function renderPanels(){
    const chatBody=document.querySelector('.chat-body');
    const chatLeft=document.querySelector('.chat-left');
    if(!chatBody||!chatLeft)return;
    const sttPanel=document.createElement('div');
    sttPanel.id='sttPanel';sttPanel.className='tab-panel hidden';
    sttPanel.innerHTML=`<div class="panel-empty" id="sttEmpty">📝 설교 텍스트가 여기에 실시간으로 표시됩니다.<br><span style="font-size:11px;opacity:.6">Sermon text will appear here.</span></div>`;
    const transPanel=document.createElement('div');
    transPanel.id='transPanel';transPanel.className='tab-panel hidden';
    transPanel.innerHTML=`<div class="panel-empty" id="transEmpty">🌐 실시간 번역이 여기에 표시됩니다.<br><span style="font-size:11px;opacity:.6">Live translation will appear here.</span></div>`;
    chatBody.insertBefore(sttPanel,chatLeft.nextSibling);
    chatBody.insertBefore(transPanel,sttPanel.nextSibling);}

  function switchTab(tab){
    activeTab=tab;
    const chatLeft=document.querySelector('.chat-left');
    const sttPanel=document.getElementById('sttPanel');
    const transPanel=document.getElementById('transPanel');
    chatLeft?.classList.add('hidden');sttPanel?.classList.add('hidden');transPanel?.classList.add('hidden');
    ['Chat','Stt','Trans'].forEach(n=>{document.getElementById(`tabBtn${n}`)?.classList.remove('active');});
    if(tab==='chat'){chatLeft?.classList.remove('hidden');document.getElementById('tabBtnChat')?.classList.add('active');}
    else if(tab==='stt'){sttPanel?.classList.remove('hidden');document.getElementById('tabBtnStt')?.classList.add('active');document.getElementById('sttBadge')?.classList.add('hidden');if(sttPanel)sttPanel.scrollTop=sttPanel.scrollHeight;}
    else if(tab==='translation'){transPanel?.classList.remove('hidden');document.getElementById('tabBtnTrans')?.classList.add('active');document.getElementById('transBadge')?.classList.add('hidden');if(transPanel)transPanel.scrollTop=transPanel.scrollHeight;}}

  function appendText(data){
    const text=(data.text||'').trim();if(!text)return;
    sttLines.push(data);if(sttLines.length>MAX_LINES)sttLines.shift();
    const panel=document.getElementById('sttPanel');if(!panel)return;
    document.getElementById('sttEmpty')?.remove();
    const time=_formatTime(data.spokenAt);
    const pct=Math.round((data.confidence||0.9)*100);
    const col=pct>=85?'var(--green)':pct>=65?'var(--gold)':'var(--muted)';
    const line=document.createElement('div');line.className='panel-line stt-line';
    line.innerHTML=`<span class="line-time">${esc(time)}</span><span class="line-lang">🇰🇷</span><span class="line-text">${esc(text)}</span><span class="line-conf" style="color:${col}">${pct}%</span>`;
    panel.appendChild(line);_trimPanel(panel,MAX_LINES);
    if(activeTab!=='stt')document.getElementById('sttBadge')?.classList.remove('hidden');
    else panel.scrollTop=panel.scrollHeight;}

  function appendTranslation(data){
    const text=(data.translatedText||'').trim();if(!text)return;
    transLines.push(data);if(transLines.length>MAX_LINES)transLines.shift();
    const panel=document.getElementById('transPanel');if(!panel)return;
    document.getElementById('transEmpty')?.remove();
    const time=_formatTime(data.spokenAt);const flag=_langFlag(data.targetLanguage);
    const line=document.createElement('div');line.className='panel-line trans-line';
    line.innerHTML=`<span class="line-time">${esc(time)}</span><span class="line-lang">${flag}</span><span class="line-text">${esc(text)}</span>`;
    panel.appendChild(line);_trimPanel(panel,MAX_LINES);
    if(activeTab!=='translation')document.getElementById('transBadge')?.classList.remove('hidden');
    else panel.scrollTop=panel.scrollHeight;}

  function loadHistory(transcripts){
    if(!transcripts?.length)return;
    const panel=document.getElementById('sttPanel');if(!panel)return;
    document.getElementById('sttEmpty')?.remove();
    transcripts.forEach(t=>{
      const time=_formatTime(t.spoken_at||t.spokenAt);
      const pct=Math.round((t.confidence||0.9)*100);
      const col=pct>=85?'var(--green)':pct>=65?'var(--gold)':'var(--muted)';
      const line=document.createElement('div');line.className='panel-line stt-line history';
      line.innerHTML=`<span class="line-time">${esc(time)}</span><span class="line-lang">🇰🇷</span><span class="line-text">${esc(t.original_text||t.text)}</span><span class="line-conf" style="color:${col}">${pct}%</span>`;
      panel.appendChild(line);});_trimPanel(panel,MAX_LINES);}

  function loadTranslationHistory(translations){
    if(!translations?.length)return;
    const panel=document.getElementById('transPanel');if(!panel)return;
    document.getElementById('transEmpty')?.remove();
    translations.forEach(t=>{
      const time=_formatTime(t.spoken_at||t.spokenAt);const flag=_langFlag(t.target_language||t.targetLanguage);
      const line=document.createElement('div');line.className='panel-line trans-line history';
      line.innerHTML=`<span class="line-time">${esc(time)}</span><span class="line-lang">${flag}</span><span class="line-text">${esc(t.translated_text||t.translatedText)}</span>`;
      panel.appendChild(line);});_trimPanel(panel,MAX_LINES);}

  function _formatTime(iso){if(!iso)return '';return new Date(iso).toLocaleTimeString(document.documentElement.lang||'ko',{hour:'2-digit',minute:'2-digit',second:'2-digit'});}
  function _langFlag(lang){const m={en:'🇺🇸',ja:'🇯🇵',zh:'🇨🇳',ko:'🇰🇷','en-US':'🇺🇸','ja-JP':'🇯🇵','zh-CN':'🇨🇳'};return m[lang]||'🌐';}
  function _trimPanel(p,max){const ls=p.querySelectorAll('.panel-line');if(ls.length>max)for(let i=0;i<ls.length-max;i++)ls[i].remove();}
  function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');}

  function injectStyles(){
    if(document.getElementById('stt-tab-styles'))return;
    const s=document.createElement('style');s.id='stt-tab-styles';
    s.textContent=`
      .stt-tab-group{display:flex;gap:3px;align-items:center;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding:2px 0;}
      .stt-tab-group::-webkit-scrollbar{display:none;}
      .stt-tab-btn{display:flex;align-items:center;gap:4px;flex-shrink:0;padding:5px 12px;border:none;border-radius:18px;font-size:11px;font-weight:600;cursor:pointer;font-family:inherit;background:transparent;color:var(--muted);transition:all .2s;white-space:nowrap;}
      .stt-tab-btn:hover{background:rgba(255,255,255,.06);color:var(--text);}
      .stt-tab-btn.active{background:rgba(201,168,76,.15);color:var(--gold);}
      .tab-new-badge{background:var(--red);color:#fff;border-radius:6px;font-size:8px;padding:1px 4px;font-weight:700;animation:tabBlink 1s infinite;}
      .tab-new-badge.hidden{display:none;}
      @keyframes tabBlink{0%,100%{opacity:1}50%{opacity:.3}}
      .tab-panel{flex:1;overflow-y:auto;padding:10px 12px;display:flex;flex-direction:column;gap:7px;scroll-behavior:smooth;min-width:0;border-right:1px solid var(--border);}
      .tab-panel.hidden{display:none!important;}
      .tab-panel::-webkit-scrollbar{width:4px;}
      .tab-panel::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:2px;}
      .panel-empty{text-align:center;padding:30px 10px;font-size:13px;color:var(--muted);line-height:1.9;}
      .panel-line{display:flex;align-items:flex-start;gap:7px;padding:8px 10px;border-radius:10px;line-height:1.6;}
      .panel-line:hover{background:rgba(255,255,255,.04);}
      .panel-line.history{opacity:.75;}
      .stt-line{background:rgba(201,168,76,.05);border-left:2px solid rgba(201,168,76,.3);}
      .trans-line{background:rgba(96,165,250,.05);border-left:2px solid rgba(96,165,250,.3);}
      .line-time{font-size:10px;color:var(--muted);flex-shrink:0;margin-top:2px;min-width:62px;}
      .line-lang{font-size:14px;flex-shrink:0;margin-top:1px;}
      .line-text{flex:1;font-size:13px;color:var(--text);word-break:break-word;}
      .line-conf{font-size:9px;flex-shrink:0;margin-top:3px;font-weight:700;min-width:28px;text-align:right;}
      .chat-left.hidden{display:none!important;}
    `;document.head.appendChild(s);}

  function clear(){sttLines=[];transLines=[];
    ['sttPanel','transPanel'].forEach(id=>{const p=document.getElementById(id);if(!p)return;
      p.innerHTML=id==='sttPanel'?'<div class="panel-empty" id="sttEmpty">📝 설교 텍스트가 여기에 실시간으로 표시됩니다.</div>':'<div class="panel-empty" id="transEmpty">🌐 실시간 번역이 여기에 표시됩니다.</div>';});}

  global.STTTab={init,switchTab,appendText,appendTranslation,loadHistory,loadTranslationHistory,clear};
})(window);
