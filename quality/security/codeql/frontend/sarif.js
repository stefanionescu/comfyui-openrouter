#!/usr/bin/env node

import { readJsonFile, requireArray, requireDictionary, requireString } from '#shared/json.js';

const sarifPath = process.argv[2];
if (!sarifPath || process.argv.length !== 3) {
  console.error('Usage: bun sarif.js <sarif-path>');
  process.exit(2);
}

const sarif = requireDictionary(readJsonFile(sarifPath, 'SARIF'), 'SARIF');
const runs = requireArray(sarif.runs, 'runs');
if (runs.length === 0) throw new Error('CodeQL returned no analysis runs.');
let findingCount = 0;

for (const run of runs) {
  const currentRun = requireDictionary(run, 'run');
  const invocations = requireArray(currentRun.invocations ?? [], 'invocations');
  for (const invocation of invocations) {
    if (requireDictionary(invocation, 'invocation').executionSuccessful === false) {
      throw new Error('CodeQL did not complete its analysis.');
    }
  }
  for (const result of requireArray(currentRun.results, 'results')) {
    const finding = requireDictionary(result, 'result');
    requireString(finding.ruleId, 'ruleId');
    findingCount += 1;
  }
}

if (findingCount > 0) {
  console.error(`CodeQL found ${findingCount} findings. Review the private SARIF report.`);
  process.exitCode = 1;
} else {
  console.log('CodeQL reported no findings.');
}
