import policy from '#config/repository/licenses/javascript.json' with { type: 'json' };

import {
  readJsonFile,
  requireArray,
  requireDictionary,
  requireKeys,
  requireString,
} from '#shared/json.js';

function licenseNames(value, context) {
  const names = requireArray(value, context);
  const unique = new Set();
  for (const name of names) {
    requireString(name, context);
    if (unique.has(name)) throw new Error(`${context}: duplicate license ${name}.`);
    unique.add(name);
  }
  if (unique.size === 0) throw new Error(`${context}: at least one license is required.`);
  return unique;
}

function packageExemptions(value) {
  const exemptions = new Map();
  for (const entry of requireArray(value, 'package_exemptions')) {
    const exemption = requireDictionary(entry, 'license exemption');
    requireKeys(exemption, ['package', 'licenses', 'reason'], [], 'license exemption');
    const name = requireString(exemption.package, 'exemption package');
    if (name !== name.trim().toLowerCase() || exemptions.has(name)) {
      throw new Error(`License exemptions require unique lowercase package names: ${name}.`);
    }
    requireString(exemption.reason.trim(), `${name}: reason`);
    exemptions.set(name, licenseNames(exemption.licenses, `${name}: licenses`));
  }
  return exemptions;
}

function main() {
  const args = process.argv.slice(2);
  if (args.length !== 1) throw new Error('Usage: bun javascript.js <license-report.json>');
  requireKeys(policy, ['allowed_licenses', 'package_exemptions'], [], 'license policy');
  const allowed = licenseNames(policy.allowed_licenses, 'allowed_licenses');
  const exemptions = packageExemptions(policy.package_exemptions);
  const report = requireDictionary(readJsonFile(args[0], 'license report'), 'license report');
  if (Object.keys(report).length === 0) throw new Error('The license report contains no packages.');
  let violations = 0;
  for (const [specifier, metadata] of Object.entries(report)) {
    const separator = specifier.lastIndexOf('@');
    if (separator < 1) throw new Error(`The license report has an invalid package: ${specifier}.`);
    const name = specifier.slice(0, separator);
    const record = requireDictionary(metadata, specifier);
    const license = requireString(record.licenses, `${specifier}: licenses`);
    const approved = exemptions.get(name) ?? allowed;
    if (!approved.has(license)) {
      console.error(`${specifier}: expected ${[...approved].join(', ')}; observed ${license}.`);
      violations += 1;
    }
  }
  process.exitCode = violations > 0 ? 1 : 0;
}

main();
