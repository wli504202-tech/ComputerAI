class SiteAdapter {
  constructor(name,hosts,enabled=false){this.name=name;this.hosts=hosts;this.enabled=enabled;}
  matches(location){return this.hosts.includes(location.hostname);}
  findChatInput(){return [...document.querySelectorAll('textarea,[contenteditable="true"],[role="textbox"]')].find(e=>e.offsetParent!==null&&!e.closest('[data-computer-ai]'))||null;}
  findMessages(){return [...document.querySelectorAll('main article,main [data-message-author-role],main [role="article"],main')];}
  sendMessage(text){const input=this.findChatInput();if(!input) throw new Error('ERROR_010: Chat input not detected'); input.focus(); if(input.tagName==='TEXTAREA') input.value=text;else {input.textContent=text;input.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:text}));} input.dispatchEvent(new Event('input',{bubbles:true})); const form=input.closest('form'); const button=(form&&form.querySelector('button[type="submit"]'))||[...document.querySelectorAll('button')].find(b=>/send|submit/i.test(b.getAttribute('aria-label')||b.textContent||'')); if(button&&!button.disabled) button.click();else input.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',code:'Enter',bubbles:true}));}
}
window.ComputerAI={SiteAdapter,adapters:[]};
