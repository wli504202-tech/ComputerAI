// Regression test: JSON belonging to another local-control product must never
// become a Computer.AI command. Run: node tests/test-command-detector.js
const fs=require('fs'),vm=require('vm');
const context={window:{ComputerAI:{}},MutationObserver:class{},clearTimeout(){},setTimeout(){},confirm(){return false}};
vm.createContext(context);vm.runInContext(fs.readFileSync('extension/content/command-detector.js','utf8'),context);
const parse=context.window.ComputerAI.parseCommandBlock;
const cases=[
  ['rejects reported local command', '{"id":"x","computer":"local","params":{}}', null],
  ['requires an id', '{"computer":"create_directory","params":{"path":"123"}}', null],
  ['rejects ordinary JSON', '{"name":"test"}', null],
  ['accepts documented command', '{"id":"cmd-1","computer":"create_directory","params":{"path":"123"}}', 'create_directory'],
];
let failed=0;for(const [name,input,expected] of cases){const actual=parse(input)?.computer||null;const ok=actual===expected;console.log(`${ok?'PASS':'FAIL'} ${name}`);if(!ok)failed++;}process.exitCode=failed?1:0;
