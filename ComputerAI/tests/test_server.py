import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'server'))
from command_router import CommandRouter

class ServerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.events=[]
  self.config={'workspace':self.root,'protocol_version':1,'max_file_size':1024*1024,'max_output_size':1024*1024,'max_command_time':2,'allow_python':True,'allow_node':False,'allow_shell':False,'require_confirmation':False}
  self.router=CommandRouter(self.config,lambda *x:self.events.append(x))
 def tearDown(self): self.tmp.cleanup()
 def cmd(self,name,params,id='test'): return self.router.execute({'id':id,'computer':name,'params':params})
 def test_health_commands(self): self.assertTrue(self.cmd('ping',{},'p')['success']);self.assertEqual(str(self.root),self.cmd('get_workspace',{},'w')['workspace'])
 def test_create_write_read(self):
  self.assertTrue(self.cmd('create_directory',{'path':'123'},'1')['success']);self.assertTrue(self.cmd('write_file',{'path':'123/time.html','content':'<h1>time</h1>'},'2')['success']);self.assertEqual('<h1>time</h1>',self.cmd('read_file',{'path':'123/time.html'},'3')['content'])
 def test_traversal_rejected(self): self.assertEqual('ERROR_004',self.cmd('write_file',{'path':'../bad.txt','content':'x'},'4')['error']['code'])
 def test_invalid_command(self): self.assertEqual('ERROR_003',self.cmd('format_disk',{},'5')['error']['code'])
 def test_missing_file(self): self.assertEqual('ERROR_006',self.cmd('read_file',{'path':'none'},'6')['error']['code'])
 def test_duplicate_command(self): self.cmd('write_file',{'path':'x','content':'a'},'same');r=self.cmd('write_file',{'path':'x','content':'b'},'same');self.assertTrue(r['duplicate']);self.assertEqual('a',(self.root/'x').read_text())
 def test_timeout(self):
  (self.root/'slow.py').write_text('import time; time.sleep(2)')
  r=self.cmd('run_python',{'file':'slow.py','timeout':1},'slow')
  self.assertEqual('ERROR_007',r['error']['code'])
if __name__=='__main__': unittest.main()
