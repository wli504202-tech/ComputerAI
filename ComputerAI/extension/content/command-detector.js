window.ComputerAI.COMMANDS=new Set(['ping','get_status','get_workspace','list_files','read_file','write_file','append_file','create_directory','copy_file','move_file','delete_file','exists','run_python','run_node','run_command']);
window.ComputerAI.parseCommandBlock=(text)=>{
  if(typeof text!=='string') return null;
  const trimmed=text.trim();
  if(!trimmed.startsWith('{')||!trimmed.includes('"computer"')) return null;
  let command; try{command=JSON.parse(trimmed);}catch{return null;}
  // A valid Computer.AI command is deliberately narrow. Never infer an id or
  // execute another product's JSON merely because it happens to use "computer".
  if(!command||typeof command.id!=='string'||!command.id.trim()||typeof command.computer!=='string'||!window.ComputerAI.COMMANDS.has(command.computer)||!command.params||typeof command.params!=='object'||Array.isArray(command.params)) return null;
  return command;
};
window.ComputerAI.CommandDetector=class {
  constructor(adapter,onResult){this.adapter=adapter;this.onResult=onResult;this.done=new Set();this.busy=false;this.started=false;}
  start(){if(this.started)return;this.started=true;this.observer=new MutationObserver(()=>this.schedule());this.observer.observe(document.body,{subtree:true,childList:true,characterData:true});this.schedule();}
  stop(){this.started=false;this.observer?.disconnect();clearTimeout(this.timer);}
  schedule(){clearTimeout(this.timer);this.timer=setTimeout(()=>this.scan(),400);}
  async scan(){if(!this.started||this.busy)return; const blocks=[...document.querySelectorAll('pre code,pre')];for(const block of blocks){const command=window.ComputerAI.parseCommandBlock(block.textContent);if(!command||this.done.has(command.id))continue;this.done.add(command.id);this.busy=true;try{const response=await window.ComputerAI.api('/command','POST',command);if(response.data?.error?.code==='ERROR_005'&&/Confirmation required/.test(response.data.error.message)){const allowed=confirm(`Computer.AI wants to perform ${command.computer}.\n\nAllow this local operation?`);if(allowed) response.data= (await window.ComputerAI.api('/command','POST',{...command,params:{...command.params,confirmed:true}})).data;}this.onResult(response.data);}catch(error){this.onResult({id:command.id,success:false,error:{code:'ERROR_002',message:error.message}});}finally{this.busy=false;}}}
};
