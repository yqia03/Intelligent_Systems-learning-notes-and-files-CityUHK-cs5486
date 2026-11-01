import { spawnSync } from 'node:child_process';
for(const script of ['scripts/browser-check.mjs','scripts/browser-midterm.mjs','scripts/browser-assignments.mjs','scripts/browser-textbook.mjs']) {
 const result=spawnSync(process.execPath,[script,...process.argv.slice(2)],{stdio:'inherit'});
 if(result.status!==0)process.exit(result.status||1);
}
